import json
import hmac
import hashlib
from datetime import datetime, timedelta
from core import crm, ai_brain
from config import META_APP_SECRET

def verify_webhook_signature(payload, signature):
    """Verify Facebook webhook signature"""
    if not META_APP_SECRET or not signature:
        return True  # Skip if not configured
    payload_bytes = payload if isinstance(payload, bytes) else payload.encode()
    expected = hmac.new(META_APP_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

def handle_incoming_message(sender_id, message_text, platform="facebook"):
    """Process an incoming Facebook/Instagram message"""
    # Try to find existing lead by some identifier (simplified)
    # In production, you'd map sender_id to lead_id
    lead = crm.get_lead_by_phone(sender_id) or crm.get_lead_by_email(sender_id)
    
    if not lead:
        # Create new lead from message
        lead_id = crm.create_lead(
            name="Unknown",
            business_name="Unknown",
            phone="",
            email="",
            source=platform,
            notes=f"Facebook ID: {sender_id}"
        )
    else:
        lead_id = lead["id"]
    
    # Log message
    crm.add_message(lead_id, platform, message_text, "lead")
    
    # Get conversation history
    messages = crm.get_messages(lead_id)
    history = "\n".join([f"{m['sender']}: {m['content']}" for m in messages[-10:]])
    
    # AI analyzes and replies
    analysis = ai_brain.analyze_conversation(history)
    
    # Update lead with extracted data
    if analysis.get("lead_temperature") == "hot":
        crm.update_lead_score(lead_id, 85)
        crm.update_lead_status(lead_id, "qualified")
    elif analysis.get("lead_temperature") == "warm":
        crm.update_lead_score(lead_id, 60)
    
    # Save AI reply
    reply = analysis.get("reply_draft", "Thanks for reaching out! We'll get back to you shortly.")
    crm.add_message(lead_id, platform, reply, "assistant", ai_analyzed=1, extracted_data=analysis)
    
    # Suggest meeting if hot
    if analysis.get("meeting_suggested") and analysis.get("lead_temperature") == "hot":
        meeting_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        crm.add_meeting(lead_id, meeting_date, "Dubai", suggested_by_ai=1, notes="AI suggested: Ready to buy")
    
    return {"lead_id": lead_id, "reply": reply, "analysis": analysis}

def handle_webhook_challenge(mode, token, challenge, verify_token):
    """Facebook webhook verification"""
    if mode == "subscribe" and token == verify_token:
        return challenge
    return None
