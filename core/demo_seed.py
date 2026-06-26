"""Seed a small, realistic demo dataset — ONLY when the leads table is empty.

On Render's free tier the filesystem is ephemeral, so the SQLite DB resets on
each deploy. This keeps the public demo looking populated without ever touching
a database that already has real data.
"""
from datetime import datetime, timedelta
from database import db
from core import crm


def seed_if_empty():
    existing = db.fetchone("SELECT COUNT(*) AS c FROM leads")
    if existing and existing["c"] > 0:
        return False  # real data present — never overwrite

    today = datetime.now()
    leads = [
        ("Jessie Caballero", "Microsoft", "+12055550100", "jessie@example.com", "referral", "negotiation", 86, "Product Manager", "Syracuse, Connecticut"),
        ("Jane Doe", "Nike", "+12055550111", "jane@nike.com", "linkedin", "proposal", 78, "Marketing Manager", "Portland, Oregon"),
        ("Aisha Rahman", "Marina Bistro", "+971500000001", "aisha@marinabistro.ae", "whatsapp", "qualified", 72, "Restaurant", "Dubai Marina"),
        ("Jack Donovan", "ACME", "+12055550122", "jack@acme.io", "google-maps", "qualified", 57, "CEO", "Austin, Texas"),
        ("Lisa Gun", "Initech", "+12055550144", "lisa@initech.com", "lead-form", "contacted", 48, "Operations", "Dallas, Texas"),
        ("Barry White", "Arasaka", "+12055550133", "barry@arasaka.co", "instagram", "new", 34, "CEO", "Night City"),
    ]
    ids = {}
    for name, biz, phone, email, src, status, score, industry, loc in leads:
        lid = crm.create_lead(name, biz, phone, email, src, "", loc, industry)
        crm.update_lead_status(lid, status)
        crm.update_lead_score(lid, score)
        ids[name] = lid

    j = ids["Jessie Caballero"]
    for plat, content, sender in [
        ("whatsapp", "Hey, how are you?", "lead"),
        ("whatsapp", "We discussed your wishes with the team and prepared a proposal.", "user"),
        ("whatsapp", "Sending it to you, I hope it meets your needs.", "user"),
        ("whatsapp", "Great, looking forward to it. I'll talk to finance and get back to you.", "lead"),
    ]:
        crm.add_message(j, plat, content, sender)

    crm.create_task("Send the proposal", lead_id=j, priority=1,
                    due_date=(today - timedelta(days=1)).strftime("%Y-%m-%d"))
    crm.create_task("Follow up after finance review", lead_id=j, priority=2)
    crm.create_task("Prepare contract draft", lead_id=ids["Jane Doe"], priority=2)
    return True
