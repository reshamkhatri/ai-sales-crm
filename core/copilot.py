import json
from datetime import datetime, timedelta

from config import AGENCY_LOCATION, AGENCY_NAME, AGENCY_SERVICES, OPENAI_API_KEY
from core import ai_brain
from database import db


def _today():
    return datetime.now().date()


def _row_count(query, params=()):
    row = db.fetchone(query, params)
    return row["count"] if row else 0


def get_business_snapshot(days=7):
    """Collect compact, source-backed business context for the copilot."""
    since = (_today() - timedelta(days=days)).isoformat()
    today = _today().isoformat()

    leads = db.fetchall(
        """
        SELECT id, name, business_name, phone, email, source, status, score,
               notes, location, industry, created_at, updated_at
        FROM leads
        ORDER BY created_at DESC
        LIMIT 50
        """
    )
    hot_leads = db.fetchall(
        """
        SELECT id, name, business_name, phone, email, source, status, score,
               notes, location, industry, created_at, updated_at
        FROM leads
        WHERE score >= 70
        ORDER BY score DESC, updated_at DESC
        LIMIT 10
        """
    )
    overdue_tasks = db.fetchall(
        """
        SELECT t.*, l.name, l.business_name, l.score
        FROM tasks t
        LEFT JOIN leads l ON l.id = t.lead_id
        WHERE t.status = 'open' AND t.due_date IS NOT NULL AND t.due_date < ?
        ORDER BY t.due_date ASC, t.priority ASC
        LIMIT 10
        """,
        (today,),
    )
    open_tasks = db.fetchall(
        """
        SELECT t.*, l.name, l.business_name, l.score
        FROM tasks t
        LEFT JOIN leads l ON l.id = t.lead_id
        WHERE t.status = 'open'
        ORDER BY t.priority ASC, t.due_date ASC
        LIMIT 10
        """
    )
    meetings_today = db.fetchall(
        """
        SELECT m.*, l.name, l.business_name, l.score
        FROM meetings m
        LEFT JOIN leads l ON l.id = m.lead_id
        WHERE m.meeting_date = ? AND (m.outcome IS NULL OR m.outcome = '')
        ORDER BY m.created_at ASC
        """,
        (today,),
    )
    recent_messages = db.fetchall(
        """
        SELECT m.id, m.lead_id, m.platform, m.sender, m.content, m.created_at,
               l.name, l.business_name, l.score, l.status
        FROM messages m
        LEFT JOIN leads l ON l.id = m.lead_id
        ORDER BY m.created_at DESC
        LIMIT 30
        """
    )
    recommendations = db.fetchall(
        """
        SELECT id, type, content, created_at
        FROM ai_recommendations
        WHERE actioned = 0
        ORDER BY created_at DESC
        LIMIT 10
        """
    )
    rules = db.fetchall(
        """
        SELECT id, rule_text, category, created_at
        FROM business_rules
        WHERE active = 1
        ORDER BY created_at DESC
        LIMIT 25
        """
    )
    channel_counts = db.fetchall(
        """
        SELECT COALESCE(source, 'unknown') AS source, COUNT(*) AS count
        FROM leads
        GROUP BY COALESCE(source, 'unknown')
        ORDER BY count DESC
        """
    )
    status_counts = db.fetchall(
        """
        SELECT COALESCE(status, 'unknown') AS status, COUNT(*) AS count
        FROM leads
        GROUP BY COALESCE(status, 'unknown')
        ORDER BY count DESC
        """
    )
    ads = db.fetchall(
        """
        SELECT c.name, c.status, i.date, i.spend, i.impressions, i.clicks,
               i.leads, i.cost_per_lead
        FROM ad_insights i
        LEFT JOIN ad_campaigns c ON c.id = i.campaign_id
        ORDER BY i.date DESC
        LIMIT 20
        """
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "window_days": days,
        "agency": {
            "name": AGENCY_NAME,
            "services": AGENCY_SERVICES,
            "location": AGENCY_LOCATION,
        },
        "metrics": {
            "total_leads": _row_count("SELECT COUNT(*) AS count FROM leads"),
            "new_leads_today": _row_count("SELECT COUNT(*) AS count FROM leads WHERE date(created_at) = ?", (today,)),
            "new_leads_window": _row_count("SELECT COUNT(*) AS count FROM leads WHERE date(created_at) >= ?", (since,)),
            "hot_leads": _row_count("SELECT COUNT(*) AS count FROM leads WHERE score >= 70"),
            "warm_leads": _row_count("SELECT COUNT(*) AS count FROM leads WHERE score BETWEEN 40 AND 69"),
            "cold_leads": _row_count("SELECT COUNT(*) AS count FROM leads WHERE score < 40"),
            "open_tasks": _row_count("SELECT COUNT(*) AS count FROM tasks WHERE status = 'open'"),
            "overdue_tasks": _row_count(
                "SELECT COUNT(*) AS count FROM tasks WHERE status = 'open' AND due_date IS NOT NULL AND due_date < ?",
                (today,),
            ),
            "meetings_today": len(meetings_today),
            "messages_window": _row_count("SELECT COUNT(*) AS count FROM messages WHERE date(created_at) >= ?", (since,)),
        },
        "channel_counts": channel_counts,
        "status_counts": status_counts,
        "hot_leads": hot_leads,
        "recent_leads": leads,
        "recent_messages": recent_messages,
        "meetings_today": meetings_today,
        "open_tasks": open_tasks,
        "overdue_tasks": overdue_tasks,
        "recommendations": recommendations,
        "business_rules": rules,
        "ad_insights": ads,
    }


def _fallback_answer(question, snapshot):
    import re
    question_lower = question.lower()
    
    def matches_any(words):
        for w in words:
            if re.search(r'\b' + re.escape(w) + r'\b', question_lower):
                return True
        return False
    
    # 1. Greetings Intent
    if matches_any(["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
        return (
            f"Hello Alex! I am your Sales AI Copilot for {snapshot['agency']['name']}.\n\n"
            f"I am connected to the CRM, Meta Ads, and task manager. You can ask me questions like:\n"
            f"- *'How is business going?'* to get a snapshot summary.\n"
            f"- *'Which leads are hot?'* to view high-priority prospects.\n"
            f"- *'Draft an outreach script for [Lead Name]'* to write a message template.\n"
            f"- *'Analyze ad campaigns'* to check marketing performance.\n\n"
            f"What would you like to analyze or draft today?"
        )

    # 2. Ads & Marketing Spend Intent
    if matches_any(["ad", "spend", "meta", "campaign", "marketing", "ads"]):
        ads = snapshot.get("ad_insights", [])
        if not ads:
            return (
                "📊 **Meta Ads Campaign Analysis**\n\n"
                "I couldn't find any Meta Ad Campaign insights in the database.\n\n"
                "**Recommended Action:** Please check if Meta Ad campaigns have been synced or imported into the `ad_campaigns` and `ad_insights` tables."
            )
        # Summarize campaigns
        total_spend = sum(ad.get("spend") or 0.0 for ad in ads)
        total_leads = sum(ad.get("leads") or 0 for ad in ads)
        cost_per_lead = total_spend / total_leads if total_leads > 0 else 0.0
        
        lines = [
            f"### 📊 Meta Ads Campaign Analysis (Last 7 Days)",
            f"- **Total Spend:** AED {total_spend:,.2f}",
            f"- **Total Leads Generated:** {total_leads}",
            f"- **Average Cost Per Lead (CPL):** AED {cost_per_lead:,.2f}",
            "",
            "**Recent Active Campaigns:**"
        ]
        # Find best and worst campaigns
        best_campaign = None
        worst_campaign = None
        min_cpl = float('inf')
        max_cpl = 0.0
        for ad in ads[:5]:
            name = ad.get("name") or "Unnamed Campaign"
            status = ad.get("status") or "unknown"
            spend = ad.get("spend") or 0.0
            leads = ad.get("leads") or 0
            cpl = ad.get("cost_per_lead") or (spend / leads if leads > 0 else 0.0)
            lines.append(f"- **{name}** ({status.upper()}): Spent AED {spend:,.2f}, generated {leads} leads, CPL: AED {cpl:,.2f}")
            
            if status.lower() == 'active' or True:
                if leads > 0 and cpl < min_cpl:
                    min_cpl = cpl
                    best_campaign = name
                if cpl > max_cpl or (leads == 0 and spend > 0):
                    max_cpl = cpl
                    worst_campaign = name

        lines.append("")
        lines.append("### 🤖 Copilot Recommendations:")
        if best_campaign:
            lines.append(f"1. **Scale Up:** Campaign *'{best_campaign}'* has the lowest Cost Per Lead (AED {min_cpl:,.2f}). Suggest increasing daily budget by 15-20%.")
        if worst_campaign:
            lines.append(f"2. **Pause or Optimize:** Campaign *'{worst_campaign}'* has a high Cost Per Lead or zero leads. Recommend reviewing ad creatives or pausing to prevent budget leak.")
        else:
            lines.append("1. All campaigns are operating within normal efficiency bounds.")
        
        return "\n".join(lines)

    # 3. CRM & Leads Intent
    if matches_any(["lead", "leads", "hot", "prospect", "prospects", "client", "clients", "customer", "customers", "pipeline"]):
        leads = snapshot.get("recent_leads", [])
        hot_leads = [l for l in leads if (l.get("score") or 0) >= 70]
        
        if not leads:
            return "I found no leads in the CRM database yet."
            
        lines = [
            f"### 👥 Lead CRM Summary",
            f"- **Total Leads:** {snapshot['metrics']['total_leads']}",
            f"- **Hot Leads (Score >= 70):** {snapshot['metrics']['hot_leads']}",
            f"- **Warm Leads (Score 40-69):** {snapshot['metrics']['warm_leads']}",
            f"- **Cold Leads (Score < 40):** {snapshot['metrics']['cold_leads']}",
            "",
            "**Top Hot Prospects requiring immediate attention:**"
        ]
        
        if hot_leads:
            for idx, lead in enumerate(hot_leads[:5], 1):
                name = lead.get("name") or "Unknown Lead"
                biz = lead.get("business_name") or "No business name"
                score = lead.get("score") or 0
                status = lead.get("status") or "new"
                loc = lead.get("location") or "Not set"
                ind = lead.get("industry") or "Not set"
                notes = lead.get("notes") or "No notes"
                lines.append(f"{idx}. **{name}** ({biz}) — **Score: {score}** (Status: *{status.upper()}*)")
                lines.append(f"   - *Location:* {loc} | *Industry:* {ind}")
                lines.append(f"   - *Latest Notes:* {notes}")
        else:
            lines.append("No hot leads found with a score of 70 or above. Showing most recent leads:")
            for idx, lead in enumerate(leads[:5], 1):
                name = lead.get("name") or "Unknown Lead"
                biz = lead.get("business_name") or "No business name"
                score = lead.get("score") or 0
                lines.append(f"{idx}. **{name}** ({biz}) — **Score: {score}** (Status: *{lead.get('status', 'new').upper()}*)")
                
        lines.append("")
        lines.append("**Recommended Next Action:** Call the highest scoring lead first to confirm budget and timeline before drafting a proposal.")
        return "\n".join(lines)

    # 4. Tasks & Meetings Intent
    if matches_any(["task", "tasks", "follow", "todo", "todos", "action", "actions", "meeting", "meetings"]):
        open_tasks = snapshot.get("open_tasks", [])
        overdue_tasks = snapshot.get("overdue_tasks", [])
        meetings = snapshot.get("meetings_today", [])
        
        lines = [
            f"### 📅 Follow-ups, Tasks & Meetings",
            f"- **Open Tasks:** {snapshot['metrics']['open_tasks']}",
            f"- **Overdue Tasks:** {snapshot['metrics']['overdue_tasks']}",
            f"- **Meetings Today:** {snapshot['metrics']['meetings_today']}",
            ""
        ]
        
        if meetings:
            lines.append("**Meetings scheduled for today:**")
            for m in meetings:
                lead_name = m.get("lead_name") or f"Lead #{m.get('lead_id')}"
                lines.append(f"- **{lead_name}**: scheduled at {m.get('meeting_date')}. Notes: {m.get('notes') or 'none'}")
            lines.append("")
            
        if overdue_tasks:
            lines.append("**⚠️ Overdue Tasks:**")
            for t in overdue_tasks[:5]:
                lead_name = t.get("lead_name") or f"Lead #{t.get('lead_id')}"
                lines.append(f"- *{t.get('title')}* for **{lead_name}** (due {t.get('due_date') or 'immediately'})")
            lines.append("")
            
        if open_tasks:
            lines.append("**Upcoming Active Tasks:**")
            for t in open_tasks[:5]:
                lead_name = t.get("lead_name") or f"Lead #{t.get('lead_id')}"
                lines.append(f"- *{t.get('title')}* for **{lead_name}** (due {t.get('due_date') or 'not set'})")
        else:
            lines.append("No open tasks found.")
            
        lines.append("")
        lines.append("**Recommended Next Action:** Clear the overdue follow-ups first before scheduling new meetings.")
        return "\n".join(lines)

    # 5. Writing Outreach Scripts Intent
    if matches_any(["script", "scripts", "outreach", "email", "emails", "call", "calls", "write", "template", "templates", "draft", "drafts"]):
        target_lead = None
        leads = snapshot.get("recent_leads", [])
        for lead in leads:
            lead_name = lead.get("name", "").lower()
            lead_biz = lead.get("business_name", "").lower()
            if (lead_name and lead_name in question_lower) or (lead_biz and lead_biz in question_lower):
                target_lead = lead
                break
                
        if not target_lead and leads:
            target_lead = leads[0]
            
        if not target_lead:
            return "I couldn't find any leads in the CRM database to draft an outreach script for."
            
        name = target_lead.get("name") or "Client"
        biz = target_lead.get("business_name") or "your business"
        loc = target_lead.get("location") or "Dubai"
        ind = target_lead.get("industry") or "Web Design"
        notes = target_lead.get("notes") or "design a premium website"
        
        lines = [
            f"### 📝 Generated Outbound Scripts for **{name}** ({biz})",
            f"*Based on lead details: Location: {loc}, Industry: {ind}, Notes: {notes}*",
            "",
            "#### 💬 WhatsApp / Message Outreach Draft",
            f"\"Hi {name}! Hope you are doing well. I saw your request regarding a new website for {biz}. At {snapshot['agency']['name']}, we specialize in designing high-converting websites for businesses in the {ind} space right here in {loc}. Would you be free for a quick 5-minute call tomorrow at 11 AM to discuss your ideas?\"",
            "",
            "#### ✉️ Cold Outreach Email Draft",
            f"**Subject:** Premium web design concepts for {biz}",
            f"\"Dear {name},",
            "",
            f"I came across {biz} and love what you are doing in the {ind} industry. I noticed that we could optimize your online conversion rates by refreshing your website design to match the premium standards of {loc}.",
            "",
            f"At {snapshot['agency']['name']}, we build customized digital assets. Would you be open to a brief chat next Tuesday to review some layout concepts we drafted for you?",
            "",
            "Best regards,",
            "Alex",
            f"Sales Director, {snapshot['agency']['name']}\"",
            "",
            "#### 📞 30-Second Cold Call Script",
            f"- **Hook:** \"Hi {name}, this is Alex from {snapshot['agency']['name']}. How are you doing today? I'm reaching out because I saw your recent interest in launching a premium digital experience for {biz}.\"",
            f"- **Problem:** \"A lot of {ind} agencies in {loc} lose up to 40% of potential bookings due to complex mobile designs.\"",
            f"- **Solution:** \"We build custom booking pipelines that turn visitors into paid clients automatically.\"",
            f"- **CTA:** \"I'd love to show you a quick 3-minute mock-up we made for {biz}. Do you have your calendar open for next Tuesday?\"",
        ]
        return "\n".join(lines)

    # 6. Rules Intent
    if matches_any(["rule", "rules", "instruction", "instructions", "preference", "preferences"]):
        rules = snapshot.get("business_rules", [])
        if not rules:
            return "There are no custom business rules stored in the database currently."
        lines = [
            "### 📜 Stored Business Rules & Preferences",
            "The following instructions guide my recommendations and automated draft generation:"
        ]
        for idx, rule in enumerate(rules, 1):
            lines.append(f"{idx}. **{rule.get('category', 'general').upper()}:** {rule.get('rule_text')}")
        return "\n".join(lines)

    # 7. General Business Overview Fallback
    metrics = snapshot["metrics"]
    hot_leads = snapshot["hot_leads"][:3]
    overdue = snapshot["overdue_tasks"][:3]
    
    lines = [
        f"### 📈 Business Pulse Overview",
        f"Greetings Alex! Here is your business pulse snapshot today:",
        f"- **Total Leads in CRM:** {metrics['total_leads']}",
        f"- **New Leads Today:** {metrics['new_leads_today']} leads",
        f"- **Hottest Opportunities:** {metrics['hot_leads']} leads (Score >= 70)",
        f"- **Pending Tasks:** {metrics['open_tasks']} active follow-ups",
        f"- **Meetings Today:** {metrics['meetings_today']} scheduled",
        ""
    ]
    
    if hot_leads:
        lines.append("**🔥 Top Hot Leads:**")
        for lead in hot_leads:
            name = lead.get("business_name") or lead.get("name") or f"Lead #{lead['id']}"
            lines.append(f"- **{name}** (Score {lead['score']}): Status *{lead['status']}*, Location: {lead.get('location', 'Dubai')}")
        lines.append("")
        
    if overdue:
        lines.append("**⚠️ Overdue Tasks:**")
        for task in overdue:
            name = task.get("business_name") or task.get("name") or f"Lead #{task.get('lead_id')}"
            lines.append(f"- *{task['title']}* for **{name}** (due {task.get('due_date')})")
        lines.append("")
        
    lines.append("**🤖 Recommended Actions for Today:**")
    lines.append("1. Follow up with the hottest leads above immediately.")
    lines.append("2. Clear the overdue follow-ups list to keep the pipeline moving.")
    lines.append("3. Review Meta Ads spend efficiency to verify campaign budgets.")
    
    return "\n".join(lines)


def ask_business_copilot(question):
    snapshot = get_business_snapshot()
    db.execute("INSERT INTO ai_chat_messages (role, content, data_snapshot) VALUES (?, ?, ?)",
               ("user", question, json.dumps(snapshot)))

    if not OPENAI_API_KEY:
        answer = _fallback_answer(question, snapshot)
    else:
        system = f"""You are the AI Business Copilot for {AGENCY_NAME}.
You answer only from the provided business snapshot. Do not invent numbers or facts.
If data is missing, say what is missing. Be concise, practical, and action-oriented.
When making important claims, mention the CRM source such as lead id, task id, or message id.
Agency services: {AGENCY_SERVICES}. Location: {AGENCY_LOCATION}."""
        prompt = f"""Business snapshot JSON:
{json.dumps(snapshot, ensure_ascii=False)}

CEO question:
{question}

Answer with:
1. Direct answer
2. What needs attention
3. Recommended next action
Keep it short and grounded in the snapshot."""
        answer = ai_brain.ask(prompt, system=system, temperature=0.2)

    db.execute("INSERT INTO ai_chat_messages (role, content, data_snapshot) VALUES (?, ?, ?)",
               ("assistant", answer, json.dumps(snapshot)))
    return {"answer": answer, "snapshot": snapshot}


def add_business_rule(rule_text, category="general"):
    return db.execute(
        "INSERT INTO business_rules (rule_text, category) VALUES (?, ?)",
        (rule_text, category),
    )


def get_business_rules():
    return db.fetchall(
        "SELECT * FROM business_rules WHERE active = 1 ORDER BY created_at DESC"
    )


def get_chat_history(limit=20):
    return db.fetchall(
        "SELECT role, content, created_at FROM ai_chat_messages ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )


def generate_daily_brief():
    snapshot = get_business_snapshot(days=1)
    question = "Generate today's CEO brief with hot leads, overdue follow-ups, meetings, ad notes, and the top 3 actions."

    if not OPENAI_API_KEY:
        content = _fallback_answer(question, snapshot)
    else:
        system = f"""You are the daily CEO briefing assistant for {AGENCY_NAME}.
Use only the provided data. Do not invent revenue, meetings, or campaign results.
Be crisp and executive-friendly."""
        prompt = f"""Create a daily CEO brief from this snapshot:
{json.dumps(snapshot, ensure_ascii=False)}

Sections:
- Business pulse
- Hot leads
- Follow-ups and meetings
- Ads and recommendations
- Top 3 actions today"""
        content = ai_brain.ask(prompt, system=system, temperature=0.2)

    brief_date = _today().isoformat()
    db.execute(
        """
        INSERT INTO daily_briefs (brief_date, content, data_snapshot)
        VALUES (?, ?, ?)
        ON CONFLICT(brief_date) DO UPDATE SET
            content = excluded.content,
            data_snapshot = excluded.data_snapshot,
            created_at = CURRENT_TIMESTAMP
        """,
        (brief_date, content, json.dumps(snapshot)),
    )
    return {"date": brief_date, "content": content, "snapshot": snapshot}


def get_daily_brief():
    brief_date = _today().isoformat()
    existing = db.fetchone("SELECT * FROM daily_briefs WHERE brief_date = ?", (brief_date,))
    if existing:
        try:
            created_at_str = existing.get("created_at")
            if created_at_str:
                # 1. Check if older than 1 hour (3600 seconds)
                created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                age = datetime.utcnow() - created_at
                if age.total_seconds() >= 3600:
                    return generate_daily_brief()
                
                # 2. Check if there were any database changes since the brief was generated
                has_changes_query = """
                SELECT EXISTS (
                    SELECT 1 FROM leads WHERE created_at > ? OR updated_at > ?
                    UNION ALL
                    SELECT 1 FROM messages WHERE created_at > ?
                    UNION ALL
                    SELECT 1 FROM tasks WHERE created_at > ? OR updated_at > ?
                    UNION ALL
                    SELECT 1 FROM meetings WHERE created_at > ?
                    UNION ALL
                    SELECT 1 FROM ai_recommendations WHERE created_at > ?
                    UNION ALL
                    SELECT 1 FROM business_rules WHERE created_at > ? OR updated_at > ?
                ) AS has_changes
                """
                params = (created_at_str,) * 9
                row = db.fetchone(has_changes_query, params)
                if row and row["has_changes"]:
                    return generate_daily_brief()
                
                return existing
        except Exception as e:
            # If check fails for any reason, regenerate brief
            return generate_daily_brief()
            
    return generate_daily_brief()
