import json
from datetime import datetime, timedelta
from database import db

def create_lead(name, business_name, phone, email, source, notes="", location="", industry="", status="new", tags="", place_id=""):
    sql = """
    INSERT INTO leads (name, business_name, phone, email, source, notes, location, industry, status, tags, place_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return db.execute(sql, (name, business_name, phone, email, source, notes, location, industry, status, tags, place_id))

def get_lead(lead_id):
    return db.fetchone("SELECT * FROM leads WHERE id = ?", (lead_id,))

def get_lead_by_phone(phone):
    return db.fetchone("SELECT * FROM leads WHERE phone = ?", (phone,))

def get_lead_by_email(email):
    return db.fetchone("SELECT * FROM leads WHERE email = ?", (email,))

def update_lead_status(lead_id, status):
    db.execute("UPDATE leads SET status = ?, updated_at = ? WHERE id = ?", (status, datetime.now().isoformat(), lead_id))

def update_lead_score(lead_id, score):
    db.execute("UPDATE leads SET score = ?, updated_at = ? WHERE id = ?", (score, datetime.now().isoformat(), lead_id))

def update_lead(lead_id, **kwargs):
    """Update arbitrary columns for a lead dynamically"""
    if not kwargs:
        return
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(datetime.now().isoformat())
    values.append(lead_id)
    sql = f"UPDATE leads SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
    db.execute(sql, tuple(values))

def add_message(lead_id, platform, content, sender, ai_analyzed=0, extracted_data=None):
    sql = """
    INSERT INTO messages (lead_id, platform, content, sender, ai_analyzed, extracted_data)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    return db.execute(sql, (lead_id, platform, content, sender, ai_analyzed, json.dumps(extracted_data) if extracted_data else None))

def get_messages(lead_id):
    return db.fetchall("SELECT * FROM messages WHERE lead_id = ? ORDER BY created_at ASC", (lead_id,))

def get_recent_leads(limit=20):
    return db.fetchall("SELECT * FROM leads ORDER BY created_at DESC LIMIT ?", (limit,))

def get_leads_by_status(status):
    return db.fetchall("SELECT * FROM leads WHERE status = ? ORDER BY score DESC", (status,))

def get_hot_leads(min_score=70):
    return db.fetchall("SELECT * FROM leads WHERE score >= ? ORDER BY score DESC", (min_score,))

def add_meeting(lead_id, meeting_date, location, suggested_by_ai=1, notes=""):
    sql = """
    INSERT INTO meetings (lead_id, suggested_by_ai, meeting_date, location, notes)
    VALUES (?, ?, ?, ?, ?)
    """
    return db.execute(sql, (lead_id, suggested_by_ai, meeting_date, location, notes))

def get_todays_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    return db.fetchall("SELECT * FROM meetings WHERE meeting_date = ? AND outcome IS NULL", (today,))


# ---------------------------------------------------------------------------
# Follow-up tasks  (Phase 4: Sales Workflow — "reduce missed follow-ups")
# ---------------------------------------------------------------------------

# Select tasks joined with their lead so the UI can show who each one is about.
_TASK_SELECT = """
SELECT t.*, l.name AS lead_name, l.business_name AS lead_business,
       l.phone AS lead_phone, l.email AS lead_email, l.score AS lead_score
FROM tasks t
LEFT JOIN leads l ON l.id = t.lead_id
"""

def create_task(title, lead_id=None, description="", task_type="follow_up",
                priority=3, due_date=None, created_by="user"):
    """Create a follow-up task. due_date is 'YYYY-MM-DD' (defaults to today)."""
    if not due_date:
        due_date = datetime.now().strftime("%Y-%m-%d")
    sql = """
    INSERT INTO tasks (lead_id, title, description, task_type, priority, due_date, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return db.execute(sql, (lead_id, title, description, task_type, priority, due_date, created_by))

def get_task(task_id):
    return db.fetchone(_TASK_SELECT + " WHERE t.id = ?", (task_id,))

def get_open_tasks(limit=100):
    return db.fetchall(
        _TASK_SELECT + " WHERE t.status = 'open' ORDER BY t.priority ASC, t.due_date ASC LIMIT ?",
        (limit,),
    )

def get_tasks_for_lead(lead_id):
    return db.fetchall(_TASK_SELECT + " WHERE t.lead_id = ? ORDER BY t.due_date ASC", (lead_id,))

def get_todays_followups():
    today = datetime.now().strftime("%Y-%m-%d")
    return db.fetchall(
        _TASK_SELECT + " WHERE t.status = 'open' AND t.due_date = ? ORDER BY t.priority ASC",
        (today,),
    )

def get_overdue_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    return db.fetchall(
        _TASK_SELECT + " WHERE t.status = 'open' AND t.due_date < ? ORDER BY t.due_date ASC",
        (today,),
    )

def get_task_summary():
    """Counts the dashboard needs: overdue, due today, and total open."""
    today = datetime.now().strftime("%Y-%m-%d")
    open_count = db.fetchone("SELECT COUNT(*) AS c FROM tasks WHERE status = 'open'")
    overdue = db.fetchone("SELECT COUNT(*) AS c FROM tasks WHERE status = 'open' AND due_date < ?", (today,))
    today_count = db.fetchone("SELECT COUNT(*) AS c FROM tasks WHERE status = 'open' AND due_date = ?", (today,))
    return {
        "open": open_count["c"] if open_count else 0,
        "overdue": overdue["c"] if overdue else 0,
        "today": today_count["c"] if today_count else 0,
    }

def complete_task(task_id):
    db.execute(
        "UPDATE tasks SET status = 'done', updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), task_id),
    )
    return get_task(task_id)

def snooze_task(task_id, days=1):
    """Push an open task's due date forward by N days."""
    task = db.fetchone("SELECT due_date FROM tasks WHERE id = ?", (task_id,))
    base = datetime.now()
    if task and task.get("due_date"):
        try:
            base = datetime.strptime(task["due_date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            base = datetime.now()
    new_due = (base + timedelta(days=days)).strftime("%Y-%m-%d")
    db.execute(
        "UPDATE tasks SET due_date = ?, updated_at = ? WHERE id = ?",
        (new_due, datetime.now().isoformat(), task_id),
    )
    return get_task(task_id)

def get_worklist_stats():
    """Counts for the workspace header tiles."""
    total = db.fetchone("SELECT COUNT(*) AS c FROM leads")
    new_leads = db.fetchone("SELECT COUNT(*) AS c FROM leads WHERE status = 'new'")
    assigned = db.fetchone("SELECT COUNT(*) AS c FROM leads WHERE score >= 70")
    updates = db.fetchone(
        "SELECT COUNT(DISTINCT lead_id) AS c FROM messages WHERE sender = 'lead' AND ai_analyzed = 0"
    )
    return {
        "worklist": total["c"] if total else 0,
        "new_leads": new_leads["c"] if new_leads else 0,
        "updates": updates["c"] if updates else 0,
        "assigned": assigned["c"] if assigned else 0,
    }

def ensure_followup_for_lead(lead_id, title=None, due_date=None, priority=2):
    """Create a follow-up task for a lead unless one is already open.
    Used to auto-queue follow-ups for hot leads so they are never missed."""
    existing = db.fetchone(
        "SELECT id FROM tasks WHERE lead_id = ? AND status = 'open'", (lead_id,)
    )
    if existing:
        return existing["id"]
    lead = get_lead(lead_id)
    who = (lead.get("business_name") or lead.get("name") or "lead") if lead else "lead"
    return create_task(
        title or f"Follow up with {who}",
        lead_id=lead_id,
        task_type="follow_up",
        priority=priority,
        due_date=due_date,
        created_by="system",
    )
