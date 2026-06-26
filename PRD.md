# Product Requirements Document (PRD)

## AI Sales Assistant — Multi-Channel Smart Sales & Business Intelligence Platform

**Version:** 1.0
**Date:** 2026
**Author:** Product Team
**Status:** Draft → Ready for Development

---

## 1. Executive Summary

### 1.1 Product Vision
Build an AI-powered sales assistant that acts as a virtual Sales Director and Business Intelligence analyst for a Dubai-based web design agency. The system ingests conversations from all customer-facing channels, analyzes them with AI, scores leads, suggests actions, manages ad performance, and outputs actionable intelligence — all for under $10/month.

### 1.2 Problem Statement
The agency currently struggles with:
- **Scattered leads** across WhatsApp, Instagram, Facebook, email, and phone — no central tracking
- **No lead scoring** — cannot distinguish hot prospects from time-wasters
- **Manual ad management** — no data-driven decisions on which ads to kill or scale
- **Missed follow-ups** — conversations get lost, leads go cold
- **No sales intelligence** — the owner/CEO has no visibility into what's working
- **Inconsistent outreach** — no system for cold calls, LinkedIn messages, or email sequences
- **Botim dependency** — no way to automate the UAE's most popular messaging app

### 1.3 Solution
A unified AI-powered platform that:
- **Auto-replies** to incoming messages on WhatsApp, Instagram, Facebook, Email, and Telegram
- **Extracts** budget, timeline, and needs from every conversation automatically
- **Scores** every lead 0-100 based on engagement, information completeness, and AI signals
- **Suggests** physical meetings for hot leads (70+ score) with location and timing
- **Analyzes** Meta ad performance daily and recommends kill/scale/test actions
- **Drafts** outbound messages for LinkedIn, Email, and cold calls (human sends)
- **Tracks** every touchpoint in a central CRM accessible from a web dashboard
- **Costs** $3–$8/month to operate

### 1.4 Target Market
Dubai-based web design agency targeting small-to-medium businesses (restaurants, clinics, real estate, salons, e-commerce) in the UAE.

### 1.5 Business Value
- Reduce lead response time from hours to seconds
- Increase lead-to-meeting conversion by 2-3x through AI-driven scoring
- Reduce ad waste by 30-50% through data-driven recommendations
- Eliminate manual CRM data entry
- Give the CEO a single source of truth for all sales activity

---

## 2. Target Users & Personas

### 2.1 Primary User: The CEO / Founder
**Name:** Ahmed
**Role:** Founder & CEO of the web design agency
**Goals:**
- See which leads are hot and need a meeting TODAY
- Know which ads are working and which are burning money
- Understand what his sales team is doing without micromanaging
- Make data-driven decisions about where to invest marketing budget
- Never lose track of a conversation with a potential client

**Pain Points:**
- Checking 5 different apps (WhatsApp, IG, FB, Email, phone) to find conversations
- No idea which of his 50 open leads are actually going to buy
- His sales assistant forgets to follow up
- Ads are running but he doesn't know ROI
- Sometimes he meets a client who already said "no" to his assistant — embarrassing

**How the product helps:**
- Single dashboard showing all hot leads, meetings, and ad performance
- Daily AI report: "Today, meet 3 people. Kill Ad B. Your assistant called 5 leads."
- Complete conversation history for every lead before every meeting

### 2.2 Secondary User: The Sales Assistant
**Name:** Fatima
**Role:** Sales Assistant / Cold Caller
**Goals:**
- Know exactly who to call and what to say
- Log call outcomes so the AI can update lead scores
- See which leads are hot and pass them to the CEO immediately
- Track her daily activity

**Pain Points:**
- Calling random leads with no context
- No script — winging it every call
- Leads tell her "I already talked to someone" — duplicate outreach
- No system to know if a lead was already called today

**How the product helps:**
- AI-generated call scripts personalized to each lead
- Call list sorted by lead score (call hot leads first)
- All previous conversations visible before every call
- One-click log of call outcome (answered, voicemail, callback, not interested)

### 2.3 Tertiary User: Marketing / Ad Manager
**Name:** Karim
**Role:** Runs Meta ads (Facebook, Instagram)
**Goals:**
- Know which ad creative is winning
- Get suggestions for new ad angles to test
- Understand cost per lead by campaign
- Optimize budget allocation

**Pain Points:**
- Meta Ads Manager is overwhelming
- Doesn't know if "Ad A" or "Ad B" is actually getting more clients
- Spends AED 500/day with no clear ROI
- Tests random creatives without a system

**How the product helps:**
- Daily AI analysis: "Ad A got 5 leads for $10, Ad B got 1 for $50. Kill B, scale A."
- Plain English recommendations, not spreadsheet numbers
- Suggested new creatives based on what converted

---

## 3. Product Goals & Objectives

### 3.1 Primary Goals (Must Have for V1)

| # | Goal | Success Metric | Timeline |
|---|------|---------------|----------|
| G1 | Auto-reply to incoming WhatsApp messages with AI | < 5 second response time | Week 2 |
| G2 | Extract lead data (budget, timeline, needs) from conversations | > 80% extraction accuracy | Week 3 |
| G3 | Score every lead 0-100 automatically | Hot leads (70+) flagged correctly | Week 4 |
| G4 | Suggest meetings for hot leads | CEO sees "Meet This Client" daily | Week 4 |
| G5 | Pull Meta ad data and recommend actions | Daily AI report generated | Week 5 |
| G6 | Central dashboard showing all leads, scores, meetings, ads | Single page, loads in < 2s | Week 5 |
| G7 | Store every conversation from all channels in one CRM | Zero data loss | Week 1 |
| G8 | Generate cold call list with AI scripts | CSV export + personalized scripts | Week 6 |

### 3.2 Secondary Goals (Should Have for V1)

| # | Goal | Success Metric | Timeline |
|---|------|---------------|----------|
| G9 | Auto-reply to Instagram DMs | Same as WhatsApp | Week 3 |
| G10 | Monitor Gmail and draft replies | 15-minute polling, auto-detect | Week 4 |
| G11 | Draft outbound messages for LinkedIn, Email, X | 5 drafts/day generated | Week 6 |
| G12 | Multi-channel lead tracking (same person on WhatsApp + Email) | Deduplication rate > 95% | Week 3 |

### 3.3 Tertiary Goals (Could Have for V2)

| # | Goal | Timeline |
|---|------|----------|
| G13 | Auto-send WhatsApp template messages after 24h | V2 |
| G14 | Auto-adjust Meta ad budget based on AI recommendations | V2 |
| G15 | Google Calendar integration for auto-meeting creation | V2 |
| G16 | Arabic language support for conversations | V2 |
| G17 | Voice call integration (Twilio) | V3 |
| G18 | Mobile app for sales team | V3 |

---

## 4. User Stories & Use Cases

### 4.1 Use Case 1: WhatsApp Lead Auto-Capture & Reply

**Actor:** Potential client (restaurant owner in Dubai)
**Trigger:** Client sees Facebook Ad, clicks "Message on WhatsApp"

**Flow:**
1. Client sends "Hi, I need a website for my restaurant"
2. System receives WhatsApp webhook
3. Unified Inbox creates a new lead: source=whatsapp, phone=+97155...
4. AI analyzes: "Need: restaurant website. No budget mentioned. Timeline: unknown. Temperature: warm."
5. AI drafts reply: "Hi! We'd love to help with your restaurant website. What's your budget range, and do you need online ordering?"
6. System sends reply via WhatsApp Cloud API (< 3 seconds)
7. Lead score updated to 45 (warm, no budget yet)
8. Conversation stored in messages table
9. Dashboard shows: "New lead: Restaurant owner, WhatsApp, Score: 45, Warm"

**Expected Result:** Lead engaged instantly, qualifying question asked, data captured for follow-up.

### 4.2 Use Case 2: Hot Lead Meeting Suggestion

**Actor:** CEO (Ahmed)
**Trigger:** Lead replies with budget and timeline

**Flow:**
1. Lead replies: "AED 8,000 budget, need it in 2 weeks, we're in Dubai Marina"
2. AI extracts: budget=AED 8,000, timeline=2 weeks, location=Dubai Marina
3. AI analysis: "Hot lead. Budget confirmed. Timeline urgent. Suggest meeting."
4. Lead score jumps to 85 (hot)
5. System auto-creates meeting suggestion: +2 days, location=Dubai Marina
6. Dashboard shows: "🔥 HOT LEAD — Restaurant, Dubai Marina, AED 8K, Meet in 2 days"
7. CEO sees it, clicks "Confirm Meeting", physically meets the client
8. Meeting outcome logged: "Won — AED 8,000 project, signed"
9. Lead status updated to "won"

**Expected Result:** CEO never misses a hot lead. AI does the filtering. CEO only meets qualified prospects.

### 4.3 Use Case 3: Ad Performance Analysis

**Actor:** Marketing manager (Karim)
**Trigger:** Daily 9 AM cron job

**Flow:**
1. System pulls last 7 days of ad data from Meta Graph API
2. Stores daily snapshots in ad_insights table
3. Aggregates: Campaign A spent $200, got 8 leads. Campaign B spent $300, got 2 leads.
4. AI analyzes: "Campaign A: $25/lead, 5x better than Campaign B. Campaign B: $150/lead, kill it."
5. AI suggests: "Scale Campaign A by 50%. Kill Campaign B. Test a new ad with restaurant imagery since that converted."
6. Recommendation saved to ai_recommendations table
7. Dashboard shows: "🎯 AI Recommendation: Scale Ad A, Kill Ad B, Test C"
8. Karim updates Meta Ads Manager accordingly

**Expected Result:** Data-driven ad decisions, reduced waste, higher ROI.

### 4.4 Use Case 4: Cold Call Preparation

**Actor:** Sales assistant (Fatima)
**Trigger:** CEO asks for call list on Monday morning

**Flow:**
1. Fatima opens dashboard, clicks "Call List"
2. System queries: all leads with phone, score > 50, not called in last 7 days
3. Returns 12 leads sorted by score (highest first)
4. For each lead, AI generates 30-second script:
   - "Hi [Name], you messaged us about a website for [Business]. We build restaurant websites in Dubai. Can we schedule 15 minutes to discuss your needs?"
5. Fatima exports to CSV, prints call sheet
6. Calls first lead: "Hi Rami, you messaged us about a website for your café..."
7. Logs outcome: "Answered — interested, wants meeting next Tuesday"
8. System updates lead score to 75 and suggests meeting for Tuesday

**Expected Result:** Fatima has context, script, and purpose for every call. No more winging it.

### 4.5 Use Case 5: Email Monitoring & Proposal

**Actor:** CEO (Ahmed)
**Trigger:** Client sends email: "Can you send me a proposal for an e-commerce website?"

**Flow:**
1. Client sends email to agency@gmail.com
2. System checks Gmail IMAP (every 15 min), detects new email
3. Creates lead from email: name, email, subject parsed
4. AI analyzes: "Request: e-commerce proposal. Temperature: warm. Needs: online store."
5. AI drafts reply: "Thanks for your interest! We specialize in e-commerce sites. Could you share your product catalog size and preferred payment gateway? This will help us tailor the proposal."
6. Reply saved to outbound_drafts (not auto-sent — Ahmed reviews first)
7. Ahmed reviews, edits, clicks "Send Proposal"
8. System sends email via SMTP with proposal attached
9. Lead status updated to "proposal sent"

**Expected Result:** No email slips through the cracks. AI drafts, human approves, sent with tracking.

### 4.6 Use Case 6: Multi-Channel Lead Tracking

**Actor:** Same lead contacts on multiple channels
**Trigger:** Lead messages on WhatsApp, then emails, then DMs on Instagram

**Flow:**
1. Lead messages on WhatsApp → lead created, phone=+97155...
2. Same person sends email → system matches by name/email, finds existing lead
3. Does NOT create duplicate. Links email to same lead_id.
4. AI sees both conversations: "This person is serious — contacted us on 3 channels."
5. Lead score increases due to multi-channel engagement
6. Dashboard shows all messages in one timeline: WhatsApp → Email → Instagram

**Expected Result:** No duplicate leads. Complete customer history across all channels.

---

## 5. Functional Requirements

### 5.1 Channel Integration (FR-1xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-101 | Receive WhatsApp messages via Meta Cloud API webhook | P0 | ✅ Built |
| FR-102 | Send WhatsApp replies within 24h conversation window (free-form) | P0 | ✅ Built |
| FR-103 | Send WhatsApp template messages after 24h window | P1 | ✅ Built |
| FR-104 | Receive Instagram DMs via Meta Graph API webhook | P1 | ✅ Built |
| FR-105 | Send Instagram DM replies | P1 | ✅ Built |
| FR-106 | Receive Facebook Messenger messages via webhook | P0 | ✅ Built |
| FR-107 | Send Facebook Messenger replies | P0 | ✅ Built |
| FR-108 | Monitor Gmail inbox via IMAP (every 15 min) | P1 | ✅ Built |
| FR-109 | Send emails via Gmail SMTP | P1 | ✅ Built |
| FR-110 | Receive Telegram messages via bot webhook | P2 | ✅ Built |
| FR-111 | Send Telegram messages | P2 | ✅ Built |
| FR-112 | Manual entry for Botim conversations (no API) | P2 | ✅ Built |
| FR-113 | Manual entry for LinkedIn conversations (no API) | P2 | ✅ Built |
| FR-114 | Manual entry for X/Twitter conversations (no API) | P2 | ✅ Built |

### 5.2 AI Processing (FR-2xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-201 | Analyze every incoming conversation with AI (OpenAI) | P0 | ✅ Built |
| FR-202 | Extract lead data: budget, timeline, needs, objections | P0 | ✅ Built |
| FR-203 | Classify lead temperature: hot, warm, cold | P0 | ✅ Built |
| FR-204 | Generate contextual reply for every incoming message | P0 | ✅ Built |
| FR-205 | Suggest meetings for hot leads (score >= 70) | P0 | ✅ Built |
| FR-206 | Detect if phone number is collected in conversation | P1 | ✅ Built |
| FR-207 | Analyze ad performance data and recommend actions | P1 | ✅ Built |
| FR-208 | Generate weekly sales report for CEO | P1 | ✅ Built |
| FR-209 | Draft outbound messages for LinkedIn, Email, X | P1 | ✅ Built |
| FR-210 | Generate cold call scripts (30 seconds, personalized) | P1 | ✅ Built |
| FR-211 | Support Arabic language conversations (V2) | P2 | Planned |
| FR-212 | Fine-tune AI on agency's past conversations (V3) | P3 | Planned |

### 5.3 Lead Management (FR-3xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-301 | Create lead automatically from any incoming message | P0 | ✅ Built |
| FR-302 | Deduplicate leads across channels (phone, email, name) | P0 | ✅ Built |
| FR-303 | Score leads 0-100 based on multi-factor algorithm | P0 | ✅ Built |
| FR-304 | Update lead status: new, contacted, qualified, proposal, negotiation, won, lost | P0 | ✅ Built |
| FR-305 | Store complete conversation history per lead | P0 | ✅ Built |
| FR-306 | Track lead source (WhatsApp, Instagram, Facebook, Email, Telegram, manual) | P0 | ✅ Built |
| FR-307 | Add manual notes to any lead | P0 | ✅ Built |
| FR-308 | Export leads to CSV | P1 | ✅ Built |
| FR-309 | Search leads by name, phone, email, business | P1 | Planned |
| FR-310 | Bulk update lead status | P2 | Planned |

### 5.4 Meeting Management (FR-4xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-401 | Auto-suggest meeting date (+2 days) for hot leads | P0 | ✅ Built |
| FR-402 | Store meeting location | P0 | ✅ Built |
| FR-403 | Log meeting outcome (scheduled, completed, no-show, rescheduled) | P0 | ✅ Built |
| FR-404 | Show today's meetings on dashboard | P0 | ✅ Built |
| FR-405 | Meeting reminders (V2) | P2 | Planned |
| FR-406 | Google Calendar integration (V2) | P2 | Planned |

### 5.5 Ad Management (FR-5xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-501 | Connect to Meta Graph API and pull ad data | P0 | ✅ Built |
| FR-502 | Store daily ad performance snapshots | P0 | ✅ Built |
| FR-503 | Aggregate metrics: spend, impressions, clicks, CTR, leads, cost per lead | P0 | ✅ Built |
| FR-504 | Identify best performing ad (highest leads per dollar) | P1 | ✅ Built |
| FR-505 | Identify worst performing ad (lowest conversion, highest spend) | P1 | ✅ Built |
| FR-506 | AI analysis with plain English recommendations | P1 | ✅ Built |
| FR-507 | Save recommendations to database for review | P1 | ✅ Built |
| FR-508 | Show ad performance on dashboard | P1 | ✅ Built |
| FR-509 | Auto-adjust ad budget (V2) | P2 | Planned |
| FR-510 | Suggest new ad creative concepts (V2) | P2 | Planned |

### 5.6 Outbound & Cold Calling (FR-6xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-601 | AI draft personalized LinkedIn connection message | P1 | ✅ Built |
| FR-602 | AI draft personalized cold email | P1 | ✅ Built |
| FR-603 | AI draft WhatsApp template message for re-engagement | P1 | ✅ Built |
| FR-604 | AI draft Instagram DM (for followers) | P1 | ✅ Built |
| FR-605 | AI generate cold call script (30 sec, personalized) | P1 | ✅ Built |
| FR-606 | Export call list to CSV (name, business, phone, score, script) | P1 | ✅ Built |
| FR-607 | Log cold call outcomes (answered, voicemail, callback, not interested) | P1 | ✅ Built |
| FR-608 | Track call history per lead | P1 | ✅ Built |
| FR-609 | Auto-send email sequences (V2) | P2 | Planned |
| FR-610 | Auto-send WhatsApp templates after 24h (V2) | P2 | Planned |

### 5.7 Dashboard & Reporting (FR-7xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-701 | Single-page dashboard showing all key metrics | P0 | ✅ Built |
| FR-702 | Hot leads section (score >= 70) | P0 | ✅ Built |
| FR-703 | Today's meetings section | P0 | ✅ Built |
| FR-704 | Recent leads section (last 20) | P0 | ✅ Built |
| FR-705 | AI recommendations section | P0 | ✅ Built |
| FR-706 | Channel status section | P1 | ✅ Built |
| FR-707 | Lead detail page with full conversation history | P1 | ✅ Built |
| FR-708 | Ad performance summary | P1 | ✅ Built |
| FR-709 | Call list view | P1 | ✅ Built |
| FR-710 | Lead count by channel | P1 | ✅ Built |
| FR-711 | Unread messages view | P1 | ✅ Built |
| FR-712 | Weekly email report to CEO (V2) | P2 | Planned |
| FR-713 | Mobile-responsive dashboard (V2) | P2 | Planned |

### 5.8 System & Automation (FR-8xx)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-801 | Daily 9 AM cron: pull ad data, analyze, save recommendation | P0 | ✅ Built |
| FR-802 | Every 15 min: check Gmail for new emails | P0 | ✅ Built |
| FR-803 | Auto-restart on crash (systemd) | P1 | ✅ Built |
| FR-804 | Daily database backup (3 AM) | P1 | ✅ Built |
| FR-805 | Log all errors to journal | P1 | ✅ Built |
| FR-806 | Webhook signature verification (security) | P0 | ✅ Built |
| FR-807 | API key management via .env file | P0 | ✅ Built |
| FR-808 | SQLite database with proper schema | P0 | ✅ Built |

---

## 6. Non-Functional Requirements

### 6.1 Performance (NFR-1xx)

| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| NFR-101 | WhatsApp auto-reply latency | < 5 seconds | Target |
| NFR-102 | Dashboard page load time | < 2 seconds | Target |
| NFR-103 | AI analysis response time | < 3 seconds | Target |
| NFR-104 | Email polling frequency | Every 15 minutes | Set |
| NFR-105 | Ad data pull frequency | Daily at 9 AM | Set |
| NFR-106 | Concurrent webhook handling | 10 simultaneous | Set |
| NFR-107 | Database query response time | < 100ms | Target |
| NFR-108 | System uptime | > 99% | Target |

### 6.2 Security (NFR-2xx)

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-201 | Webhook verification tokens (prevent spoofing) | ✅ Built |
| NFR-202 | API keys stored in environment variables (not code) | ✅ Built |
| NFR-203 | Gmail App Password (not main password) | ✅ Built |
| NFR-204 | HTTPS for production (Let's Encrypt) | Deployment |
| NFR-205 | Firewall: only 22, 80, 443 open | Deployment |
| NFR-206 | No PII logged in plain text | ✅ Built |
| NFR-207 | SQLite file permissions (readable only by app user) | Deployment |
| NFR-208 | Rate limiting on API endpoints (V2) | Planned |

### 6.3 Scalability (NFR-3xx)

| ID | Requirement | Current | Future |
|----|-------------|---------|--------|
| NFR-301 | Lead capacity | 100K (SQLite) | 1M+ (PostgreSQL) |
| NFR-302 | Message capacity | 1M (SQLite) | 10M+ (PostgreSQL) |
| NFR-303 | Daily AI analysis cost | $0.25 (50 leads) | $2.50 (500 leads) |
| NFR-304 | WhatsApp free tier | 1,000 conv/month | Unlimited (paid) |
| NFR-305 | Server resources | 1 GB RAM | 2 GB RAM (upgrade) |
| NFR-306 | Concurrent users | 5 | 50+ (Redis + workers) |

### 6.4 Reliability (NFR-4xx)

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-401 | Auto-restart on crash (systemd) | ✅ Built |
| NFR-402 | Daily database backups | ✅ Built |
| NFR-403 | Graceful degradation if AI API is down | Planned |
| NFR-404 | Graceful degradation if Meta API is down | Planned |
| NFR-405 | Retry failed webhook deliveries (3 attempts) | Planned |
| NFR-406 | Alert on system errors (V2) | Planned |

### 6.5 Usability (NFR-5xx)

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-501 | Dashboard works on mobile browser | Partial |
| NFR-502 | No coding required to use dashboard | ✅ Built |
| NFR-503 | Add lead manually in < 30 seconds | ✅ Built |
| NFR-504 | Export call list in < 10 seconds | ✅ Built |
| NFR-505 | AI recommendations in plain English | ✅ Built |
| NFR-506 | Zero technical knowledge for daily use | ✅ Built |

### 6.6 Maintainability (NFR-6xx)

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-601 | Modular code (each channel is a separate file) | ✅ Built |
| NFR-602 | One-line database swap (SQLite → PostgreSQL) | ✅ Built |
| NFR-603 | One-line AI model swap (OpenAI → Claude → local) | ✅ Built |
| NFR-604 | Environment-based configuration (no code changes) | ✅ Built |
| NFR-605 | Logging of all errors and warnings | ✅ Built |
| NFR-606 | Clear separation of concerns (router, brain, CRM, handlers) | ✅ Built |

---

## 7. Data Model

### 7.1 Entity Relationship Diagram

```
leads (1) ────< (*) messages
leads (1) ────< (*) meetings
leads (1) ────< (*) cold_calls
leads (1) ────< (*) outbound_drafts
ad_campaigns (1) ────< (*) ad_insights
ai_recommendations (standalone)
```

### 7.2 Lead Lifecycle States

```
new → contacted → qualified → proposal → negotiation → won
        ↓              ↓            ↓            ↓
       lost         lost         lost         lost
```

### 7.3 Lead Score Ranges

| Range | Label | Action |
|-------|-------|--------|
| 0-39 | Cold | Nurture or deprioritize |
| 40-69 | Warm | Follow up sequence |
| 70-100 | Hot | Suggest meeting immediately |

### 7.4 Data Retention

| Data Type | Retention | Action |
|-----------|-----------|--------|
| Lead records | Indefinite | Keep forever |
| Messages | Indefinite | Keep forever |
| Ad insights | 1 year | Archive after 1 year |
| AI recommendations | 90 days | Delete after 90 days |
| Cold call logs | 1 year | Archive after 1 year |
| Backups | 30 days | Delete old backups |

---

## 8. API Specifications

### 8.1 Webhook Endpoints (Inbound)

| Endpoint | Method | Description | Expected Body |
|----------|--------|-------------|---------------|
| `/api/webhook/facebook` | GET | Verification challenge | hub.mode, hub.verify_token, hub.challenge |
| `/api/webhook/facebook` | POST | Incoming message | Facebook Messenger JSON |
| `/api/webhook/whatsapp` | GET | Verification challenge | hub.mode, hub.verify_token, hub.challenge |
| `/api/webhook/whatsapp` | POST | Incoming message | WhatsApp Cloud API JSON |
| `/api/webhook/instagram` | GET | Verification challenge | hub.mode, hub.verify_token, hub.challenge |
| `/api/webhook/instagram` | POST | Incoming DM | Instagram Messaging JSON |
| `/api/webhook/telegram` | POST | Incoming message | Telegram Update JSON |

### 8.2 API Endpoints (CRUD & Actions)

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/leads` | GET | List all leads | None (local) |
| `/api/leads/{id}` | GET | Lead detail + messages | None |
| `/api/hot-leads` | GET | Leads with score >= 70 | None |
| `/api/leads/by-channel` | GET | Lead count per channel | None |
| `/api/leads/unread` | GET | Leads with unread messages | None |
| `/api/lead/add` | POST | Add lead manually | None |
| `/api/lead/{id}/score` | POST | Recalculate score | None |
| `/api/call-list` | GET | Call list with scripts | None |
| `/api/ads` | GET | Ad performance summary | None |
| `/api/ads/analyze` | POST | Trigger AI ad analysis | None |
| `/api/draft/{id}` | POST | Draft outbound message | None |
| `/api/email/check` | POST | Check Gmail manually | None |
| `/api/email/send-proposal/{id}` | POST | Send proposal email | None |
| `/api/whatsapp/send/{id}` | POST | Send WhatsApp to lead | None |
| `/api/instagram/send/{id}` | POST | Send Instagram DM | None |

### 8.3 Response Formats

**Standard Success:**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional human-readable message"
}
```

**Standard Error:**
```json
{
  "status": "error",
  "error": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

---

## 9. UI/UX Requirements

### 9.1 Dashboard Layout

```
┌──────────────────────────────────────────────────────┐
│  AI Sales Assistant — Dubai Web Design Agency         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ HOT LEADS    │  │ CHANNEL      │  │ TODAY'S  │  │
│  │ (Meet These) │  │ STATUS       │  │ MEETINGS │  │
│  │              │  │              │  │          │  │
│  │ Lead 1       │  │ WhatsApp ✅  │  │ Meeting 1│  │
│  │ Lead 2       │  │ Instagram ✅ │  │ Meeting 2│  │
│  │ Lead 3       │  │ Facebook ✅  │  │          │  │
│  └──────────────┘  │ Email ✅     │  └──────────┘  │
│                    │ Telegram ✅  │                 │
│  ┌──────────────┐  │ Botim ❌     │  ┌──────────┐  │
│  │ RECENT LEADS │  └──────────────┘  │ QUICK    │  │
│  │              │                    │ ACTIONS  │  │
│  │ Lead 1       │  ┌──────────────┐  │          │  │
│  │ Lead 2       │  │ AI RECS      │  │ Call List│  │
│  │ Lead 3       │  │              │  │ Hot Leads│  │
│  │ Lead 4       │  │ Rec 1        │  │ Analyze  │  │
│  │ Lead 5       │  │ Rec 2        │  │ Check    │  │
│  └──────────────┘  │ Rec 3        │  │ Email    │  │
│                    └──────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────┘
```

### 9.2 Color Coding

| Color | Meaning | Use |
|-------|---------|-----|
| 🔴 Red | Hot lead (score >= 70) | Score badge, alerts |
| 🟡 Yellow | Warm lead (score 40-69) | Score badge |
| ⚪ Gray | Cold lead (score < 40) | Score badge |
| 🟢 Green | Active channel | Status indicator |
| 🔴 Red | Inactive channel | Status indicator |
| 🟠 Orange | AI recommendation | Alert box |
| 🟣 Purple | Action button | Buttons |

### 9.3 Mobile Requirements (V2)
- Responsive dashboard (CSS media queries)
- Push notifications for hot leads
- Mobile-optimized call logging
- Voice-to-text for quick notes

---

## 10. Security & Compliance

### 10.1 Data Privacy (UAE / GDPR)
- Lead data stored locally (SQLite) — no cloud data sharing
- AI processing via OpenAI API — conversations processed but not stored by OpenAI
- No PII logged in application logs
- Right to deletion: can delete any lead record and all associated messages
- Consent: implicit via messaging the business (business account, not personal)

### 10.2 Meta Platform Policies
- WhatsApp: Follow 24-hour conversation window rule
- WhatsApp: Use only pre-approved templates for outbound after 24h
- Facebook/Instagram: No unsolicited messaging (only reply to inbound)
- All webhooks verify signature to prevent spoofing

### 10.3 Email Compliance
- Gmail App Password (not main password)
- Unsubscribe support for marketing emails (V2)
- No spam — only reply to inbound or send proposals to qualified leads

---

## 11. Success Metrics & KPIs

### 11.1 Product Metrics

| Metric | Baseline | Target (30 days) | Target (90 days) |
|--------|----------|-----------------|-----------------|
| Lead response time | 2-4 hours | < 5 seconds | < 3 seconds |
| Lead-to-meeting rate | 10% | 25% | 35% |
| Cost per lead (ads) | Unknown | Trackable | Optimized |
| Ad waste (low-performing) | 50% | 30% | 15% |
| Meetings missed | 20% | 5% | 2% |
| Cold call conversion | 5% | 15% | 20% |
| Follow-up completion | 30% | 80% | 95% |

### 11.2 System Metrics

| Metric | Target |
|--------|--------|
| System uptime | > 99% |
| WhatsApp reply latency | < 5 seconds |
| Dashboard load time | < 2 seconds |
| AI analysis accuracy | > 80% |
| Lead deduplication rate | > 95% |
| Database backup success | 100% |
| Zero data loss | 100% |

### 11.3 Business Metrics

| Metric | Target (6 months) |
|--------|-------------------|
| Revenue increase from better lead conversion | +50% |
| Ad spend reduction through optimization | -30% |
| Time saved on manual CRM entry | 10 hrs/week |
| Time saved on ad analysis | 5 hrs/week |
| Meetings scheduled per week | 10+ |
| Deals closed per month | 8+ |

---

## 12. Roadmap

### 12.1 Phase 1: Foundation (Weeks 1-2) — COMPLETE
- ✅ SQLite CRM with 7 tables
- ✅ Unified inbox router
- ✅ AI brain (OpenAI GPT-4o-mini)
- ✅ Facebook Messenger auto-reply
- ✅ Basic FastAPI dashboard
- ✅ Lead scoring algorithm
- ✅ Manual lead entry

### 12.2 Phase 2: Multi-Channel (Weeks 3-4) — COMPLETE
- ✅ WhatsApp Cloud API integration
- ✅ Instagram DM integration
- ✅ Gmail IMAP monitoring + SMTP
- ✅ Telegram bot integration
- ✅ Botim/LinkedIn/X manual entry
- ✅ Multi-channel lead deduplication
- ✅ Outbound message drafting
- ✅ Cold call script generation
- ✅ CSV export for call lists

### 12.3 Phase 3: Intelligence (Weeks 5-6) — COMPLETE
- ✅ Meta Graph API ad data pull
- ✅ Daily ad performance snapshots
- ✅ AI ad analysis (kill/scale/test)
- ✅ Meeting suggestion for hot leads
- ✅ Email proposal sending
- ✅ Channel status dashboard
- ✅ Weekly AI report generation
- ✅ Cron jobs (daily ads, 15-min email, weekly report)

### 12.4 Phase 4: Production (Weeks 7-8)
- [ ] Oracle Cloud Free Tier deployment
- [ ] Nginx reverse proxy setup
- [ ] Let's Encrypt SSL
- [ ] Systemd auto-restart service
- [ ] Daily database backup cron
- [ ] Firewall (UFW) configuration
- [ ] Webhook URL updates (Meta, Telegram)
- [ ] Production monitoring
- [ ] Load testing

### 12.5 Phase 5: Polish (Weeks 9-10)
- [ ] Mobile-responsive dashboard
- [ ] Search & filter leads
- [ ] Bulk actions (update status, export)
- [ ] Lead tags and categories
- [ ] Team user accounts (CEO, Sales Assistant, Marketer)
- [ ] Role-based access control
- [ ] In-app notifications for hot leads
- [ ] Dark mode

### 12.6 Phase 6: Scale (V2 — Months 3-6)
- [ ] Arabic language support
- [ ] WhatsApp Business API advanced (catalog, payments)
- [ ] Google Calendar integration (auto-meeting creation)
- [ ] Auto-send WhatsApp templates after 24h
- [ ] Email drip sequences (auto-follow-up)
- [ ] Meta Marketing API (auto-budget adjustment)
- [ ] PostgreSQL migration
- [ ] Redis caching layer
- [ ] Celery async task queue
- [ ] React/Vue frontend
- [ ] LangChain memory (AI remembers across sessions)
- [ ] Fine-tuned AI model on agency data
- [ ] Weekly email report to CEO
- [ ] Slack/Discord integration for alerts
- [ ] Google Analytics integration
- [ ] AI-generated ad creative suggestions
- [ ] Competitor ad analysis (V3)
- [ ] Voice call integration (Twilio) (V3)
- [ ] Mobile app (Flutter/React Native) (V3)
- [ ] Multi-tenant (white-label for other agencies) (V4)

---

## 13. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Meta API changes break webhooks | Medium | High | Modular channel code, easy to adapt |
| OpenAI API rate limits or price increases | Low | Medium | Can swap to Claude or local Llama |
| WhatsApp template approval rejected | Medium | Medium | Create multiple templates, follow Meta guidelines |
| Lead data loss (database corruption) | Low | Critical | Daily backups, SQLite is robust |
| Server goes down (Oracle Cloud) | Low | High | Systemd auto-restart, monitoring alerts |
| AI gives incorrect lead scores | Medium | Medium | Human review of hot leads, tune prompts |
| Too many leads overwhelm system | Low | Medium | SQLite handles 100K leads, upgrade path clear |
| Meta account banned for policy violation | Low | Critical | Follow platform rules, don't spam, only reply to inbound |
| Sales team doesn't adopt the tool | Medium | High | Simple dashboard, no training needed, show value immediately |
| Competitor copies the system | Medium | Low | Open source architecture, differentiation is execution |

---

## 14. Open Questions & Decisions

| # | Question | Decision Needed By | Status |
|---|----------|-------------------|--------|
| Q1 | Do we want Arabic language support in V1? | Week 8 | Defer to V2 |
| Q2 | Should we auto-send emails or require approval? | Week 5 | Draft first, auto-send toggle |
| Q3 | Do we need team accounts (CEO, sales, marketer)? | Week 8 | Defer to V2 |
| Q4 | Should we integrate with existing CRM (HubSpot, Pipedrive)? | Week 6 | Not needed — built-in CRM is sufficient |
| Q5 | Do we want to sell this to other agencies? | Month 3 | Possible V4 white-label |
| Q6 | Should we add payment collection (Stripe, PayPal)? | Month 3 | Not needed for sales tool |
| Q7 | Do we need invoice generation? | Month 3 | Separate accounting tool |
| Q8 | Should we track competitor ads? | Month 6 | V3 feature |
| Q9 | Do we want SMS support (Twilio)? | Month 6 | V3 feature |
| Q10 | Should we add AI voice calls? | Month 6 | V3 feature |

---

## 15. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Unified Inbox** | Single router that processes messages from all channels into one system |
| **Lead Score** | 0-100 rating of lead quality based on data completeness, engagement, and AI signals |
| **Hot Lead** | Lead with score >= 70, suggesting immediate meeting |
| **24h Window** | Meta's rule: free-form WhatsApp replies only within 24h of user message |
| **Template Message** | Pre-approved WhatsApp message for use after the 24h window |
| **Webhook** | HTTP callback from Meta/Telegram to our server when a message arrives |
| **CRM** | Customer Relationship Management — database of leads and conversations |
| **Cost Per Lead** | Total ad spend divided by number of leads generated |
| **CTR** | Click-through rate — clicks / impressions |
| **IMAP** | Internet Message Access Protocol — reads emails from Gmail |
| **SMTP** | Simple Mail Transfer Protocol — sends emails from Gmail |
| **Systemd** | Linux service manager — auto-starts and restarts the app |
| **Nginx** | Web server and reverse proxy — handles HTTPS and routes to FastAPI |

### Appendix B: Technology Stack

| Layer | Technology | Version | Cost |
|-------|-----------|---------|------|
| Language | Python | 3.11+ | Free |
| Web Framework | FastAPI | 0.110+ | Free |
| Database | SQLite | 3.40+ | Free |
| AI Model | OpenAI GPT-4o-mini | Latest | $3-8/mo |
| Scheduler | APScheduler | 3.10+ | Free |
| Templating | Jinja2 | 3.1+ | Free |
| Server | Uvicorn | 0.29+ | Free |
| Reverse Proxy | Nginx | 1.24+ | Free |
| SSL | Let's Encrypt | Latest | Free |
| OS | Ubuntu | 22.04 LTS | Free |
| Cloud | Oracle Cloud Free Tier | Always Free | Free |
| API Client | requests / httpx | Latest | Free |
| Environment | python-dotenv | 1.0+ | Free |

### Appendix C: Meta API Permissions Required

| Platform | Permission | Purpose |
|----------|-----------|---------|
| Facebook | `pages_messaging` | Read/send Messenger messages |
| Facebook | `pages_read_engagement` | Read page insights |
| Facebook | `ads_read` | Read ad account data |
| Instagram | `instagram_basic` | Read Instagram profile |
| Instagram | `instagram_messaging` | Read/send DMs |
| WhatsApp | `whatsapp_business_management` | Manage WhatsApp business |
| WhatsApp | `whatsapp_business_messaging` | Send/receive messages |

### Appendix D: Environment Variables Reference

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | YES | `sk-...` | OpenAI API key |
| `OPENAI_MODEL` | NO | `gpt-4o-mini` | AI model to use |
| `META_ACCESS_TOKEN` | YES | `EAA...` | Meta Page access token |
| `META_AD_ACCOUNT_ID` | YES | `act_123...` | Meta ad account ID |
| `META_PAGE_ID` | YES | `123...` | Facebook Page ID |
| `META_VERIFY_TOKEN` | YES | `fb_webhook_123` | Webhook verification token |
| `META_APP_SECRET` | YES | `abc...` | Meta App secret |
| `META_INSTAGRAM_ID` | NO | `123...` | Instagram Business ID |
| `WHATSAPP_PHONE_NUMBER_ID` | YES | `123...` | WhatsApp phone number ID |
| `WHATSAPP_ACCESS_TOKEN` | YES | `EAA...` | WhatsApp API token |
| `WHATSAPP_VERIFY_TOKEN` | YES | `wa_webhook_123` | WhatsApp webhook token |
| `EMAIL_ADDRESS` | YES | `you@gmail.com` | Gmail address |
| `EMAIL_PASSWORD` | YES | `xxxx...` | Gmail App Password |
| `EMAIL_IMAP_SERVER` | NO | `imap.gmail.com` | IMAP server |
| `EMAIL_SMTP_SERVER` | NO | `smtp.gmail.com` | SMTP server |
| `EMAIL_SMTP_PORT` | NO | `587` | SMTP port |
| `TELEGRAM_BOT_TOKEN` | NO | `123...` | Telegram bot token |
| `ACTIVE_CHANNELS` | NO | `facebook,whatsapp,...` | Enabled channels |
| `DATABASE_PATH` | NO | `database/...` | SQLite file path |
| `DASHBOARD_HOST` | NO | `0.0.0.0` | Server bind address |
| `DASHBOARD_PORT` | NO | `8000` | Server port |
| `AGENCY_NAME` | NO | `Your Agency` | Display name |
| `AGENCY_SERVICES` | NO | `Web Design...` | Service list |
| `AGENCY_LOCATION` | NO | `Dubai, UAE` | Location |

---

## 16. Approval & Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| CEO / Founder | | | |
| Lead Developer | | | |
| QA / Testing | | | |

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026 | AI Assistant | Initial PRD creation |
| 1.1 | | | |

---

*End of Product Requirements Document*
