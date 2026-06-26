import json
from core import crm

def score_lead(lead_id):
    """Score a lead based on messages, info completeness, and engagement"""
    lead = crm.get_lead(lead_id)
    if not lead:
        return 0
    
    score = 0
    
    # Info completeness
    if lead.get("phone"): score += 15
    if lead.get("email"): score += 10
    if lead.get("business_name") and lead["business_name"] != "Unknown": score += 10
    if lead.get("industry"): score += 5
    
    # Status bonus
    status_scores = {"new": 0, "contacted": 10, "qualified": 30, "proposal": 50, "negotiation": 70, "won": 100}
    score += status_scores.get(lead.get("status", "new"), 0)
    
    # Engagement (message count)
    messages = crm.get_messages(lead_id)
    msg_count = len(messages)
    score += min(msg_count * 3, 20)  # Max 20 for messages
    
    # AI-extracted data (hot signals)
    for msg in messages:
        data = msg.get("extracted_data")
        if data and isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                continue
        if data and isinstance(data, dict):
            if data.get("lead_temperature") == "hot": score += 15
            if data.get("budget") and data["budget"] != "unknown": score += 10
            if data.get("meeting_suggested"): score += 10
    
    score = min(score, 100)
    crm.update_lead_score(lead_id, score)
    return score

def get_leads_needing_action():
    """Get leads that need follow-up today"""
    # Hot leads without meetings
    hot = crm.get_hot_leads(70)
    needing_action = []
    for lead in hot:
        if lead.get("status") not in ["won", "lost"]:
            needing_action.append(lead)
    return needing_action

def classify_lead(analysis):
    """Classify based on AI analysis"""
    temp = analysis.get("lead_temperature", "cold")
    mapping = {"hot": 80, "warm": 55, "cold": 30}
    return mapping.get(temp, 30)
