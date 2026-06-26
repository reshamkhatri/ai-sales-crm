import requests
import pandas as pd
from datetime import datetime, timedelta
from database import db
from config import META_ACCESS_TOKEN, META_AD_ACCOUNT_ID

BASE_URL = "https://graph.facebook.com/v18.0"

def get_insights(days=7):
    """Pull ad insights from Meta Graph API"""
    if not META_ACCESS_TOKEN or not META_AD_ACCOUNT_ID:
        return []
    
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "fields": "campaign_name,adset_name,ad_name,spend,impressions,clicks,ctr,cpm,cpc,actions,cost_per_action_type",
        "time_range": f"{{'since':'{since}','until':'{until}'}}",
        "level": "ad",
    }
    
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"Meta API error: {resp.text}")
        return []
    
    data = resp.json().get("data", [])
    
    # Transform and store
    for row in data:
        # Extract lead count from actions
        leads = 0
        messaging = 0
        for action in row.get("actions", []):
            if action["action_type"] == "lead":
                leads = int(action["value"])
            if action["action_type"] == "onsite_conversion.messaging_conversation_started":
                messaging = int(action["value"])
        
        # Find or create campaign
        campaign = db.fetchone("SELECT id FROM ad_campaigns WHERE meta_ad_id = ?", (row.get("ad_id", "unknown"),))
        if not campaign:
            campaign_id = db.execute(
                "INSERT INTO ad_campaigns (meta_campaign_id, meta_adset_id, meta_ad_id, name, objective) VALUES (?, ?, ?, ?, ?)",
                (row.get("campaign_id"), row.get("adset_id"), row.get("ad_id"), row.get("ad_name", "Unknown"), "MESSAGES")
            )
        else:
            campaign_id = campaign["id"]
        
        # Store insight
        db.execute(
            """INSERT INTO ad_insights 
            (campaign_id, date, spend, impressions, clicks, ctr, cpm, cpc, leads, messaging_conversations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (campaign_id, until, float(row.get("spend", 0)), int(row.get("impressions", 0)),
             int(row.get("clicks", 0)), float(row.get("ctr", 0)), float(row.get("cpm", 0)),
             float(row.get("cpc", 0)), leads, messaging)
        )
    
    return data

def get_ad_summary(days=7):
    """Get aggregated ad performance for AI analysis"""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = db.fetchall("""
        SELECT c.name, c.meta_ad_id, SUM(i.spend) as total_spend, SUM(i.impressions) as total_impressions,
               SUM(i.clicks) as total_clicks, AVG(i.ctr) as avg_ctr, SUM(i.leads) as total_leads,
               SUM(i.messaging_conversations) as total_messages
        FROM ad_insights i
        JOIN ad_campaigns c ON i.campaign_id = c.id
        WHERE i.date >= ?
        GROUP BY c.id
    """, (since,))
    return rows

def get_best_performing_ad(days=7):
    """Return the ad with lowest cost per lead or most messages"""
    summary = get_ad_summary(days)
    if not summary:
        return None
    
    # Score by leads per dollar spent
    best = None
    best_score = -1
    for ad in summary:
        spend = ad["total_spend"] or 0.01
        leads = ad["total_leads"] or ad["total_messages"] or 0
        score = leads / spend
        if score > best_score:
            best_score = score
            best = ad
    return best

def get_ad_decision_summary(days=7):
    """Return dashboard-ready Meta ads intelligence with plain action labels."""
    ads = get_ad_summary(days)
    if not ads:
        return {
            "has_data": False,
            "days": days,
            "total_spend": 0,
            "total_clicks": 0,
            "total_leads": 0,
            "total_messages": 0,
            "cost_per_result": None,
            "best": None,
            "worst": None,
            "ads": [],
            "recommendation": "Connect Meta Ads or pull insights to see what is working, what is wasting money, and what to do next."
        }

    enriched = []
    total_spend = 0
    total_clicks = 0
    total_leads = 0
    total_messages = 0

    for ad in ads:
        spend = float(ad.get("total_spend") or 0)
        clicks = int(ad.get("total_clicks") or 0)
        leads = int(ad.get("total_leads") or 0)
        messages = int(ad.get("total_messages") or 0)
        results = leads + messages
        cost_per_result = spend / results if results else None
        ctr = float(ad.get("avg_ctr") or 0)

        if results >= 3 and cost_per_result is not None and cost_per_result <= 25:
            action = "Scale"
            reason = "Good result volume at a healthy cost."
        elif spend >= 50 and results == 0:
            action = "Kill"
            reason = "Spend is accumulating with no tracked leads or messages."
        elif spend >= 50 and cost_per_result and cost_per_result >= 75:
            action = "Cut"
            reason = "Cost per result is too high."
        elif ctr < 0.8 and spend >= 20:
            action = "Refresh Creative"
            reason = "Low CTR suggests the hook or creative is weak."
        else:
            action = "Watch"
            reason = "Needs more data before a strong decision."

        total_spend += spend
        total_clicks += clicks
        total_leads += leads
        total_messages += messages

        enriched.append({
            **ad,
            "results": results,
            "cost_per_result": cost_per_result,
            "action": action,
            "reason": reason,
        })

    def score(ad):
        if ad["results"] <= 0:
            return -999999 + float(ad.get("total_spend") or 0) * -1
        return ad["results"] / max(float(ad.get("total_spend") or 0), 0.01)

    best = max(enriched, key=score)
    worst = min(enriched, key=score)
    total_results = total_leads + total_messages
    overall_cpr = total_spend / total_results if total_results else None

    if best and best["results"] > 0:
        recommendation = f"Best ad is '{best['name']}' with {best['results']} results. Action: {best['action']}."
    else:
        recommendation = "No ad has produced a tracked lead or message yet. Check tracking first, then refresh creative."

    if worst and worst != best:
        recommendation += f" Weakest ad is '{worst['name']}'. Action: {worst['action']}."

    return {
        "has_data": True,
        "days": days,
        "total_spend": total_spend,
        "total_clicks": total_clicks,
        "total_leads": total_leads,
        "total_messages": total_messages,
        "cost_per_result": overall_cpr,
        "best": best,
        "worst": worst,
        "ads": sorted(enriched, key=score, reverse=True),
        "recommendation": recommendation,
    }
