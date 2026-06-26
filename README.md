<div align="center">

# 🎯 AI Sales CRM

**An AI-powered sales platform that finds leads, talks to them across every channel, moves them through a pipeline, and tells you what to do next — from one command center.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![LLM](https://img.shields.io/badge/LLM-OpenAI%20%7C%20DeepSeek-412991?logo=openai&logoColor=white)](#ai-provider)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ✨ Overview

AI Sales CRM is a full-stack sales operating system for small agencies and teams. It unifies **lead generation, multi-channel conversations, a deal pipeline, follow-up automation, and an AI business copilot** into a single, fast dashboard — runnable on a laptop for a few dollars a month.

It answers the questions every sales team actually has:
- **Who do I call today?** → interest-weighted worklist & hot-lead detection
- **How do I get more leads?** → built-in prospecting + a browser-extension Google-Maps pipeline + a public lead-capture form
- **What's going on in the business?** → an AI copilot that reasons over live CRM data
- **How are my ads doing?** → Meta ad ingestion with kill/scale/test recommendations

## 🚀 Features

| Area | What it does |
|---|---|
| 🧲 **Lead generation** | Google-Maps / web prospecting with **website contact enrichment** (scrapes phone + email), CSV import, dedup, and a public **lead-capture form** with an ingest API |
| 🔌 **Browser-extension integration** | Speaks a clean `/api/leads/ingest` + `/batch` protocol so a Chrome extension can push reliably-scraped Google-Maps leads straight into the CRM (API-key auth + placeId/phone dedup) |
| 💬 **Multi-channel inbox** | WhatsApp, Instagram, Facebook, Email, and Telegram webhooks route into one unified handler; outbound messages deliver via the lead's channel |
| 📊 **Lead workspace** | A focused per-lead view: profile, deal-stage pipeline (`qualified → proposal → negotiation → won`), activity timeline, live chat, tasks, and contact card |
| ✅ **Follow-up engine** | Overdue tracking, due-today queue, snooze, and auto-queueing follow-ups for hot leads so nothing slips |
| 🤖 **AI business copilot** | Source-grounded answers about pipeline, leads, and ads + a daily CEO brief — works with **OpenAI or any OpenAI-compatible API (e.g. DeepSeek)**, with a smart data-backed fallback when no key is set |
| 📈 **Ad intelligence** | Pulls Meta ad performance and recommends what to kill, scale, or test |
| 🎯 **Lead scoring** | 0–100 scoring with hot/warm/cold tiers driving the worklist |

## 🖼️ Screenshots

> _Add screenshots of the workspace, overview, and prospecting modal here._
>
> `docs/screenshots/workspace.png` · `docs/screenshots/overview.png`

## 🏗️ Architecture

```
        Lead sources                          One brain                       Outcomes
 ┌────────────────────────┐        ┌──────────────────────────┐        ┌───────────────────┐
 │ Browser extension      │        │                          │        │ Worklist & scoring│
 │ (Google Maps)          ├───┐    │   FastAPI app            │   ┌───►│ Deal pipeline     │
 │ Prospecting + enrich   │   │    │   ├─ unified inbox       │   │    │ Follow-up queue   │
 │ Public lead form       ├───┼───►│   ├─ CRM (SQLite)        ├───┼───►│ AI copilot + brief│
 │ WhatsApp/IG/FB/Email   │   │    │   ├─ AI brain (LLM)      │   │    │ Ad recommendations│
 │ Manual entry           ├───┘    │   └─ lead scorer         │   └───►│ Outbound delivery │
 └────────────────────────┘        └──────────────────────────┘        └───────────────────┘
```

**Tech stack:** Python · FastAPI · SQLite · Jinja2 · vanilla JS (no build step) · APScheduler · OpenAI-compatible LLM.

## ⚡ Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (copy the template, fill in what you have — it runs with no keys too)
cp .env.example .env

# 3. Run
python run.py
```

Open **http://localhost:8000** — the lead workspace. Other views:
- `/overview` — command-center dashboard
- `/lead-form` — public lead-capture form

> The app runs **with zero API keys** using data-backed fallbacks. Add an AI key to unlock the real copilot, and channel tokens to go live.

## 🔑 Configuration

All secrets live in `.env` (never committed). See [`.env.example`](.env.example) for the full list. Highlights:

```env
# AI — OpenAI or any OpenAI-compatible provider
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
# DeepSeek example:
#   OPENAI_BASE_URL=https://api.deepseek.com
#   OPENAI_MODEL=deepseek-chat

# Lead Finder browser extension (x-api-key it must send; blank = accept any)
LEADFINDER_API_KEY=
```

### AI provider
The AI layer talks to OpenAI by default but works with **any OpenAI-compatible API** (DeepSeek, Together, Groq, OpenRouter, local models) by setting `OPENAI_BASE_URL`. One line, no code changes.

## 🗺️ Roadmap

- [ ] One-click deploy (Railway / Render / Oracle Cloud)
- [ ] Auth / multi-user
- [ ] Deal value & revenue forecasting
- [ ] Calendar integration for meetings
- [ ] Arabic language support

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built with FastAPI + a lot of sales-process thinking.</sub>
</div>
