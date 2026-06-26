import requests
import json
from datetime import datetime, timedelta
from core import crm, ai_brain
from config import META_ACCESS_TOKEN, META_INSTAGRAM_ID

INSTAGRAM_API_URL = "https://graph.facebook.com/v18.0"

def send_instagram_dm(user_id, message_text):
    """Send Instagram DM via Meta Graph API. 
    ONLY works if the user has already messaged you (24h window).
    """
    if not META_ACCESS_TOKEN or not META_INSTAGRAM_ID:
        return {"error": "Instagram credentials not configured"}
    
    url = f"{INSTAGRAM_API_URL}/me/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"  # Must be RESPONSE or UPDATE, not MESSAGE_TAG
    }
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()

def handle_instagram_webhook(body):
    """Process incoming Instagram DM via webhook (same as Facebook, different sender IDs)"""
    entries = body.get("entry", [])
    results = []
    
    for entry in entries:
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            
            if "text" in message:
                text = message["text"]
            else:
                text = "[Media/Story reply]"
            
            # Find or create, log, analyze, score, and handle via unified inbox
            from core import unified_inbox
            res = unified_inbox.handle_incoming_message(
                lead_identifier=sender_id,
                message_text=text,
                platform="instagram",
                extra_data={"phone": sender_id, "notes": f"Instagram ID: {sender_id}"}
            )
            lead_id = res["lead_id"]
            reply = res["reply"]
            analysis = res["analysis"]
            
            # Reply via Instagram
            send_instagram_dm(sender_id, reply)
            
            # Log reply and re-score
            unified_inbox.log_ai_reply(lead_id, "instagram", reply, analysis)
            
            results.append({"lead_id": lead_id, "instagram_id": sender_id, "reply": reply})
    
    return results

def get_instagram_profile_info(username):
    """Get basic Instagram business profile info (if they have a business account)"""
    if not META_ACCESS_TOKEN:
        return None
    
    url = f"{INSTAGRAM_API_URL}/{META_INSTAGRAM_ID}"
    params = {
        "fields": "username,biography,followers_count,follows_count,media_count",
        "access_token": META_ACCESS_TOKEN
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    return None
