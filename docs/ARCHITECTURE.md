# AI Sales Assistant — System Architecture

## Overview
A unified, multi-channel AI sales & business assistant for a Dubai web design agency. It ingests messages from 6+ channels, processes them through a single AI brain, stores everything in a central CRM, and surfaces actionable insights (lead scores, meeting suggestions, ad performance, call lists) via a web dashboard.

## Design Principles
1. **Unified Inbox** — One router handles all channels, one AI brain processes all conversations.
2. **Event-Driven** — Webhooks for real-time, cron jobs for polling, all feeding the same pipeline.
3. **SQLite-First** — Single-file database, zero infra cost, easy to backup and migrate.
4. **$10 Budget** — Every component must be free or near-free at startup scale.
5. **Inbound-First** — Auto-reply to people who message YOU. Outbound is AI-drafted, human-sent (except Email).

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            EXTERNAL CHANNELS                                 │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬────────┤
│  WhatsApp   │  Instagram  │  Facebook   │   Email     │  Telegram   │ Botim  │
│   (Meta)    │   (Meta)    │   (Meta)    │  (Gmail)    │   (Bot)     │(Manual)│
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴────┬───┘
       │             │             │             │             │           │
       │  Webhook    │  Webhook    │  Webhook    │  IMAP Poll  │ Webhook   │ Paste
       │  (POST)     │  (POST)     │  (POST)     │  (15 min)   │ (POST)    │ (Manual)
       └─────────────┴─────────────┴──────┬──────┴─────────────┴───────────┘
                                          │
                     ┌────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         UNIFIED INBOX ROUTER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  WhatsApp   │  │  Instagram  │  │  Facebook   │  │   Email     │   │
│  │  Handler    │  │  Handler    │  │  Handler    │  │  Handler    │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │                │            │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐    │
│  │                    Normalize & Enrich                          │    │
│  │  Extract: sender_id, name, phone, email, text, timestamp     │    │
│  │  Lookup: existing lead by phone/email/external_id              │    │
│  │  Create: new lead if not found                                 │    │
│  └────────────────────────────────────────┬───────────────────────┘    │
└───────────────────────────────────────────┼──────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              AI BRAIN (OpenAI)                           │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  System Prompt: "You are the AI Sales Director for a Dubai web    │    │
│  │  design agency. Be concise, professional, and actionable."       │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Conversation│  │   Lead      │  │   Outbound  │  │   Ad        │    │
│  │  Analysis   │  │  Extraction │  │  Drafting   │  │  Analysis   │    │
│  │             │  │             │  │             │  │             │    │
│  │ Temperature │  │ Budget      │  │ LinkedIn    │  │ Kill/Scale  │    │
│  │ Budget      │  │ Timeline    │  │ Email       │  │ Creative    │    │
│  │ Timeline    │  │ Business    │  │ WhatsApp    │  │ Audience    │    │
│  │ Needs       │  │ Type        │  │ Template    │  │ Budget      │    │
│  │ Objections  │  │ Phone       │  │             │  │             │    │
│  │ Reply Draft │  │ Email       │  │             │  │             │    │
│  │ Meeting?    │  │             │  │             │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────┬───────────────────────────────┘
                                            │
                            ┌───────────────┼───────────────┐
                            ▼               ▼               ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐
│      CRM (SQLite)    │  │    DASHBOARD (FastAPI)│  │  CRON JOBS        │
│  ┌────────────────┐  │  │  ┌────────────────┐   │  │  ┌──────────────┐  │
│  │  leads         │  │  │  │  Hot Leads     │   │  │  │  Daily Ad    │  │
│  │  messages      │  │  │  │  Meetings      │   │  │  │  Pull 9 AM   │  │
│  │  ad_campaigns  │  │  │  │  Call Lists    │   │  │  │  Email Check │  │
│  │  ad_insights   │  │  │  │  Ad Performance│   │  │  │  15 min      │  │
│  │  ai_recs       │  │  │  │  AI Reports    │   │  │  │  Weekly      │  │
│  │  meetings      │  │  │  │  Channel Status│   │  │  │  Report      │  │
│  │  cold_calls    │  │  │  │  Lead Details  │   │  │  └──────────────┘  │
│  │  outbound      │  │  │  └────────────────┘   │  │                   │
│  └────────────────┘  │  └──────────────────────┘  └────────────────────┘
└──────────────────────┘
```

---

## Component Diagram

### 1. Channel Adapters (Inbound)
| Component | Input | Output | Trigger | Auth |
|-----------|-------|--------|---------|------|
| `whatsapp.py` | Webhook JSON from Meta | lead_id, reply, analysis | POST to `/api/webhook/whatsapp` | WhatsApp Cloud API token |
| `instagram.py` | Webhook JSON from Meta | lead_id, reply, analysis | POST to `/api/webhook/instagram` | Meta Graph API token |
| `messenger.py` | Webhook JSON from Meta | lead_id, reply, analysis | POST to `/api/webhook/facebook` | Meta Graph API token |
| `email_handler.py` | Gmail IMAP fetch | lead_id, reply draft, analysis | Cron every 15 min | Gmail App Password |
| `telegram.py` | Webhook JSON from Telegram | lead_id, reply, analysis | POST to `/api/webhook/telegram` | Telegram Bot Token |
| Manual entry | Copy-paste from Botim/LinkedIn/X | lead_id, analysis | Dashboard form | None |

### 2. Unified Inbox Router
**File:** `core/unified_inbox.py`
**Responsibility:** One function `handle_incoming_message()` that ALL channel adapters call. It:
1. Deduplicates leads (lookup by phone/email/external_id)
2. Creates new leads if not found
3. Logs every message to the CRM
4. Fetches last 10 messages as context
5. Calls the AI brain
6. Updates lead score and status
7. Suggests meetings if hot
8. Returns reply + analysis to the channel adapter

**Why this matters:** Without a unified router, each channel would have its own lead creation logic, leading to duplicate leads and inconsistent scoring. One router = one source of truth.

### 3. AI Brain (OpenAI GPT-4o-mini)
**File:** `core/ai_brain.py`
**Responsibility:** Pure prompt engineering. No business logic. Receives conversation history and returns structured analysis.

**Prompt Design:**
```
System: You are the AI Sales Director for [Agency Name], a Dubai web design agency.
       Services: Web Design, Landing Pages, SEO, E-commerce.
       Be concise, direct, and actionable. Speak like a Dubai business professional.

User: Analyze this conversation history and return ONLY JSON with:
  - lead_temperature: hot/warm/cold
  - budget: estimated or unknown
  - timeline: estimated or unknown
  - needs: what they need
  - objections: any objections
  - suggested_action: what to do next
  - meeting_suggested: true/false
  - phone_collected: true/false
  - reply_draft: a friendly, professional reply to send
```

**Temperature:** 0.3 for analysis (consistent), 0.7 for drafts (creative).

**Why GPT-4o-mini:**
- $0.15 per 1M input tokens, $0.60 per 1M output tokens
- A typical conversation analysis costs $0.002-0.005
- 50 leads/day = $0.10-0.25/day = $3-7.50/month
- Good enough for extraction, scoring, and drafting

### 4. CRM (SQLite)
**File:** `database/db.py`, `database/schema.sql`
**Tables:**
- `leads` — master lead record, scores, status, source
- `messages` — every message from every channel, linked to lead
- `ad_campaigns` + `ad_insights` — daily ad performance snapshots
- `ai_recommendations` — AI suggestions waiting for action
- `meetings` — suggested and scheduled meetings
- `cold_calls` — logged calls with scripts and outcomes
- `outbound_drafts` — AI-drafted messages waiting for human send

**Why SQLite:**
- Zero config, zero cost, single file
- 100K leads easily handled
- Easy to backup (just copy the file)
- Migration path to PostgreSQL later (one line change in `db.py`)

### 5. Ad Analyzer
**File:** `core/ad_analyzer.py`
**Responsibility:**
- Pull campaign, adset, ad-level metrics from Meta Graph API daily
- Store daily snapshots in `ad_insights`
- Aggregate by campaign for AI analysis
- Identify best/worst performing ads by leads per dollar spent

**Key Metrics:**
- CTR, CPC, CPM, cost per lead, messaging conversations
- Best ad = highest (leads + messages) / spend
- Kill ad = lowest conversion at highest spend

### 6. Lead Scorer
**File:** `core/lead_scorer.py`
**Algorithm:**
```
score = 0
+15 if phone present
+10 if email present
+10 if business_name known
+5 if industry known
+status_bonus (new=0, contacted=10, qualified=30, proposal=50, negotiation=70, won=100)
+min(msg_count * 3, 20)  # engagement bonus
+15 if AI says "hot"
+10 if AI extracted budget
+10 if AI suggested meeting
score = min(score, 100)
```

**Hot threshold:** 70+ (suggest meeting)
**Warm threshold:** 40-69 (follow up sequence)
**Cold threshold:** <40 (nurture or deprioritize)

### 7. Outbound Engine
**File:** `core/outbound.py`
**Responsibility:**
- AI drafts personalized messages for each platform
- Stores drafts in `outbound_drafts` table
- For Email: can auto-send (toggle in config)
- For WhatsApp/Instagram: AI drafts, you send manually (or use templates after 24h)
- Generates cold call scripts with AI
- Exports call list to CSV with phone + script + score

### 8. Dashboard (FastAPI)
**File:** `dashboard/app.py`
**Routes:**
- `GET /` — Main dashboard (HTML)
- `GET /api/leads` — All leads JSON
- `GET /api/leads/{id}` — Lead detail + messages
- `GET /api/hot-leads` — Hot leads JSON
- `GET /api/call-list` — Call list with scripts
- `GET /api/ads` — Ad performance summary
- `POST /api/ads/analyze` — Trigger AI ad analysis
- `POST /api/draft/{id}` — Draft outbound for a lead
- `POST /api/lead/add` — Manual lead entry
- `GET/POST /api/webhook/*` — Webhooks for all channels
- `POST /api/email/check` — Manually trigger email check
- `POST /api/email/send-proposal/{id}` — Send proposal email
- `POST /api/whatsapp/send/{id}` — Send WhatsApp to lead
- `GET /api/leads/by-channel` — Lead count per channel
- `GET /api/leads/unread` — Unread messages

### 9. Cron Jobs (APScheduler)
**Scheduler:** `BackgroundScheduler` in `app.py`
- **Daily 9 AM:** Pull ad insights from Meta → store → AI analysis → save recommendation
- **Every 15 minutes:** Check Gmail IMAP for new emails → process → AI reply → store
- **Weekly (Friday 6 PM):** Generate weekly report → save to dashboard

---

## Data Flow: Lead Lifecycle

```
┌─────────────────┐
│  Lead Messages  │  (WhatsApp/IG/FB/Email/Telegram)
│     You First   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Unified Inbox  │  → Deduplicate → Create lead → Log message
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Brain       │  → Analyze conversation → Extract data → Draft reply
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Auto-  │ │ Update │
│ Reply  │ │ Lead   │  → score, status, extracted data
└────────┘ │        │
           │        │
           ▼        ▼
    ┌─────────────────┐
    │  Score >= 70?   │
    └────────┬────────┘
             │
       Yes ┌─┴─┐ No
         ▼     ▼
  ┌────────┐ ┌────────┐
  │ Suggest│ │ Follow │
  │ Meeting│ │ Up     │
  │ +2 days│ │ Sequence│
  └────────┘ └────────┘
       │
       ▼
  ┌────────┐
  │ You    │
  │ Meet   │
  │ Client │
  └────────┘
       │
       ▼
  ┌────────┐
  │ Close  │
  │ Deal   │
  └────────┘
       │
       ▼
  ┌────────┐
  │ Update │
  │ Status │  → won
  └────────┘
```

---

## Data Flow: Ad Performance → AI Decision

```
┌─────────────────┐
│  Meta Ads Run   │  → Daily budget spent, impressions, clicks, messages
└────────┬────────┘
         │
         ▼ (Daily 9 AM cron)
┌─────────────────┐
│  Graph API      │  → Pull campaign/adset/ad data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ad_insights    │  → Store daily snapshot per ad
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Aggregate      │  → Sum spend, leads, messages per ad
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Brain       │  → Prompt: "Which ad wins? Which to kill? What to test?"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ai_recs        │  → Save recommendation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboard      │  → Show: "🔥 Scale Ad X, Kill Ad Y, Test Z next"
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  You Act        │  → Update Meta Ads Manager (manual, for now)
└─────────────────┘
```

---

## Deployment Architecture

### Option A: Local Development (Free, You Run It)
```
Your Laptop / PC
├── Python 3.11
├── SQLite file
├── OpenAI API key
├── ngrok (for webhooks during testing)
└── http://localhost:8000
```

### Option B: Oracle Cloud Free Tier (Free Forever, Production-Ready)
```
Oracle Cloud Free Tier (AMD VM, 2 vCPU, 1 GB RAM)
├── Ubuntu 22.04
├── Python 3.11
├── SQLite file + daily backups to Object Storage
├── Nginx reverse proxy
├── SSL (Let's Encrypt)
├── Systemd service (auto-restart on crash)
└── https://your-domain.com
```
**Cost: $0/month** (always free tier)

### Option C: Railway / Render (Paid, Easiest)
```
Railway.app or Render.com
├── Docker container
├── Environment variables
├── Automatic deploy from GitHub
├── SSL included
└── https://your-app.railway.app
```
**Cost: $5-10/month**

---

## Security Considerations

1. **Webhook Verification:** Every webhook (Facebook, WhatsApp, Instagram, Telegram) verifies the signature/token to prevent spoofing.
2. **API Keys:** Stored in `.env`, never in code. `.env` is in `.gitignore`.
3. **SQLite:** Single file, easy to encrypt if needed (SQLCipher). For now, file permissions are sufficient.
4. **Gmail:** Uses App Password, not your main password. Can be revoked anytime.
5. **Meta Tokens:** Use long-lived tokens. Rotate quarterly.

---

## Scalability Path (When You Grow)

| Current | Next Step | When |
|---------|-----------|------|
| SQLite | PostgreSQL | 10K+ leads |
| Single process | Gunicorn + Uvicorn workers | 100+ concurrent users |
| APScheduler | Celery + Redis | 10K+ messages/day |
| OpenAI direct | LangChain + vector DB (Chroma) | Need memory across sessions |
| FastAPI templates | React/Vue frontend | Need richer UX |
| One AI model | Fine-tuned model on your data | 100K+ conversations |
| Manual ad actions | Meta Marketing API (auto-budget) | 10+ campaigns running |
| One server | Docker + Kubernetes | Team of 10+ salespeople |

---

## Why This Architecture Works for $10

| Component | Why Cheap | Cost |
|-----------|----------|------|
| SQLite | Zero infra, zero hosting | $0 |
| FastAPI | Python, open source | $0 |
| OpenAI GPT-4o-mini | Cheapest capable model | $3-8/mo |
| WhatsApp Cloud API | 1,000 free conversations | $0 |
| Meta Graph API | Free for your own data | $0 |
| Gmail IMAP/SMTP | Free with any Gmail | $0 |
| Oracle Cloud Free Tier | Always free VM | $0 |
| **Total** | | **$3-8/mo** |

The architecture is designed to be **monolithic but modular**. Every channel is a separate file, but they all route through one unified inbox. This means:
- You can add a new channel in 1 day (just write a new handler)
- You can remove a channel without breaking anything
- You can swap the AI model later (one file: `ai_brain.py`)
- You can migrate the database later (one file: `db.py`)

---

## Next Architecture Decisions

1. **Do you want the Oracle Cloud deployment script now?** (Free forever, runs 24/7)
2. **Do you want me to add a Redis/caching layer?** (For faster responses, but adds cost)
3. **Do you want me to design the React frontend?** (Better UX, but more complexity)
4. **Do you want me to add LangChain + memory?** (AI remembers conversations across sessions, more human-like)

The architecture is solid. The code is modular. Now we just need to deploy it and start testing with real leads.
