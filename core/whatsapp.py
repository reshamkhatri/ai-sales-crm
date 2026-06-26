import requests
import json
from datetime import datetime, timedelta
from core import crm, ai_brain
from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN

WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}"

def send_whatsapp_message(phone_number, message_text, template=False):
    """Send a WhatsApp message via Cloud API. 
    For non-template, user must have messaged you in last 24h.
    """
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        return {"error": "WhatsApp credentials not configured"}
    
    url = f"{WHATSAPP_API_URL}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if template:
        # For first contact or after 24h, you MUST use a pre-approved template
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": "hello_world",  # You must create this in Meta Business Manager
                "language": {"code": "en"}
            }
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message_text}
        }
    
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()

def handle_whatsapp_webhook(body):
    """Process incoming WhatsApp message via webhook"""
    entries = body.get("entry", [])
    results = []
    
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "messages" in value:
                for msg in value["messages"]:
                    phone = msg.get("from")  # Sender's phone number
                    msg_type = msg.get("type")
                    
                    if msg_type == "text":
                        text = msg.get("text", {}).get("body", "")
                    elif msg_type == "interactive":
                        text = msg.get("interactive", {}).get("button_reply", {}).get("title", "")
                    else:
                        text = f"[Non-text message: {msg_type}]"
                    
                    # Find or create, log, analyze, score, and handle via unified inbox
                    from core import unified_inbox
                    res = unified_inbox.handle_incoming_message(
                        lead_identifier=phone,
                        message_text=text,
                        platform="whatsapp",
                        extra_data={"phone": phone, "notes": f"WhatsApp: {phone}"}
                    )
                    lead_id = res["lead_id"]
                    reply = res["reply"]
                    analysis = res["analysis"]
                    
                    # Send reply via WhatsApp
                    send_result = send_whatsapp_message(phone, reply)
                    
                    # Log reply and re-score
                    unified_inbox.log_ai_reply(lead_id, "whatsapp", reply, analysis)
                    
                    results.append({"lead_id": lead_id, "phone": phone, "reply": reply, "analysis": analysis})
    
    return results

def verify_whatsapp_webhook(mode, token, challenge, verify_token):
    """WhatsApp webhook verification"""
    if mode == "subscribe" and token == verify_token:
        return challenge
    return None

def get_conversation_history(phone):
    """Get last 24h of messages for a phone number"""
    lead = crm.get_lead_by_phone(phone)
    if not lead:
        return []
    return crm.get_messages(lead["id"])

def mark_template_message(phone_number, template_name, language="en"):
    """Helper to send a pre-approved template message (for after 24h or cold outreach)"""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        return {"error": "WhatsApp not configured"}
    
    url = f"{WHATSAPP_API_URL}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language}
        }
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()
