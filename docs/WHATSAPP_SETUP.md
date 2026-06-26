# WhatsApp Cloud API Setup Guide for Dubai

## Why WhatsApp is Essential in Dubai
In Dubai and the UAE, **WhatsApp is the #1 business communication channel**. Every client, lead, and partner expects to message you on WhatsApp. Your AI assistant MUST be on WhatsApp.

## What the AI Can Do on WhatsApp
- Auto-reply instantly when someone messages you
- Extract budget, timeline, needs from their messages
- Send AI-written replies back (within 24h window)
- After 24h, use pre-approved templates to re-engage
- Collect phone numbers for your cold call list
- Suggest meetings for hot leads

## What it CANNOT Do
- Send unsolicited messages to people who haven't messaged you (Meta restriction)
- Send marketing messages without pre-approved templates

## Setup Steps

### Step 1: Get Meta Business Manager
1. Go to https://business.facebook.com
2. Create a Business Manager account (or use existing)
3. Verify your business (recommended for full features)

### Step 2: Create WhatsApp Business Account
1. In Business Manager, go to **More Tools > WhatsApp Manager**
2. Click **Get Started**
3. Add a phone number (use a UAE number, can be a business mobile)
4. Verify via SMS/call

### Step 3: Create a WhatsApp App
1. Go to https://developers.facebook.com/apps
2. Create App > Business > WhatsApp
3. Connect your WhatsApp Business Account
4. Add your verified phone number

### Step 4: Get Your Credentials

**Phone Number ID:**
- In WhatsApp Manager, go to **Phone Numbers**
- Copy the ID (looks like `123456789012345`)
- Add to `.env`: `WHATSAPP_PHONE_NUMBER_ID=...`

**Access Token:**
- In your app, go to **WhatsApp > API Setup**
- Generate a **Permanent Access Token**
- Add to `.env`: `WHATSAPP_ACCESS_TOKEN=...`

**Note:** The WhatsApp token is often the SAME as your Facebook Page token if permissions are set correctly.

### Step 5: Set Up Webhook

1. In your Meta app, go to **WhatsApp > Configuration**
2. Set webhook URL: `https://your-server.com/api/webhook/whatsapp`
3. Verify token: `wa_webhook_123` (or whatever you set in `.env`)
4. Subscribe to: `messages`

### Step 6: Create Message Templates (for after 24h)

1. In WhatsApp Manager, go to **Account Tools > Message Templates**
2. Create a template like:

```
Name: webdesign_intro
Language: English
Category: Utility

Body: Hello {{1}}, thanks for your interest in our web design services! We'd love to discuss your project. Can we schedule a quick call?

Variables: {{1}} = customer name
```

3. Submit for approval (usually takes 1-24 hours)
4. Once approved, you can send this to leads after the 24h window

### Step 7: Test

1. Send a message to your WhatsApp business number
2. Check your dashboard — the AI should reply instantly
3. Check the database — the lead should be saved automatically

## WhatsApp Pricing (What You Actually Pay)

| Conversation Type | Cost | When |
|-----------------|------|------|
| User-initiated | FREE (first 1,000/mo) | Someone messages you first |
| Business-initiated (template) | ~$0.005-0.02/msg | You send first (after 24h) |
| Meta free tier | 1,000 conversations/mo | Always |

**For a Dubai web design agency:**
- If you get 50-100 WhatsApp leads per month: **FREE** (under 1,000)
- If you need to re-engage 200+ cold leads: ~$5-10/month
- So WhatsApp is essentially FREE for most small agencies

## Important: 24-Hour Window Rule

Meta enforces a **24-hour conversation window**:
- If a user messages you, you have 24 hours to reply with ANY message (free-form AI)
- After 24 hours, you MUST use a pre-approved template
- This is why you create templates in Step 6

**The AI handles this automatically:**
- Within 24h: AI replies with full natural language
- After 24h: AI suggests which template to use, you send it manually OR set up auto-send for approved templates

## Botim Reality Check

**Botim does NOT have a public business API.** It is owned by Etisalat/du and is closed. You cannot:
- Programmatically send Botim messages
- Set up webhooks for Botim
- Integrate Botim with your AI

**What you CAN do:**
- When someone messages you on Botim, manually paste their info into your CRM
- The AI can then draft a reply for you to send back on Botim manually
- Use the dashboard to track Botim leads as "manual" source

**Recommendation:** For Dubai business, prioritize **WhatsApp** over Botim. Everyone who uses Botim also has WhatsApp. Add your WhatsApp number to your website and ads instead of Botim.

## Next Steps After Setup

1. Add your WhatsApp number to your website (WhatsApp click-to-chat link)
2. Add WhatsApp CTA to your Facebook/Instagram ads
3. Set up QR code on business cards linking to WhatsApp
4. Train your AI with Dubai-specific responses (e.g., "We offer Arabic and English websites")
