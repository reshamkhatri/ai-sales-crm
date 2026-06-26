from core import crm, ai_brain, lead_scorer
from datetime import datetime, timedelta

SYSTEM_PERSONA = "You are the AI Sales Director for a Dubai web design agency. Be professional, concise, and actionable."

def handle_incoming_message(lead_identifier, message_text, platform, extra_data=None):
    """
    Unified handler for ALL incoming messages from ANY channel.
    
    Args:
        lead_identifier: phone, email, or external ID
        message_text: the incoming message
        platform: whatsapp, instagram, facebook, email, telegram, linkedin, manual
        extra_data: dict with name, business, email, phone, etc.
    
    Returns:
        dict with lead_id, reply, analysis, action_suggested
    """
    # Find or create lead
    lead = None
    
    # Try to find by phone first (WhatsApp, Instagram ID stored here)
    if extra_data and extra_data.get("phone"):
        lead = crm.get_lead_by_phone(extra_data["phone"])
    
    # Try by email
    if not lead and extra_data and extra_data.get("email"):
        lead = crm.get_lead_by_email(extra_data["email"])
    
    # Try by the identifier itself (could be phone/instagram ID)
    if not lead and lead_identifier:
        lead = crm.get_lead_by_phone(lead_identifier)
    
    if not lead:
        # Create new lead
        lead_id = crm.create_lead(
            name=extra_data.get("name", "Unknown") if extra_data else "Unknown",
            business_name=extra_data.get("business_name", "Unknown") if extra_data else "Unknown",
            phone=extra_data.get("phone", lead_identifier) if extra_data else lead_identifier,
            email=extra_data.get("email", "") if extra_data else "",
            source=platform,
            notes=extra_data.get("notes", "") if extra_data else ""
        )
    else:
        lead_id = lead["id"]
        # Update source if new
        if lead.get("source") != platform:
            # Add note about new channel
            crm.add_message(lead_id, platform, f"[Lead also contacted via {platform}]", "system")
    
    # Log the incoming message
    crm.add_message(lead_id, platform, message_text, "lead")
    
    # Get conversation history (last 10 messages)
    messages = crm.get_messages(lead_id)
    history = "\n".join([f"{m['sender']}: {m['content']}" for m in messages[-10:]])
    
    # AI analyzes conversation
    analysis = ai_brain.analyze_conversation(history)
    
    # Update lead based on analysis
    temperature = analysis.get("lead_temperature", "cold")
    if temperature == "hot":
        crm.update_lead_score(lead_id, 85)
        crm.update_lead_status(lead_id, "qualified")
    elif temperature == "warm":
        crm.update_lead_score(lead_id, 60)
    elif temperature == "cold":
        crm.update_lead_score(lead_id, 30)
    
    # Update extracted info if available
    if extra_data and lead:
        # Merge any new info into lead
        updates = {}
        for field in ["name", "business_name", "email", "phone", "location", "industry"]:
            val = extra_data.get(field)
            if val and (not lead.get(field) or lead.get(field) in ["Unknown", ""]):
                updates[field] = val
        if updates:
            crm.update_lead(lead_id, **updates)
    
    # Get reply draft
    reply = analysis.get("reply_draft", "Thanks for reaching out! We'll get back to you shortly.")
    
    # Determine suggested action
    action_suggested = None
    if analysis.get("meeting_suggested") and temperature == "hot":
        meeting_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        crm.add_meeting(lead_id, meeting_date, "Dubai", suggested_by_ai=1, 
                       notes=f"AI suggested: {platform} lead ready to buy")
        action_suggested = "meeting"
    
    # Extract phone number if present in message and not already saved
    phone_extracted = analysis.get("phone_collected", False)
    if phone_extracted:
        current_lead = crm.get_lead(lead_id)
        if current_lead and not current_lead.get("phone"):
            import re
            # Parse phone from message text (simple regex for 7-15 digit numbers, optionally with +, spaces, dashes)
            phone_match = re.search(r'\+?[0-9]{1,4}[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}', message_text)
            if phone_match:
                extracted_phone = phone_match.group(0).strip()
                digits = re.sub(r'\D', '', extracted_phone)
                if len(digits) >= 7:
                    crm.update_lead(lead_id, phone=extracted_phone)
    
    return {
        "lead_id": lead_id,
        "reply": reply,
        "analysis": analysis,
        "action_suggested": action_suggested,
        "temperature": temperature
    }


def log_ai_reply(lead_id, platform, reply_text, analysis):
    """Log the AI's reply to the conversation"""
    crm.add_message(lead_id, platform, reply_text, "assistant", ai_analyzed=1, extracted_data=analysis)
    
    # Re-score lead after AI reply
    lead_scorer.score_lead(lead_id)


def get_lead_context(lead_id):
    """Get full context for a lead: profile, all messages, score, meetings"""
    lead = crm.get_lead(lead_id)
    messages = crm.get_messages(lead_id)
    
    # Get meetings
    meetings = crm.get_todays_tasks()  # Could be filtered by lead_id
    
    # Build summary
    summary = {
        "lead": lead,
        "messages": messages,
        "total_messages": len(messages),
        "platforms": list(set(m["platform"] for m in messages)),
        "meetings": meetings
    }
    return summary


def route_outbound(lead_id, platform, message_text=None):
    """
    Route an outbound message to the right platform handler.
    If message_text is None, AI drafts it.
    """
    from core import outbound, whatsapp, instagram, email_handler, telegram
    
    lead = crm.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}
    
    # Draft if not provided
    if not message_text:
        message_text = ai_brain.draft_outbound_message(lead, platform)
    
    # Save draft
    outbound.draft_outreach_for_lead(lead_id, platform)
    
    # Route to platform (only for channels that support sending)
    result = {"draft": message_text, "sent": False}
    
    if platform == "whatsapp" and lead.get("phone"):
        send_result = whatsapp.send_whatsapp_message(lead["phone"], message_text)
        result["sent"] = True
        result["send_result"] = send_result
    
    elif platform == "instagram" and lead.get("phone"):
        # phone field stores Instagram ID for Instagram leads
        send_result = instagram.send_instagram_dm(lead["phone"], message_text)
        result["sent"] = True
        result["send_result"] = send_result
    
    elif platform == "email" and lead.get("email"):
        send_result = email_handler.send_email(lead["email"], "Following up", message_text)
        result["sent"] = True
        result["send_result"] = send_result
    
    elif platform == "telegram":
        # Would need chat_id stored somewhere
        pass
    
    return result
