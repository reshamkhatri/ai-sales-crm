import json
from core import crm, ai_brain
from database import db

def find_leads_to_outreach(source="manual"):
    """In a real system, this would scrape groups/directories. 
    For now, returns leads with no contact attempts."""
    return db.fetchall("SELECT * FROM leads WHERE source = ? AND status = 'new'", (source,))

def draft_outreach_for_lead(lead_id, platform):
    lead = crm.get_lead(lead_id)
    if not lead:
        return None
    
    draft = ai_brain.draft_outbound_message(lead, platform)
    
    db.execute(
        "INSERT INTO outbound_drafts (lead_id, platform, draft_text) VALUES (?, ?, ?)",
        (lead_id, platform, draft)
    )
    return draft

def generate_call_list(min_score=50):
    """Generate a list of leads for cold calling with scripts"""
    leads = db.fetchall("SELECT * FROM leads WHERE score >= ? AND (phone IS NOT NULL AND phone != '')", (min_score,))
    call_list = []
    for lead in leads:
        # Check cache in outbound_drafts
        cached = db.fetchone(
            "SELECT draft_text FROM outbound_drafts WHERE lead_id = ? AND platform = 'call' ORDER BY created_at DESC LIMIT 1",
            (lead["id"],)
        )
        if cached:
            script = cached["draft_text"]
        else:
            if not ai_brain.AI_ENABLED:
                script = "No AI provider configured. Set ANTHROPIC_API_KEY (Claude) or OPENAI_API_KEY in your .env to generate scripts."
            else:
                try:
                    script = ai_brain.generate_cold_call_script(lead)
                    if script and not script.startswith("[ERROR]"):
                        # Cache it
                        db.execute(
                            "INSERT INTO outbound_drafts (lead_id, platform, draft_text) VALUES (?, ?, ?)",
                            (lead["id"], "call", script)
                        )
                except Exception as e:
                    script = f"Error generating script: {e}"
        
        call_list.append({
            "lead_id": lead["id"],
            "name": lead["name"],
            "business": lead["business_name"],
            "phone": lead["phone"],
            "script": script,
            "score": lead["score"]
        })
    return call_list

def log_call(lead_id, phone, result, notes=""):
    db.execute(
        "INSERT INTO cold_calls (lead_id, phone, result, notes) VALUES (?, ?, ?, ?)",
        (lead_id, phone, result, notes)
    )

def export_call_list_to_csv(filename="call_list.csv"):
    import csv
    calls = generate_call_list()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Business", "Phone", "Score", "Script"])
        for c in calls:
            writer.writerow([c["name"], c["business"], c["phone"], c["score"], c["script"]])
    return filename
