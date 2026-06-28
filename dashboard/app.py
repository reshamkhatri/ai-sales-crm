import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
from datetime import datetime, timedelta

from core import crm, ad_analyzer, ai_brain, lead_scorer, outbound, messenger, whatsapp, instagram, email_handler, telegram, copilot, prospector
from database import db
from config import DASHBOARD_HOST, DASHBOARD_PORT, META_VERIFY_TOKEN, WHATSAPP_VERIFY_TOKEN, ACTIVE_CHANNELS, LEADFINDER_API_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    # Populate a demo dataset only if the DB is empty (e.g. a fresh deploy).
    try:
        from core import demo_seed
        demo_seed.seed_if_empty()
    except Exception as e:
        print(f"[demo_seed] skipped: {e}")
    scheduler = BackgroundScheduler()
    # Daily ad pull at 9 AM
    scheduler.add_job(ad_analyzer.get_insights, CronTrigger(hour=9, minute=0))
    # Check emails every 15 minutes
    scheduler.add_job(email_handler.check_new_emails, CronTrigger(minute="*/15"))
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()

app = FastAPI(title="AI Sales Assistant", lifespan=lifespan)

# Allow the public lead form to be embedded/submitted from any website.
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/lead-form", response_class=HTMLResponse)
def lead_form(request: Request):
    """Public lead-capture form — share the link or embed it on a website."""
    return templates.TemplateResponse(request, "lead_form.html", {})

def _apikey_ok(request: Request) -> bool:
    """Validate the Lead Finder extension's x-api-key header.
    If LEADFINDER_API_KEY is configured, require an exact match; otherwise any
    non-empty key is accepted (convenient for local use)."""
    key = (request.headers.get("x-api-key") or "").strip()
    if LEADFINDER_API_KEY:
        return key == LEADFINDER_API_KEY
    return bool(key)


def _norm_phone(p):
    return re.sub(r"[^\d+]", "", str(p or ""))


def _find_lead_duplicate(business_name, phone, place_id):
    """Return (lead_id, reason) if this maps lead already exists, else (None, None)."""
    if place_id:
        row = db.fetchone("SELECT id FROM leads WHERE place_id = ? AND place_id != ''", (place_id,))
        if row:
            return row["id"], "placeId"
    clean = _norm_phone(phone)
    if clean and len(re.sub(r"\D", "", clean)) >= 7:
        row = db.fetchone(
            "SELECT id FROM leads WHERE REPLACE(REPLACE(REPLACE(REPLACE(phone,' ',''),'-',''),'(',''),')','') = ?",
            (clean,),
        )
        if row:
            return row["id"], "phone"
    if business_name:
        row = db.fetchone("SELECT id FROM leads WHERE business_name = ? COLLATE NOCASE", (business_name.strip(),))
        if row:
            return row["id"], "hash"
    return None, None


def _ingest_extension_lead(payload: dict) -> dict:
    """Map a Lead Finder extension payload into a CRM lead. Returns the
    extension-style result the crm-client expects."""
    business_name = (payload.get("businessName") or "").strip()
    # phone is the primary; extras come in "phones"
    phone = (payload.get("phone") or "").strip()
    phones = payload.get("phones") or []
    place_id = (payload.get("placeId") or "").strip()

    if not business_name and not phone:
        return {"error": "businessName or phone required", "_status": 400}

    dup_id, reason = _find_lead_duplicate(business_name, phone, place_id)
    if dup_id:
        return {"duplicate": True, "leadId": str(dup_id), "reason": reason,
                "businessName": business_name, "message": "Already in CRM"}

    # Build notes from the rich maps fields.
    notes = "\n".join(filter(None, [
        f"Website: {payload['website']}" if payload.get("website") else "",
        f"Facebook: {payload['facebook']}" if payload.get("facebook") else "",
        f"Rating: {payload['rating']} ({payload.get('reviewCount', 0)} reviews)" if payload.get("rating") else "",
        f"Website status: {payload['websiteStatus']}" if payload.get("websiteStatus") else "",
        f"Extra phones: {', '.join(phones)}" if phones else "",
        (payload.get("notes") or "").strip(),
    ]))
    location = " · ".join(filter(None, [(payload.get("address") or "").strip(), (payload.get("city") or "").strip()]))
    source_map = {"google_maps": "google-maps", "google_places_api": "google-maps",
                  "google_search": "web-search", "yellow_pages": "yellowpages",
                  "facebook": "facebook", "manual": "manual"}
    source = source_map.get(payload.get("source", ""), "google-maps")

    lead_id = crm.create_lead(
        name=business_name or "Maps Lead",
        business_name=business_name,
        phone=phone,
        email="",
        source=source,
        notes=notes,
        location=location,
        industry=(payload.get("category") or "").strip(),
        tags="leadfinder",
        place_id=place_id,
    )
    return {"ok": True, "leadId": str(lead_id), "businessName": business_name, "aiScore": None}


@app.get("/api/user/apikey")
def api_user_apikey(request: Request):
    """Test-connection endpoint used by the Lead Finder extension settings page."""
    if not _apikey_ok(request):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    return {"ok": True, "active": True}


@app.post("/api/leads/ingest")
async def api_ingest_lead(request: Request):
    """Capture a lead. Handles BOTH the public website form (name/email/phone)
    and the Lead Finder extension (businessName/placeId/... + x-api-key)."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        payload = dict(await request.form())

    # ── Lead Finder extension payload (has businessName) ──────────────────
    if "businessName" in payload:
        if not _apikey_ok(request):
            return JSONResponse({"error": "Invalid API key"}, status_code=401)
        result = _ingest_extension_lead(payload)
        status = result.pop("_status", 200)
        return JSONResponse(result, status_code=status)

    # ── Public website form payload ───────────────────────────────────────
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    phone = (payload.get("phone") or "").strip()
    if not name and not email and not phone:
        return JSONResponse({"error": "Please provide a name, email, or phone."}, status_code=400)

    service = (payload.get("service") or "").strip()
    message = (payload.get("message") or "").strip()
    notes = "\n".join(filter(None, [
        f"Service: {service}" if service else "",
        f"Message: {message}" if message else "",
    ]))
    lead_id = crm.create_lead(
        name=name or "Website Lead",
        business_name=(payload.get("business") or "").strip(),
        phone=phone,
        email=email,
        source=(payload.get("source") or "website").strip(),
        notes=notes,
        tags="website-lead",
    )
    if message:
        try:
            crm.add_message(lead_id, "website", message, "lead")
        except Exception:
            pass
    return {"ok": True, "lead_id": lead_id, "message": "Thanks! We'll be in touch shortly."}


@app.post("/api/leads/ingest/batch")
async def api_ingest_batch(request: Request):
    """Bulk ingest from the Lead Finder extension: {"leads": [ ...payloads ]}."""
    if not _apikey_ok(request):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    body = await request.json()
    leads = body.get("leads") or []
    summary = {"total": len(leads), "created": 0, "duplicate": 0, "errors": 0}
    results = []
    for i, p in enumerate(leads):
        try:
            r = _ingest_extension_lead(p)
            if r.get("duplicate"):
                summary["duplicate"] += 1
                results.append({"index": i, "ok": True, "duplicate": True,
                                "reason": r["reason"], "leadId": r["leadId"], "businessName": r["businessName"]})
            elif r.get("ok"):
                summary["created"] += 1
                results.append({"index": i, "ok": True, "created": True,
                                "leadId": r["leadId"], "businessName": r["businessName"], "aiScore": None})
            else:
                summary["errors"] += 1
                results.append({"index": i, "ok": False, "error": r.get("error", "Unknown error")})
        except Exception as e:
            summary["errors"] += 1
            results.append({"index": i, "ok": False, "error": str(e)})
    return {"summary": summary, "results": results}

@app.get("/overview", response_class=HTMLResponse)
def dashboard(request: Request):
    leads = crm.get_recent_leads(20)
    hot_leads = crm.get_hot_leads(70)
    today_meetings = crm.get_todays_tasks()
    recommendations = db.fetchall("SELECT * FROM ai_recommendations WHERE actioned = 0 ORDER BY created_at DESC LIMIT 5")
    daily_brief = copilot.get_daily_brief()
    ad_decisions = ad_analyzer.get_ad_decision_summary()
    overdue = crm.get_overdue_tasks()
    for t in overdue:
        t["overdue"] = True
    followups = overdue + crm.get_todays_followups()
    task_summary = crm.get_task_summary()
    return templates.TemplateResponse(request, "index.html", {
        "leads": leads,
        "hot_leads": hot_leads,
        "today_meetings": today_meetings,
        "recommendations": recommendations,
        "daily_brief": daily_brief,
        "ad_decisions": ad_decisions,
        "followups": followups,
        "task_summary": task_summary
    })

@app.get("/", response_class=HTMLResponse)
@app.get("/workspace", response_class=HTMLResponse)
@app.get("/workspace/{lead_id}", response_class=HTMLResponse)
def workspace(request: Request, lead_id: int = None):
    leads = crm.get_recent_leads(50)
    if lead_id is None and leads:
        lead_id = leads[0]["id"]
    selected = crm.get_lead(lead_id) if lead_id else None
    messages = crm.get_messages(lead_id) if lead_id else []
    tasks = crm.get_tasks_for_lead(lead_id) if lead_id else []
    open_tasks = [t for t in tasks if t.get("status") == "open"]
    stats = crm.get_worklist_stats()
    return templates.TemplateResponse(request, "workspace.html", {
        "leads": leads,
        "selected": selected,
        "messages": messages,
        "tasks": tasks,
        "open_tasks": open_tasks,
        "stats": stats,
    })

def _deliver_to_channel(lead, text):
    """Try to actually deliver an outbound message via the lead's channel.
    Returns delivery status. Send functions return {'error': ...} when the
    channel's credentials aren't configured, so this safely no-ops until set up."""
    source = (lead.get("source") or "").lower()
    phone = lead.get("phone")
    email = lead.get("email")
    try:
        if source == "whatsapp" and phone:
            r = whatsapp.send_whatsapp_message(phone, text)
        elif source == "instagram" and phone:
            r = instagram.send_instagram_dm(phone, text)
        elif source == "email" or (email and not phone):
            if not email:
                return {"attempted": False, "delivered": False, "channel": None, "detail": "Lead has no email"}
            r = email_handler.send_email(email, "Message from our team", text)
        else:
            return {"attempted": False, "delivered": False, "channel": source or None,
                    "detail": "No sendable channel connected for this lead"}
        delivered = not (isinstance(r, dict) and r.get("error"))
        channel = "email" if (source == "email" or (email and not phone)) else source
        return {"attempted": True, "delivered": delivered, "channel": channel,
                "detail": (r.get("error") if isinstance(r, dict) else None) if not delivered else None}
    except Exception as e:
        return {"attempted": True, "delivered": False, "channel": source or None, "detail": str(e)}


@app.post("/api/leads/{lead_id}/message")
async def api_post_message(request: Request, lead_id: int):
    """Log a message in the lead's thread, and deliver it via the lead's channel
    when it's an outbound message and the channel is connected."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        payload = dict(await request.form())
    content = (payload.get("content") or "").strip()
    if not content:
        return JSONResponse({"error": "Message content is required"}, status_code=400)
    sender = payload.get("sender") or "user"
    lead = crm.get_lead(lead_id)
    platform = payload.get("platform") or (lead or {}).get("source") or "manual"
    msg_id = crm.add_message(lead_id, platform, content, sender)

    # Deliver genuine outbound messages (sender 'user'); internal logs are not sent.
    deliver = payload.get("deliver")
    if deliver is None:
        deliver = (sender == "user")
    delivery = {"attempted": False, "delivered": False, "channel": None, "detail": None}
    if deliver and lead:
        delivery = _deliver_to_channel(lead, content)

    return {"id": msg_id, "lead_id": lead_id, "content": content, "sender": sender,
            "platform": platform, "delivery": delivery}

@app.post("/api/leads/{lead_id}/status")
def api_update_status(lead_id: int, status: str = Form(...)):
    crm.update_lead_status(lead_id, status)
    return {"lead_id": lead_id, "status": status}

@app.get("/api/leads")
def api_leads(q: str = None, status: str = None, source: str = None, score_tier: str = None, limit: int = 50):
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if q:
        query += " AND (name LIKE ? OR business_name LIKE ? OR phone LIKE ? OR email LIKE ? OR industry LIKE ? OR tags LIKE ?)"
        q_wild = f"%{q}%"
        params.extend([q_wild, q_wild, q_wild, q_wild, q_wild, q_wild])
    if status:
        query += " AND status = ?"
        params.append(status)
    if source:
        query += " AND source = ?"
        params.append(source)
    if score_tier:
        if score_tier == "hot":
            query += " AND score >= 70"
        elif score_tier == "warm":
            query += " AND score >= 40 AND score < 70"
        elif score_tier == "cold":
            query += " AND score < 40"
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    return db.fetchall(query, tuple(params))

@app.post("/api/leads/{lead_id}/tags")
async def api_add_tag(lead_id: int, request: Request):
    payload = await request.json()
    tag = payload.get("tag", "").strip()
    if not tag:
        return JSONResponse({"error": "Tag cannot be empty"}, status_code=400)
    lead = crm.get_lead(lead_id)
    if not lead:
        return JSONResponse({"error": "Lead not found"}, status_code=404)
    
    current_tags = lead.get("tags") or ""
    tags_list = [t.strip() for t in current_tags.split(",") if t.strip()]
    if tag not in tags_list:
        tags_list.append(tag)
    new_tags = ",".join(tags_list)
    crm.update_lead(lead_id, tags=new_tags)
    return {"lead_id": lead_id, "tags": new_tags}

@app.delete("/api/leads/{lead_id}/tags")
def api_remove_tag(lead_id: int, tag: str):
    lead = crm.get_lead(lead_id)
    if not lead:
        return JSONResponse({"error": "Lead not found"}, status_code=404)
    
    current_tags = lead.get("tags") or ""
    tags_list = [t.strip() for t in current_tags.split(",") if t.strip()]
    if tag in tags_list:
        tags_list.remove(tag)
    new_tags = ",".join(tags_list)
    crm.update_lead(lead_id, tags=new_tags)
    return {"lead_id": lead_id, "tags": new_tags}

@app.post("/api/leads/bulk-status")
async def api_bulk_status(request: Request):
    payload = await request.json()
    lead_ids = payload.get("lead_ids", [])
    status = payload.get("status")
    if not lead_ids or not status:
        return JSONResponse({"error": "lead_ids and status are required"}, status_code=400)
    for lid in lead_ids:
        crm.update_lead_status(lid, status)
    return {"success": True, "updated_count": len(lead_ids)}

@app.post("/api/leads/bulk-export")
async def api_bulk_export(request: Request):
    from fastapi.responses import StreamingResponse
    import io
    import csv
    payload = await request.json()
    lead_ids = payload.get("lead_ids", [])
    if not lead_ids:
        return JSONResponse({"error": "No leads selected"}, status_code=400)
    
    placeholders = ",".join(["?"] * len(lead_ids))
    query = f"SELECT * FROM leads WHERE id IN ({placeholders}) ORDER BY created_at DESC"
    leads = db.fetchall(query, tuple(lead_ids))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Business Name", "Phone", "Email", "Source", "Status", "Score", "Location", "Industry", "Tags", "Notes", "Created At"])
    for l in leads:
        writer.writerow([
            l.get("id"),
            l.get("name"),
            l.get("business_name"),
            l.get("phone"),
            l.get("email"),
            l.get("source"),
            l.get("status"),
            l.get("score"),
            l.get("location"),
            l.get("industry"),
            l.get("tags"),
            l.get("notes"),
            l.get("created_at")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )

@app.post("/api/prospect/google-maps")
async def api_prospect_google_maps(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        payload = dict(await request.form())
    
    query = payload.get("query", "").strip()
    location = payload.get("location", "").strip()
    limit = int(payload.get("limit") or 20)
    
    if not query:
        return JSONResponse({"error": "Search query is required"}, status_code=400)
        
    results = prospector.search_google_maps(query, location, limit)
    results = prospector.enrich_prospects(results, max_sites=6, timeout=4)
    return prospector.check_duplicates(results)

@app.post("/api/prospect/web-search")
async def api_prospect_web_search(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        payload = dict(await request.form())
    
    query = payload.get("query", "").strip()
    location = payload.get("location", "").strip()
    limit = int(payload.get("limit") or 20)
    
    if not query:
        return JSONResponse({"error": "Search query is required"}, status_code=400)
        
    full_query = f"{query} {location}".strip()
    results = prospector._search_duckduckgo(full_query, limit)
    results = prospector.enrich_prospects(results, max_sites=6, timeout=4)
    prospector._log_search("web_search", query, location, results)
    return prospector.check_duplicates(results)

@app.post("/api/prospect/import")
async def api_prospect_import(request: Request):
    payload = await request.json()
    prospects = payload.get("prospects", [])
    source_tag = payload.get("source_tag", "prospected")
    
    if not prospects:
        return JSONResponse({"error": "No prospects selected for import"}, status_code=400)
        
    checked = prospector.check_duplicates(prospects)
    summary = prospector.import_prospects(checked, source_tag)
    return summary

@app.post("/api/prospect/csv-upload")
async def api_prospect_csv_upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parsed = prospector.parse_csv(content)
        parsed["rows"] = prospector.check_duplicates(parsed["rows"])
        return parsed
    except Exception as e:
        return JSONResponse({"error": f"Failed to parse CSV: {str(e)}"}, status_code=400)

@app.get("/api/prospect/history")
def api_prospect_history():
    return prospector.get_search_history()

@app.get("/api/hot-leads")
def api_hot_leads():
    return crm.get_hot_leads(70)

@app.get("/api/call-list")
def api_call_list():
    return outbound.generate_call_list()

@app.get("/api/ads")
def api_ads():
    return ad_analyzer.get_ad_decision_summary()

@app.post("/api/ads/analyze")
def api_analyze_ads():
    data = ad_analyzer.get_ad_summary()
    if not data:
        return {"error": "No ad data available"}
    analysis = ai_brain.analyze_ads(json.dumps(data))
    db.execute("INSERT INTO ai_recommendations (type, content, data_snapshot) VALUES (?, ?, ?)",
               ("ad_analysis", analysis, json.dumps(data)))
    return {"analysis": analysis}

@app.post("/api/draft/{lead_id}")
def api_draft(lead_id: int, platform: str = Form(...)):
    draft = outbound.draft_outreach_for_lead(lead_id, platform)
    return {"draft": draft}

@app.get("/api/webhook/facebook")
def facebook_webhook_verify(request: Request):
    """Verify Facebook Messenger webhook"""
    params = dict(request.query_params)
    challenge = messenger.handle_webhook_challenge(
        params.get("hub.mode"), params.get("hub.verify_token"), params.get("hub.challenge"), META_VERIFY_TOKEN
    )
    if challenge:
        return int(challenge)
    return {"error": "Verification failed"}

@app.post("/api/webhook/facebook")
async def facebook_webhook(request: Request):
    """Handle Facebook Messenger webhook"""
    data = await request.json()
    
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            if "text" in message:
                result = messenger.handle_incoming_message(sender_id, message["text"], "facebook")
    return {"status": "ok"}

@app.get("/api/webhook/whatsapp")
@app.post("/api/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle WhatsApp Cloud API webhook"""
    if request.method == "GET":
        params = dict(request.query_params)
        challenge = whatsapp.verify_whatsapp_webhook(
            params.get("hub.mode"), params.get("hub.verify_token"), params.get("hub.challenge"), WHATSAPP_VERIFY_TOKEN
        )
        if challenge:
            return int(challenge)
        return {"error": "Verification failed"}
    
    data = await request.json()
    results = whatsapp.handle_whatsapp_webhook(data)
    return {"status": "ok", "processed": len(results)}

@app.get("/api/webhook/instagram")
@app.post("/api/webhook/instagram")
async def instagram_webhook(request: Request):
    """Handle Instagram DM webhook (uses same Meta infrastructure)"""
    if request.method == "GET":
        params = dict(request.query_params)
        challenge = messenger.handle_webhook_challenge(
            params.get("hub.mode"), params.get("hub.verify_token"), params.get("hub.challenge"), META_VERIFY_TOKEN
        )
        if challenge:
            return int(challenge)
        return {"error": "Verification failed"}
    
    data = await request.json()
    results = instagram.handle_instagram_webhook(data)
    return {"status": "ok", "processed": len(results)}

@app.post("/api/webhook/telegram")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    data = await request.json()
    result = telegram.handle_telegram_update(data)
    return {"status": "ok", "result": result}

@app.post("/api/email/check")
def api_check_emails():
    """Manually trigger email check (also runs via cron)"""
    results = email_handler.check_new_emails()
    return {"checked": len(results) if isinstance(results, list) else 0, "results": results}

@app.post("/api/email/send-proposal/{lead_id}")
def api_send_proposal(lead_id: int, proposal: str = Form(...)):
    result = email_handler.send_proposal_email(lead_id, proposal)
    return result

@app.post("/api/whatsapp/send/{lead_id}")
def api_send_whatsapp(lead_id: int, message: str = Form(...)):
    lead = crm.get_lead(lead_id)
    if not lead or not lead.get("phone"):
        return {"error": "Lead has no phone number"}
    result = whatsapp.send_whatsapp_message(lead["phone"], message)
    return result

@app.post("/api/instagram/send/{lead_id}")
def api_send_instagram(lead_id: int, message: str = Form(...)):
    lead = crm.get_lead(lead_id)
    if not lead or not lead.get("phone"):
        return {"error": "Lead has no Instagram ID stored in phone field"}
    result = instagram.send_instagram_dm(lead["phone"], message)
    return result

@app.get("/api/leads/by-channel")
def api_leads_by_channel():
    """Get lead count per channel"""
    channels = {}
    for channel in ACTIVE_CHANNELS:
        count = db.fetchone("SELECT COUNT(*) as count FROM leads WHERE source = ?", (channel,))
        channels[channel] = count["count"] if count else 0
    return channels

@app.get("/api/leads/unread")
def api_unread_messages():
    """Get leads with unread messages (no AI reply yet)"""
    return db.fetchall("""
        SELECT l.*, COUNT(m.id) as msg_count 
        FROM leads l 
        JOIN messages m ON l.id = m.lead_id 
        WHERE m.sender = 'lead' AND m.ai_analyzed = 0
        GROUP BY l.id
    """)

@app.get("/api/leads/{lead_id}")
def api_lead_detail(lead_id: int):
    lead = crm.get_lead(lead_id)
    messages = crm.get_messages(lead_id)
    return {"lead": lead, "messages": messages}

@app.get("/api/copilot/snapshot")
def api_copilot_snapshot():
    """Get the business data snapshot used by the AI copilot"""
    return copilot.get_business_snapshot()

@app.post("/api/copilot/chat")
async def api_copilot_chat(request: Request):
    """Ask the AI business copilot about leads, tasks, meetings, ads, and performance"""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        question = payload.get("question", "")
    else:
        form = await request.form()
        question = form.get("question", "")

    question = question.strip()
    if not question:
        return JSONResponse({"error": "Question is required"}, status_code=400)
    return copilot.ask_business_copilot(question)

@app.get("/api/copilot/history")
def api_copilot_history():
    return copilot.get_chat_history()

@app.get("/api/copilot/business-rules")
def api_business_rules():
    return copilot.get_business_rules()

@app.post("/api/copilot/business-rules")
async def api_add_business_rule(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        rule_text = payload.get("rule_text", "")
        category = payload.get("category", "general")
    else:
        form = await request.form()
        rule_text = form.get("rule_text", "")
        category = form.get("category", "general")

    rule_text = rule_text.strip()
    if not rule_text:
        return JSONResponse({"error": "Rule text is required"}, status_code=400)
    rule_id = copilot.add_business_rule(rule_text, category)
    return {"rule_id": rule_id, "rule_text": rule_text, "category": category}

@app.get("/api/copilot/daily-brief")
def api_daily_brief():
    return copilot.get_daily_brief()

@app.post("/api/copilot/daily-brief/generate")
def api_generate_daily_brief():
    return copilot.generate_daily_brief()

@app.get("/api/tasks")
def api_tasks(view: str = "open"):
    """Follow-up tasks. view = open | today | overdue | summary"""
    if view == "today":
        return crm.get_todays_followups()
    if view == "overdue":
        return crm.get_overdue_tasks()
    if view == "summary":
        return crm.get_task_summary()
    return crm.get_open_tasks()

@app.get("/api/leads/{lead_id}/tasks")
def api_lead_tasks(lead_id: int):
    return crm.get_tasks_for_lead(lead_id)

@app.post("/api/tasks")
async def api_create_task(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        payload = dict(await request.form())

    title = (payload.get("title") or "").strip()
    if not title:
        return JSONResponse({"error": "Task title is required"}, status_code=400)

    lead_id = payload.get("lead_id")
    lead_id = int(lead_id) if lead_id not in (None, "", "null") else None
    priority = int(payload.get("priority") or 3)
    task_id = crm.create_task(
        title,
        lead_id=lead_id,
        description=(payload.get("description") or "").strip(),
        task_type=payload.get("task_type") or "follow_up",
        priority=priority,
        due_date=payload.get("due_date") or None,
        created_by="user",
    )
    return crm.get_task(task_id)

@app.post("/api/tasks/generate-followups")
def api_generate_followups():
    """Queue a follow-up for every hot lead that has no open task yet."""
    created = 0
    for lead in crm.get_hot_leads(70):
        existing = db.fetchone("SELECT id FROM tasks WHERE lead_id = ? AND status = 'open'", (lead["id"],))
        if not existing:
            crm.ensure_followup_for_lead(lead["id"])
            created += 1
    return {"created": created}

@app.post("/api/tasks/{task_id}/complete")
def api_complete_task(task_id: int):
    task = crm.complete_task(task_id)
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return task

@app.post("/api/tasks/{task_id}/snooze")
def api_snooze_task(task_id: int, days: int = Form(1)):
    task = crm.snooze_task(task_id, days)
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return task

@app.post("/api/lead/{lead_id}/score")
def api_score_lead(lead_id: int):
    score = lead_scorer.score_lead(lead_id)
    return {"score": score}

@app.post("/api/lead/add")
async def api_add_lead(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        payload = dict(await request.form())

    name = payload.get("name")
    if not name:
        return JSONResponse({"error": "Lead name is required"}, status_code=400)

    business = payload.get("business", "") or payload.get("business_name", "")
    phone = payload.get("phone", "")
    email = payload.get("email", "")
    source = payload.get("source", "manual")
    notes = payload.get("notes", "")
    location = payload.get("location", "")
    industry = payload.get("industry", "")
    status = payload.get("status", "new")

    lead_id = crm.create_lead(
        name=name,
        business_name=business,
        phone=phone,
        email=email,
        source=source,
        notes=notes,
        location=location,
        industry=industry,
        status=status
    )
    return {"lead_id": lead_id, "name": name, "status": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=DASHBOARD_HOST, port=DASHBOARD_PORT)
