# Product Requirements Document

## AI Sales Assistant & Business Copilot

**Version:** 2.0  
**Date:** 2026-06-21  
**Status:** Detailed Draft  
**Primary Market:** Dubai/UAE web design agency  
**Core Idea:** A sales assistant with memory, business context, and practical judgment that helps the owner understand what is happening, what matters, and what to do next.

---

## 1. Product Vision

Build an AI-powered sales and business copilot for a web design agency that captures customer conversations, understands lead quality, remembers business context, recommends next actions, and allows the CEO to chat with the AI about the business in natural language.

The product should feel like a reliable assistant who knows the business:

- It remembers every lead and conversation.
- It knows which leads are serious.
- It explains why sales are up or down.
- It notices missed follow-ups.
- It recommends who to call, who to meet, and which ads to stop.
- It drafts replies, call scripts, proposals, and reports.
- It asks for human approval before risky actions.

The goal is not to replace the CEO or sales team. The goal is to make them faster, sharper, and less likely to miss opportunities.

---

## 2. Product Summary

### 2.1 One-Line Description

An AI sales and business copilot that connects to messaging channels, CRM data, ad performance, and team activity so the agency owner can ask, "How is business going and what should I do next?"

### 2.2 Main Promise

The system gives the CEO a single place to:

- See all leads.
- Understand every conversation.
- Know which opportunities are hot.
- Ask questions about the business.
- Get daily recommendations.
- Track ads, calls, meetings, and pipeline.
- Turn scattered sales activity into clear decisions.

### 2.3 Product Positioning

This is not just:

- A chatbot.
- A CRM.
- A dashboard.
- A lead scoring tool.

It is a business copilot that combines all four.

---

## 3. Problem Statement

The agency currently has leads and sales activity spread across many places:

- WhatsApp
- Instagram DMs
- Facebook Messenger
- Email
- Phone calls
- Manual notes
- Meta Ads Manager
- Staff conversations
- Owner memory

This causes serious business problems:

- Hot leads get missed.
- The CEO does not know what needs attention today.
- Sales staff call people without context.
- Follow-ups are inconsistent.
- Ads are judged by gut feeling instead of conversion quality.
- The same lead may contact through multiple channels and get duplicated.
- The business has data, but no "brain" to interpret it.

The agency does not only need automation. It needs memory, context, and decision support.

---

## 4. Target Users

### 4.1 CEO / Founder

The CEO wants to know:

- How is business going today?
- Which leads should I personally handle?
- Who is ready for a meeting?
- Which deals are likely to close?
- Which ads are wasting money?
- What did the sales assistant do today?
- What should I focus on tomorrow?
- Why did we lose this lead?
- What can we improve in our sales process?

The CEO needs fast answers, not raw tables.

### 4.2 Sales Assistant

The sales assistant wants:

- A prioritized call list.
- Context before every call.
- AI-generated call scripts.
- Follow-up reminders.
- Easy call outcome logging.
- Clear handoff to the CEO when a lead becomes hot.

### 4.3 Marketing / Ad Manager

The ad manager wants:

- Plain-English ad performance summaries.
- Cost per lead.
- Lead quality by campaign.
- Recommendations to kill, scale, or test ads.
- Better understanding of which campaigns produce real buyers, not only cheap leads.

---

## 5. Core Product Principles

### 5.1 The AI Must Be Grounded

The AI should answer from real business data. If it does not know something, it must say so.

Bad answer:

> Sales are probably slow because the market is weak.

Good answer:

> Sales are slower this week because lead volume dropped from 34 to 19, and only 2 leads mentioned budget compared to 8 last week.

### 5.2 The AI Must Explain Its Reasoning

Lead scores, ad recommendations, and meeting suggestions must include reasons.

Example:

> Lead score: 86. Reasons: budget confirmed, timeline under 2 weeks, location known, asked for proposal, replied twice in 1 hour.

### 5.3 Human Approval For Risky Actions

The system may auto-draft many things, but should require approval before:

- Sending proposals.
- Giving discounts.
- Sending outbound messages after long silence.
- Changing ad budgets.
- Marking a deal won/lost.
- Sending sensitive or emotional replies.

### 5.4 Memory Must Be Useful, Not Noisy

The system should remember structured facts, summaries, and outcomes. It should not dump every message into prompts unless needed.

### 5.5 The Product Should Start Narrow And Deep

V1 should make the CEO feel:

> This thing knows my sales pipeline and helps me decide what to do.

It is better to support fewer channels well than many channels poorly.

---

## 6. Product Scope

### 6.1 V1 Must-Have

V1 should include:

- Lead CRM
- Conversation storage
- WhatsApp inbound and reply support
- Gmail monitoring and draft replies
- Manual lead entry
- AI lead extraction
- Explainable lead scoring
- Hot lead detection
- Follow-up reminders
- AI business chat
- Daily CEO brief
- Call list and call scripts
- Basic Meta ad reporting
- Human approval workflow for outbound messages

### 6.2 V1 Should-Have

- Facebook Messenger support
- Instagram DM support
- Telegram support
- CSV export
- Meeting suggestion workflow
- Lead deduplication across phone/email/name
- Weekly sales report
- Search and filters

### 6.3 V2

- Arabic support
- Google Calendar integration
- Team accounts and roles
- Mobile-responsive dashboard
- Automated WhatsApp templates after 24h
- Email follow-up sequences
- Better ad-to-lead attribution
- Proposal generation
- Voice note transcription

### 6.4 V3

- Voice call integration
- AI call summaries
- Multi-tenant white-label version
- Deeper analytics
- Advanced marketing automation
- Fine-tuned scoring based on historical wins/losses

---

## 7. Main Modules

## 7.1 Unified Inbox

The unified inbox receives and stores all customer-facing conversations.

### Supported Sources

V1:

- WhatsApp
- Gmail
- Manual entry

V1.5:

- Facebook Messenger
- Instagram DMs
- Telegram

V2:

- LinkedIn manual import
- Botim manual logging
- Website chat widget

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| UI-001 | Store every inbound message with channel, sender, timestamp, content, and lead ID | P0 |
| UI-002 | Create a lead automatically when a new contact messages | P0 |
| UI-003 | Attach new messages to existing leads when possible | P0 |
| UI-004 | Show full conversation timeline per lead | P0 |
| UI-005 | Mark messages as unread/read | P1 |
| UI-006 | Support manual notes in timeline | P1 |
| UI-007 | Store AI-generated summaries of long conversations | P0 |

---

## 7.2 Lead CRM

The CRM is the source of truth for all prospects.

### Lead Fields

Each lead should store:

- Name
- Phone
- Email
- Business name
- Business type
- Channel source
- Location
- Service needed
- Budget
- Timeline
- Status
- Lead score
- Temperature
- Last contact date
- Next follow-up date
- Owner/assigned user
- Estimated deal value
- Objections
- Important notes
- Conversation summary
- AI confidence

### Lead Statuses

Recommended states:

```text
new -> contacted -> qualified -> meeting_suggested -> meeting_scheduled -> proposal_sent -> negotiation -> won
                                                                               \-> lost
```

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| CRM-001 | Create, view, edit, archive, and delete leads | P0 |
| CRM-002 | Track complete status history | P0 |
| CRM-003 | Add manual notes and reminders | P0 |
| CRM-004 | Search by name, phone, email, business, service, and status | P1 |
| CRM-005 | Filter by hot/warm/cold, channel, date, and assigned user | P1 |
| CRM-006 | Export leads to CSV | P1 |
| CRM-007 | Merge duplicate leads manually | P1 |

---

## 7.3 AI Business Copilot

This is the most important module.

The CEO should be able to chat with the AI and ask questions about the business.

### Example Questions

- "How is business going today?"
- "What should I focus on right now?"
- "Which leads are hot?"
- "Who needs follow-up?"
- "Which leads have budget above AED 5,000?"
- "Why did we lose leads this week?"
- "Which ad brought the best leads?"
- "What did Fatima do today?"
- "Give me a summary before I meet Rami."
- "Which clients asked for proposal but did not reply?"
- "What is my estimated pipeline value?"
- "What changed since yesterday?"
- "Write a follow-up message for this lead."

### Copilot Answer Style

Answers should be:

- Short enough to act on.
- Based on real data.
- Clear about uncertainty.
- Source-backed where possible.
- Action-oriented.

Example:

```text
Today looks strong. You received 9 new leads, 3 are hot, and 2 asked for proposals.

Top priority:
1. Rami from Dubai Marina, AED 8,000 budget, needs restaurant website in 2 weeks.
2. Noor Clinic, asked for e-commerce booking site, no budget yet.
3. Cafe Jumeirah, replied twice but has not been called.

Recommended next action: call Rami before 3 PM and send Noor a budget qualification question.
```

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| AI-CHAT-001 | Provide a chat interface for business Q&A | P0 |
| AI-CHAT-002 | Query CRM, messages, calls, meetings, and ad data | P0 |
| AI-CHAT-003 | Answer with numbers from database, not guesses | P0 |
| AI-CHAT-004 | Include source references for important claims | P0 |
| AI-CHAT-005 | Say when data is missing or uncertain | P0 |
| AI-CHAT-006 | Suggest next best actions | P0 |
| AI-CHAT-007 | Draft replies, call scripts, summaries, and reports | P0 |
| AI-CHAT-008 | Ask approval before sending or changing records | P0 |
| AI-CHAT-009 | Save important CEO instructions as business rules | P1 |
| AI-CHAT-010 | Remember long-term business preferences | P1 |

---

## 7.4 Business Memory

The AI needs structured memory to act intelligently.

### Memory Types

#### Lead Memory

Facts about one lead:

- What they need
- Budget
- Timeline
- Location
- Objections
- Preferred language
- Past conversations
- Next step
- Deal probability

#### Business Memory

Facts about the agency:

- Services offered
- Pricing ranges
- Preferred client types
- Areas served
- Meeting rules
- Proposal style
- Tone of voice
- Common objections
- Sales process

#### Performance Memory

Business metrics:

- Daily lead count
- Conversion rates
- Won/lost reasons
- Ad performance
- Sales assistant activity
- Follow-up completion

#### Instruction Memory

CEO preferences:

- "Never offer discount without asking me."
- "Hot restaurant leads should come to me directly."
- "Use friendly but premium tone."
- "Do not promise delivery under 7 days."

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| MEM-001 | Store structured lead facts extracted from conversations | P0 |
| MEM-002 | Store running conversation summaries | P0 |
| MEM-003 | Store agency business rules and preferences | P0 |
| MEM-004 | Allow CEO to update business rules through chat | P1 |
| MEM-005 | Use memory when generating replies and recommendations | P0 |
| MEM-006 | Record why a memory was created or updated | P1 |
| MEM-007 | Allow memory correction by human users | P1 |

---

## 7.5 AI Lead Understanding

Every incoming conversation should be analyzed.

### Extracted Fields

- Intent
- Service needed
- Budget
- Timeline
- Location
- Business type
- Urgency
- Objections
- Buying signals
- Negative signals
- Requested next step
- Missing qualification questions
- Suggested reply

### Output Format

The AI should return structured JSON, not only free text.

Example:

```json
{
  "intent": "website_request",
  "service_needed": "restaurant website",
  "budget": 8000,
  "currency": "AED",
  "timeline": "2 weeks",
  "location": "Dubai Marina",
  "temperature": "hot",
  "score_delta": 35,
  "missing_fields": [],
  "suggested_next_action": "suggest_meeting",
  "confidence": 0.86
}
```

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| AI-001 | Analyze every inbound message | P0 |
| AI-002 | Extract lead facts into structured fields | P0 |
| AI-003 | Update conversation summary | P0 |
| AI-004 | Detect missing qualification fields | P0 |
| AI-005 | Generate a recommended next action | P0 |
| AI-006 | Flag messages requiring human review | P0 |
| AI-007 | Support multilingual content in future | P2 |

---

## 7.6 Explainable Lead Scoring

Lead score should be transparent.

### Suggested Scoring Model

| Signal | Points |
|---|---:|
| Clear service need | +15 |
| Budget mentioned | +20 |
| Budget above minimum target | +15 |
| Timeline under 30 days | +15 |
| Phone/email available | +10 |
| Location in target area | +5 |
| Asked for proposal | +10 |
| Replied more than once | +10 |
| Contacted through multiple channels | +10 |
| Has strong objection | -10 |
| No response for 7 days | -15 |
| Says "just checking price" only | -10 |
| Marked not interested | -40 |

Maximum score should be capped at 100.

### Score Bands

| Score | Label | Meaning | Action |
|---:|---|---|---|
| 0-39 | Cold | Low intent or missing info | Nurture or ignore |
| 40-69 | Warm | Potential buyer | Follow up |
| 70-100 | Hot | Strong opportunity | CEO review or meeting |

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| SCORE-001 | Calculate score automatically after every new message | P0 |
| SCORE-002 | Store score history | P0 |
| SCORE-003 | Show score explanation | P0 |
| SCORE-004 | Allow manual override | P1 |
| SCORE-005 | Learn from won/lost outcomes over time | P2 |

---

## 7.7 Next Best Action Engine

The system should recommend what to do next for each lead.

### Possible Actions

- Ask budget question
- Ask timeline question
- Ask for phone number
- Send portfolio
- Suggest meeting
- Prepare proposal
- Call now
- Follow up tomorrow
- Mark cold
- Escalate to CEO

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| NBA-001 | Generate next best action for each active lead | P0 |
| NBA-002 | Show reason for action | P0 |
| NBA-003 | Prioritize action list for CEO and sales assistant | P0 |
| NBA-004 | Detect stale leads needing follow-up | P0 |
| NBA-005 | Avoid recommending duplicate actions | P1 |

---

## 7.8 Daily CEO Brief

The CEO should receive a daily summary in the dashboard and optionally by email/WhatsApp.

### Daily Brief Sections

- New leads today
- Hot leads requiring attention
- Meetings today
- Follow-ups overdue
- Proposals pending
- Deals won/lost
- Pipeline value
- Ad spend and lead quality
- Sales assistant activity
- Recommended focus for today

### Example

```text
Good morning. Yesterday you received 14 leads. 4 are hot, 6 are warm, and 4 are cold.

Your best opportunity is Rami Restaurant, AED 8,000 budget, wants launch in 2 weeks.

You have 3 overdue follow-ups:
- Noor Clinic, proposal sent 3 days ago.
- Cafe Jumeirah, asked price but no reply.
- Dubai Salon, needs call after 4 PM.

Ad note: Restaurant Website Campaign has the best cost per qualified lead. Clinic Campaign generated cheap leads but low quality.
```

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| BRIEF-001 | Generate daily CEO brief | P0 |
| BRIEF-002 | Include hot leads and recommended actions | P0 |
| BRIEF-003 | Include ad and pipeline summary | P1 |
| BRIEF-004 | Save brief history | P1 |
| BRIEF-005 | Send brief by email/WhatsApp with approval/configuration | P2 |

---

## 7.9 Sales Assistant Workflow

The sales assistant needs a practical work queue.

### Features

- Prioritized call list
- AI call scripts
- Lead context before call
- One-click outcome logging
- Follow-up creation
- Escalation to CEO

### Call Outcomes

- Answered, interested
- Answered, not interested
- No answer
- Voicemail
- Call back later
- Wrong number
- Meeting requested
- Proposal requested

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| CALL-001 | Generate prioritized call list | P0 |
| CALL-002 | Generate personalized call script | P0 |
| CALL-003 | Show lead summary before call | P0 |
| CALL-004 | Log call outcome | P0 |
| CALL-005 | Update score and next action after call | P0 |
| CALL-006 | Show daily sales assistant activity | P1 |

---

## 7.10 Meeting Workflow

Hot leads should produce meeting suggestions.

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| MEET-001 | Suggest meeting for hot leads | P0 |
| MEET-002 | Generate meeting brief | P0 |
| MEET-003 | Store meeting date, time, location, and status | P0 |
| MEET-004 | Log outcome | P0 |
| MEET-005 | Update lead status after meeting | P0 |
| MEET-006 | Google Calendar integration | P2 |

### Meeting Brief Example

```text
Lead: Rami Restaurant
Location: Dubai Marina
Need: Restaurant website with online ordering
Budget: AED 8,000
Timeline: 2 weeks
Concern: Wants fast delivery
Recommended pitch: Emphasize restaurant examples, delivery timeline, and online ordering.
```

---

## 7.11 Ad Intelligence

The system should help the agency understand ad performance in terms of lead quality, not only clicks.

### Metrics

- Spend
- Impressions
- Clicks
- CTR
- Leads
- Cost per lead
- Qualified leads
- Cost per qualified lead
- Hot leads by campaign
- Won deals by campaign
- Estimated revenue by campaign

### Recommendations

- Kill campaign
- Scale campaign
- Reduce budget
- Test new creative
- Improve landing/message flow
- Watch for more data

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| ADS-001 | Pull Meta ad data daily | P1 |
| ADS-002 | Store daily ad snapshots | P1 |
| ADS-003 | Link leads to campaign where possible | P1 |
| ADS-004 | Calculate cost per lead and cost per qualified lead | P1 |
| ADS-005 | Generate plain-English recommendations | P1 |
| ADS-006 | Require approval before changing ad budgets | P2 |

---

## 7.12 Outbound Drafting

The AI should draft messages but avoid unsafe automation.

### Draft Types

- WhatsApp reply
- Email reply
- Follow-up message
- LinkedIn connection message
- Cold email
- Instagram DM
- Proposal introduction
- Post-meeting follow-up

### Requirements

| ID | Requirement | Priority |
|---|---|---|
| OUT-001 | Generate contextual replies from lead history | P0 |
| OUT-002 | Save drafts before sending | P0 |
| OUT-003 | Allow human edit and approval | P0 |
| OUT-004 | Respect WhatsApp 24-hour and template rules | P0 |
| OUT-005 | Detect risky replies and require review | P0 |
| OUT-006 | Keep message tone aligned with agency settings | P1 |

---

## 8. AI Safety And Reliability

### 8.1 The AI Must Not

- Invent lead details.
- Promise prices not configured by the business.
- Promise unrealistic timelines.
- Send discounts without approval.
- Ignore platform messaging rules.
- Pretend a human has approved something.
- Hide uncertainty.
- Mark deals won without confirmation.

### 8.2 Confidence Levels

Every AI extraction and recommendation should include confidence.

| Confidence | Meaning | Behavior |
|---|---|---|
| High | Clear evidence in data | Can recommend strongly |
| Medium | Some evidence, missing details | Ask clarifying question |
| Low | Unclear or conflicting data | Ask human to review |

### 8.3 Human Review Triggers

Require human review when:

- Lead asks for exact price.
- Lead complains.
- Lead mentions legal/payment issue.
- AI confidence is low.
- Message contains sarcasm or unclear intent.
- Lead score changes dramatically.
- Proposal or discount is involved.

---

## 9. Dashboard Requirements

### 9.1 Main Dashboard

The first screen should show:

- Today's CEO brief
- Hot leads
- Overdue follow-ups
- Pipeline value
- New leads by channel
- Today's meetings
- Ad recommendation
- Sales assistant activity
- AI chat entry point

### 9.2 Lead Detail Page

Must show:

- Lead profile
- Score and explanation
- Conversation timeline
- AI summary
- Next best action
- Draft reply
- Notes
- Call history
- Meeting history
- Source/ad attribution

### 9.3 AI Chat Page

Must show:

- Chat with business copilot
- Suggested questions
- Source-backed answers
- Action buttons for generated tasks/drafts
- Past business instructions

---

## 10. Data Model

Recommended core tables:

- users
- leads
- messages
- lead_facts
- lead_score_events
- conversation_summaries
- business_rules
- ai_memories
- ai_chat_sessions
- ai_chat_messages
- ai_recommendations
- tasks
- call_logs
- meetings
- outbound_drafts
- ad_campaigns
- ad_insights
- daily_briefs
- audit_logs

### Important Notes

- Messages are raw history.
- Conversation summaries are compact memory.
- Lead facts are structured truth.
- Score events explain how scores changed.
- Business rules guide AI behavior.
- Audit logs track sensitive actions.

---

## 11. API Requirements

### 11.1 Core APIs

| Endpoint | Purpose |
|---|---|
| `GET /api/leads` | List and filter leads |
| `GET /api/leads/{id}` | Lead detail |
| `POST /api/leads` | Create manual lead |
| `PATCH /api/leads/{id}` | Update lead |
| `POST /api/leads/{id}/merge` | Merge duplicate leads |
| `GET /api/leads/{id}/messages` | Lead conversation timeline |
| `POST /api/leads/{id}/notes` | Add note |
| `POST /api/leads/{id}/score/recalculate` | Recalculate score |
| `GET /api/tasks` | Work queue |
| `POST /api/tasks` | Create task |
| `POST /api/calls/log` | Log call outcome |
| `POST /api/meetings` | Create meeting |
| `POST /api/drafts` | Generate draft |
| `POST /api/drafts/{id}/send` | Send approved draft |

### 11.2 AI Copilot APIs

| Endpoint | Purpose |
|---|---|
| `POST /api/copilot/chat` | Ask business question |
| `GET /api/copilot/suggestions` | Suggested questions |
| `POST /api/copilot/business-rules` | Add business rule |
| `GET /api/copilot/daily-brief` | Get today brief |
| `POST /api/copilot/daily-brief/generate` | Generate brief |

### 11.3 Webhook APIs

| Endpoint | Purpose |
|---|---|
| `POST /api/webhooks/whatsapp` | Receive WhatsApp |
| `POST /api/webhooks/facebook` | Receive Messenger |
| `POST /api/webhooks/instagram` | Receive Instagram |
| `POST /api/webhooks/telegram` | Receive Telegram |
| `POST /api/email/check` | Poll/check Gmail |

All production APIs must require authentication except external webhooks, which must use signature verification.

---

## 12. Non-Functional Requirements

### 12.1 Performance

| Requirement | Target |
|---|---|
| Dashboard load time | Under 2 seconds for normal use |
| AI chat answer time | Under 8 seconds for normal questions |
| Auto-reply draft generation | Under 5 seconds |
| Webhook processing acknowledgement | Under 2 seconds |

### 12.2 Reliability

| Requirement | Target |
|---|---|
| Daily backup | Required |
| Restore test | Monthly |
| Error logging | Required |
| Failed job retry | Required |
| Message processing idempotency | Required |

### 12.3 Security

| Requirement | Priority |
|---|---|
| User login | P0 |
| Role-based access | P1 |
| HTTPS | P0 |
| Webhook signature verification | P0 |
| No secrets in code | P0 |
| Audit logs for sends/deletes/status changes | P0 |
| PII-safe logs | P0 |
| Right to delete lead data | P0 |

---

## 13. Success Metrics

### 13.1 Product Metrics

- Time to first response
- Number of hot leads detected
- Follow-up completion rate
- AI draft acceptance rate
- AI chat usage per day
- Daily brief open rate
- Lead score accuracy based on won/lost outcomes
- Missed follow-ups

### 13.2 Business Metrics

- Lead-to-meeting conversion
- Meeting-to-proposal conversion
- Proposal-to-close conversion
- Revenue won
- Pipeline value
- Cost per qualified lead
- Ad spend wasted on low-quality campaigns
- Hours saved per week

### 13.3 AI Quality Metrics

- Extraction accuracy
- Hallucination rate
- Percentage of answers with sources
- Human correction rate
- Unsafe auto-action attempts blocked
- Confidence calibration

---

## 14. MVP Build Plan

### Phase 1: CRM And Memory Foundation

- Leads table
- Messages table
- Notes
- Conversation summaries
- Lead facts
- Manual lead entry
- Basic dashboard

### Phase 2: AI Lead Brain

- Message analysis
- Fact extraction
- Score calculation
- Score explanation
- Suggested next action
- Draft replies

### Phase 3: AI Business Copilot

- Chat interface
- Database query tools
- Daily CEO brief
- Source-backed answers
- Business rules memory

### Phase 4: Sales Workflow

- Call list
- Call scripts
- Call logging
- Follow-up tasks
- Meeting suggestions

### Phase 5: Channels

- WhatsApp
- Gmail
- Facebook/Instagram if permissions are ready
- Telegram optional

### Phase 6: Ads

- Meta ad pull
- Cost per lead
- Cost per qualified lead
- Kill/scale/test recommendations

---

## 15. Realistic V1 Acceptance Criteria

V1 is successful if:

- The system captures leads from at least one real channel.
- The CEO can see all leads in one dashboard.
- The AI extracts useful facts from conversations.
- Every lead has a score and explanation.
- The CEO can ask the AI about the business and get grounded answers.
- The daily brief correctly identifies top opportunities and overdue follow-ups.
- The sales assistant can generate a call list and scripts.
- The system reduces missed follow-ups.
- The system does not send risky messages without approval.

---

## 16. Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| AI invents facts | Medium | High | Source-backed answers, structured data, confidence checks |
| Meta permissions delay launch | High | Medium | Start with manual/Gmail/WhatsApp where available |
| Auto-replies sound robotic | Medium | Medium | Human approval, tone settings, templates |
| Lead scoring is inaccurate | Medium | Medium | Explain scores, allow overrides, learn from outcomes |
| Data gets messy | High | High | Strong schema, deduplication, manual merge |
| CEO does not trust AI | Medium | High | Show reasoning and source data |
| Sales team does not use it | Medium | High | Keep workflows simple and fast |
| Costs exceed target | Medium | Medium | Use smaller models, summarize memory, avoid unnecessary AI calls |

---

## 17. Open Decisions

| Question | Recommended Decision |
|---|---|
| Should AI auto-send replies? | Only safe qualification replies in V1; approval for important messages |
| Should Arabic be V1? | No, but design data model for it |
| Should every channel be V1? | No, start with WhatsApp, Gmail, manual |
| Should ads be automatic? | No, recommendations only |
| Should the AI change records? | Yes for low-risk suggestions after approval; log everything |
| Should the product be multi-tenant? | Not in V1 |
| Should there be mobile app? | Not in V1; responsive web first |

---

## 18. Final Product Definition

The best version of this product is:

> A business-aware AI sales copilot that remembers every lead, understands conversations, explains what is happening in the business, and recommends the next best action for the CEO and sales team.

The product should not try to fake being human. It should behave like an extremely organized, context-aware assistant:

- It remembers.
- It summarizes.
- It reasons from data.
- It warns when something is urgent.
- It asks before risky actions.
- It gets better as the business uses it.

That is the realistic path to building an agent with a real business brain.

