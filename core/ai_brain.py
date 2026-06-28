import json
from config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    AGENCY_NAME, AGENCY_SERVICES, AGENCY_LOCATION,
)

# Provider selection: prefer Claude (Anthropic) when its key is present, otherwise
# fall back to OpenAI / any OpenAI-compatible provider (DeepSeek, Together, Groq, ...).
if ANTHROPIC_API_KEY:
    AI_PROVIDER = "anthropic"
elif OPENAI_API_KEY:
    AI_PROVIDER = "openai"
else:
    AI_PROVIDER = None

# Callers check this instead of a specific provider's key so either provider works.
AI_ENABLED = AI_PROVIDER is not None

_anthropic_client = None
_openai_client = None

if AI_PROVIDER == "anthropic":
    import anthropic
    _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
elif AI_PROVIDER == "openai":
    import openai
    # base_url lets us use any OpenAI-compatible provider. Keep timeout/retries
    # modest so a slow or down gateway fails fast and the caller can fall back.
    _openai_client = openai.OpenAI(
        api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL or None,
        timeout=30, max_retries=1,
    )


def ask(prompt, system="You are a helpful sales and marketing assistant.", temperature=0.7):
    if not AI_ENABLED:
        return "[ERROR] No AI provider configured. Set ANTHROPIC_API_KEY (Claude) or OPENAI_API_KEY in your .env."
    try:
        if AI_PROVIDER == "anthropic":
            # Opus 4.8 rejects `temperature`, so it is intentionally not forwarded;
            # callers pass it only for the OpenAI path.
            resp = _anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(b.text for b in resp.content if b.type == "text")

        resp = _openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[ERROR] {e}"

SYSTEM_PERSONA = f"""You are the AI Sales Director for {AGENCY_NAME}, a web design agency in {AGENCY_LOCATION}.
Your services: {AGENCY_SERVICES}.
You analyze ad performance, suggest improvements, and help convert leads.
Be concise, direct, and actionable. Speak like a Dubai business professional."""

def analyze_ads(ad_data_json):
    prompt = f"""Analyze this Meta ad performance data for the last 7 days.

Data: {ad_data_json}

Tell me:
1. Which ad is performing best and why
2. Which ad to kill immediately
3. What type of ad creative to test next
4. What audience to target next
5. One sentence action plan for tomorrow

Return in bullet points."""
    return ask(prompt, system=SYSTEM_PERSONA)

def analyze_conversation(message_history):
    prompt = f"""Analyze this lead conversation history:

{message_history}

Extract and return ONLY a JSON object with these keys:
- "lead_temperature": "hot", "warm", or "cold"
- "budget": estimated budget or "unknown"
- "timeline": timeline or "unknown"
- "needs": what they need
- "objections": any objections
- "suggested_action": what to do next
- "meeting_suggested": true/false if we should meet them
- "phone_collected": true/false if we have their number
- "reply_draft": a friendly, professional reply to send them
"""
    result = ask(prompt, system=SYSTEM_PERSONA, temperature=0.3)
    try:
        # Extract JSON if wrapped in markdown
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        return json.loads(result.strip())
    except Exception:
        return {"lead_temperature": "warm", "reply_draft": result, "meeting_suggested": False}

def draft_outbound_message(lead_info, platform):
    prompt = f"""Draft a short, personalized outreach message for a lead.

Lead Info: {json.dumps(lead_info)}
Platform: {platform}
Agency: {AGENCY_NAME} in {AGENCY_LOCATION}
Services: {AGENCY_SERVICES}

Rules:
- Max 2-3 sentences
- Mention their business specifically if known
- Soft pitch, not pushy
- Ask one question to start a conversation
- Include a CTA to reply or DM
"""
    return ask(prompt, system=SYSTEM_PERSONA)

def generate_cold_call_script(lead_info):
    prompt = f"""Write a 30-second cold call script for this lead:

{json.dumps(lead_info)}

Agency: {AGENCY_NAME} in {AGENCY_LOCATION}
Services: {AGENCY_SERVICES}

Include: Hook, Problem, Solution, CTA. Keep it under 80 words."""
    return ask(prompt, system=SYSTEM_PERSONA)

def generate_weekly_report(ad_data, lead_stats):
    prompt = f"""Generate a weekly sales report for the CEO.

Ad Data: {json.dumps(ad_data)}
Lead Stats: {json.dumps(lead_stats)}

Format:
## Wins This Week
## Problems
## What to Do Next Week
## Hot Leads to Meet
## Ad Budget Recommendation
"""
    return ask(prompt, system=SYSTEM_PERSONA)
