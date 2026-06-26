import requests
from core import crm, ai_brain
from database import db
from config import TELEGRAM_BOT_TOKEN

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_telegram_message(chat_id, text):
    """Send a Telegram message"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "Telegram not configured"}
    
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=payload)
    return resp.json()

def handle_telegram_update(update):
    """Process a Telegram webhook update"""
    message = update.get("message", {})
    if not message:
        return None
    
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    username = message.get("from", {}).get("username", "Unknown")
    
    # Find or create lead using DB query first to maintain compatibility with notes-based lookup
    lead = db.fetchone(
        "SELECT * FROM leads WHERE phone = ? OR notes LIKE ? OR notes LIKE ?",
        (str(chat_id), f"%Telegram: {username}%", f"%Chat ID: {chat_id}%")
    )
    if lead and (not lead.get("phone") or lead.get("phone") == ""):
        crm.update_lead(lead["id"], phone=str(chat_id))
    
    # Process through unified inbox
    from core import unified_inbox
    res = unified_inbox.handle_incoming_message(
        lead_identifier=str(chat_id),
        message_text=text,
        platform="telegram",
        extra_data={"phone": str(chat_id), "name": username, "notes": f"Telegram: {username}, Chat ID: {chat_id}"}
    )
    lead_id = res["lead_id"]
    reply = res["reply"]
    analysis = res["analysis"]
    
    # Send reply via Telegram
    send_telegram_message(chat_id, reply)
    
    # Log reply and re-score
    unified_inbox.log_ai_reply(lead_id, "telegram", reply, analysis)
    
    return {"lead_id": lead_id, "chat_id": chat_id, "reply": reply}

def set_telegram_webhook(webhook_url):
    """Set the Telegram webhook"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "Telegram not configured"}
    
    url = f"{TELEGRAM_API}/setWebhook"
    resp = requests.post(url, json={"url": webhook_url})
    return resp.json()
