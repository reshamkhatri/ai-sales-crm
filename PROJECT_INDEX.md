# AI Sales Assistant — Project Index

This is your complete AI sales assistant. Everything you need is here.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your real API keys

# 3. Run it
python run.py

# 4. Open dashboard
http://localhost:8000
```

## Project Structure

```
ai-sales-assistant/
│
├── config.py                    # All API keys & settings (reads from .env)
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies
├── run.py                       # Main entry point — starts the server
│
├── database/
│   ├── schema.sql               # SQLite database schema (7 tables)
│   └── db.py                    # Database helper functions (CRUD + queries)
│
├── core/                        # ALL business logic — modular, swappable
│   ├── unified_inbox.py         # ONE router for ALL channels → AI → CRM
│   ├── crm.py                   # Lead & message management
│   ├── ai_brain.py              # OpenAI prompts (analysis, drafting, scoring)
│   ├── ad_analyzer.py           # Meta Graph API (pull ads, store insights)
│   ├── messenger.py             # Facebook Messenger webhook handler
│   ├── whatsapp.py              # WhatsApp Cloud API (auto-reply, templates)
│   ├── instagram.py             # Instagram DM handler
│   ├── email_handler.py         # Gmail IMAP (read) + SMTP (send)
│   ├── telegram.py              # Telegram bot handler
│   ├── lead_scorer.py           # Lead scoring algorithm (0-100)
│   └── outbound.py              # Outreach drafting, call scripts, CSV export
│
├── dashboard/
│   ├── app.py                   # FastAPI app — all routes + webhooks
│   └── templates/
│       └── index.html           # Single-page dashboard (HTML, no JS framework)
│
├── docs/
│   ├── ARCHITECTURE.md          # Complete system architecture + data flows
│   ├── DEPLOYMENT.md            # Production deployment guide (3 options)
│   ├── WHATSAPP_SETUP.md        # WhatsApp Cloud API step-by-step for Dubai
│   └── diagrams/
│       └── architecture_overview.png  # Visual system diagram
│
├── deploy/
│   └── oracle-cloud-deploy.sh   # One-click deploy to Oracle Cloud Free Tier
│
└── README.md                    # Full project README with roadmap
```

## Architecture at a Glance

```
WhatsApp ──┐
Instagram ──┤
Facebook ────┼──→ Unified Inbox ──→ AI Brain (OpenAI) ──→ CRM (SQLite)
Email ───────┤                                    │
Telegram ────┘                                    │
                                                  ↓
                              ┌───────────────────┼──────────────────┐
                              ↓                   ↓                  ↓
                         Auto-Reply         Meeting Suggest      Ad Analysis
                         (WhatsApp/IG)      (Dashboard)        (Daily Report)
```

## Cost: $3–$8/month

| Component | Cost | Why |
|-----------|------|-----|
| OpenAI GPT-4o-mini | $3–$8 | Conversation analysis + drafting |
| WhatsApp Cloud API | $0 | 1,000 free conversations/month |
| Meta Graph API | $0 | Free to read your own ad data |
| Gmail IMAP/SMTP | $0 | Free with any Gmail account |
| Server | $0 | Oracle Cloud Free Tier (always free) |
| SQLite | $0 | Built-in, zero infra |
| **Total** | **$3–$8** | Well under $10 |

## What Each File Does

### `core/unified_inbox.py` — The Heart
This is the most important file. Every incoming message from every channel calls `handle_incoming_message()`. It:
1. Deduplicates leads (finds existing by phone/email/ID)
2. Creates new leads if not found
3. Logs every message to the database
4. Fetches last 10 messages as context
5. Calls the AI brain for analysis
6. Updates lead score and status
7. Suggests meetings if hot
8. Returns reply + analysis back to the channel handler

**Why this matters:** One unified router = one source of truth. No duplicate leads. Consistent scoring across all channels.

### `core/ai_brain.py` — The Brain
All AI prompts live here. Pure prompt engineering, no business logic.
- `analyze_conversation()` → Returns JSON with temperature, budget, timeline, reply draft
- `analyze_ads()` → Compares ad performance, suggests kill/scale/test
- `draft_outbound_message()` → Drafts personalized outreach for any platform
- `generate_cold_call_script()` → Writes 30-second scripts for your sales assistant
- `generate_weekly_report()` → CEO-level weekly summary

**Model:** GPT-4o-mini ($0.15/1M input tokens). 50 leads/day costs $0.10-0.25.

### `core/whatsapp.py` — Dubai's #1 Channel
- Auto-replies instantly when someone messages your WhatsApp business number
- Extracts budget, timeline, needs from Arabic/English messages
- Handles 24-hour Meta conversation window (free-form within 24h, templates after)
- Sends pre-approved templates for re-engagement
- **Cost:** FREE for 1,000 conversations/month

### `core/instagram.py` — B2C Essential
- Auto-replies to Instagram DMs
- Handles story replies and media shares
- Extracts lead info from DM conversations

### `core/email_handler.py` — Proposal Engine
- Polls Gmail IMAP every 15 minutes
- Reads incoming emails, extracts sender info
- AI drafts reply, saves to CRM
- Can auto-send proposals (toggle in config)
- Can send proposal emails manually via API

### `core/lead_scorer.py` — Hot Lead Detector
Algorithm: 0-100 score based on info completeness, engagement, AI-extracted signals.
- 70+ = HOT → Suggest meeting
- 40-69 = WARM → Follow up sequence
- <40 = COLD → Nurture or deprioritize

### `core/ad_analyzer.py` — Ad Intelligence
- Pulls daily ad performance from Meta Graph API
- Stores snapshots in `ad_insights` table
- Aggregates by campaign: spend, impressions, clicks, leads, cost per lead
- Identifies best ad by leads-per-dollar
- Feeds data to AI for strategic recommendations

### `dashboard/app.py` — The Web Interface
FastAPI app with all routes:
- `/` — Dashboard (HTML)
- `/api/leads` — All leads JSON
- `/api/hot-leads` — Hot leads only
- `/api/call-list` — Call list with AI scripts
- `/api/ads` — Ad performance summary
- `/api/ads/analyze` — Trigger AI ad analysis
- `/api/draft/{id}` — Draft outbound message
- `/api/webhook/*` — Webhooks for all channels
- `/api/email/check` — Manually check email
- `/api/whatsapp/send/{id}` — Send WhatsApp to lead
- `/api/leads/by-channel` — Lead count per channel

## Deployment Options

| Option | Cost | Uptime | Best For |
|--------|------|--------|----------|
| **Your Laptop** | $0 | When on | Development, testing |
| **Oracle Cloud Free Tier** | $0 | 24/7 | **Production (recommended)** |
| **Railway / Render** | $5-10/mo | 24/7 | Zero server management |

See `docs/DEPLOYMENT.md` for full step-by-step guide.
See `deploy/oracle-cloud-deploy.sh` for one-click script.

## Data Flow: How a Lead Becomes a Meeting

```
1. Lead sees your Facebook Ad → Clicks "Message on WhatsApp"
           ↓
2. WhatsApp message arrives → AI replies: "What type of website do you need?"
           ↓
3. Lead says: "Restaurant, AED 5K budget, 2 weeks"
           ↓
4. AI extracts: budget=AED 5K, timeline=2 weeks, type=restaurant
           ↓
5. Lead score: 85 (HOT)
           ↓
6. Dashboard shows: "🔥 MEET THIS CLIENT — Restaurant, Dubai Marina, AED 5K"
           ↓
7. Meeting auto-suggested: +2 days, location: Dubai
           ↓
8. You meet them → Close the deal
           ↓
9. All messages stored in CRM for future reference
```

## Data Flow: How AI Manages Your Ads

```
1. Daily 9 AM cron triggers
           ↓
2. Pulls Meta ad data: campaign, adset, ad metrics
           ↓
3. Stores in ad_insights table (daily snapshot)
           ↓
4. Aggregates: spend, impressions, clicks, leads per ad
           ↓
5. AI analyzes: "Ad A got 5 leads for $10, Ad B got 1 lead for $50"
           ↓
6. AI recommendation: "Kill Ad B, Scale Ad A, test new creative C"
           ↓
7. Saves to ai_recommendations table
           ↓
8. Dashboard shows: "🔥 Scale Ad A, Kill Ad B, Test C"
           ↓
9. You update Meta Ads Manager (manual for now, API later)
```

## Multi-Channel Reality Check

| Platform | Auto-Reply | Outbound Send | Cost | Dubai Essential? |
|----------|-----------|---------------|------|-----------------|
| **WhatsApp** | ✅ YES | ❌ Templates only | FREE | YES — #1 channel |
| **Instagram** | ✅ YES | ❌ Only followers | FREE | YES — B2C huge |
| **Facebook** | ✅ YES | ❌ Lead Ads only | FREE | YES — ad integration |
| **Email** | ✅ Draft | ✅ YES | FREE | YES — proposals |
| **Telegram** | ✅ YES | ✅ To bot users | FREE | Optional |
| **Botim** | ❌ NO API | ❌ NO API | N/A | Manual only — use WhatsApp instead |
| **LinkedIn** | ❌ No API | ❌ No API | FREE | AI drafts, you send manually |
| **X/Twitter** | ❌ No API | ❌ No API | FREE | AI drafts, you send manually |

## What You Can Build On Top of This

This is a solid foundation. Future additions:

1. **React/Vue Dashboard** — Richer UX, real-time updates via WebSocket
2. **PostgreSQL Migration** — When you hit 10K+ leads, swap `db.py`
3. **Redis + Celery** — When you hit 10K+ messages/day, replace APScheduler
4. **LangChain Memory** — AI remembers conversations across sessions
5. **Meta Marketing API** — Auto-budget adjustment (kill/scale ads automatically)
6. **Google Calendar Integration** — Auto-create meeting invites
7. **WhatsApp Business API Advanced** — Catalog, payments, location sharing
8. **Fine-Tuned Model** — Train on your 100K+ conversations for better replies
9. **Mobile App** — Flutter/React Native app for your sales team
10. **Voice Calls** — Integrate Twilio for AI-powered phone calls

## Quick Reference: API Routes

| Route | Method | What It Does |
|-------|--------|-------------|
| `/` | GET | Dashboard HTML |
| `/api/leads` | GET | All leads JSON |
| `/api/leads/{id}` | GET | Lead detail + messages |
| `/api/hot-leads` | GET | Hot leads (score >= 70) |
| `/api/call-list` | GET | Call list with AI scripts |
| `/api/ads` | GET | Ad performance summary |
| `/api/ads/analyze` | POST | Trigger AI ad analysis |
| `/api/draft/{id}` | POST | Draft outbound message |
| `/api/lead/add` | POST | Add lead manually |
| `/api/lead/{id}/score` | POST | Recalculate lead score |
| `/api/webhook/facebook` | GET/POST | Facebook webhook |
| `/api/webhook/whatsapp` | GET/POST | WhatsApp webhook |
| `/api/webhook/instagram` | GET/POST | Instagram webhook |
| `/api/webhook/telegram` | POST | Telegram webhook |
| `/api/email/check` | POST | Check Gmail for new emails |
| `/api/email/send-proposal/{id}` | POST | Send proposal email |
| `/api/whatsapp/send/{id}` | POST | Send WhatsApp to lead |
| `/api/instagram/send/{id}` | POST | Send Instagram DM to lead |
| `/api/leads/by-channel` | GET | Lead count per channel |
| `/api/leads/unread` | GET | Unread messages |

## Next Actions (Pick One)

1. **Set up WhatsApp** — Follow `docs/WHATSAPP_SETUP.md` (most important for Dubai)
2. **Deploy to Oracle Cloud** — Run `deploy/oracle-cloud-deploy.sh` (free forever)
3. **Test locally** — `python run.py` and message your WhatsApp number
4. **Connect Meta Ads** — Add `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID`
5. **Add a new channel** — Copy any handler file, adapt the API, route through `unified_inbox.py`

## Need Help?

- Check `docs/ARCHITECTURE.md` for deep technical details
- Check `docs/DEPLOYMENT.md` for production setup
- Check `docs/WHATSAPP_SETUP.md` for WhatsApp specifically
- All code is commented and modular — each file is self-contained

## The Bottom Line

You now have:
- ✅ A unified CRM that tracks every conversation across all channels
- ✅ An AI brain that analyzes conversations, scores leads, and suggests actions
- ✅ Auto-reply on WhatsApp, Instagram, Facebook, Email, Telegram
- ✅ Ad performance analysis that tells you what to kill and what to scale
- ✅ Meeting suggestions for hot leads
- ✅ Cold call scripts and CSV exports
- ✅ A dashboard that shows everything at a glance
- ✅ A deployment script that puts it on a free server forever
- ✅ All for $3–$8/month

**Start with WhatsApp. Everything else follows.**
