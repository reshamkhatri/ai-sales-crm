import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI (or any OpenAI-compatible provider)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# Optional base URL to use a different provider — DeepSeek, Together, Groq, OpenRouter, local, etc.
# Leave blank for OpenAI. For DeepSeek set: https://api.deepseek.com
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")

# Meta / Facebook
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")
META_PAGE_ID = os.getenv("META_PAGE_ID", "")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "fb_webhook_123")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
META_INSTAGRAM_ID = os.getenv("META_INSTAGRAM_ID", "")  # Instagram Business Account ID

# WhatsApp Cloud API (separate from Meta, but same developer account)
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")  # From WhatsApp Business Manager
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")  # Often same as META_ACCESS_TOKEN
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "wa_webhook_123")

# Email (Gmail SMTP + IMAP)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # App password, not your Gmail password
EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/sales_assistant.db")

# Dashboard
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))

# Agency Info
AGENCY_NAME = os.getenv("AGENCY_NAME", "Dubai Web Design Agency")
AGENCY_SERVICES = os.getenv("AGENCY_SERVICES", "Web Design, SEO, Landing Pages")
AGENCY_LOCATION = os.getenv("AGENCY_LOCATION", "Dubai, UAE")

# Prospecting (all optional — free scraping works without keys)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")  # For Places API (free tier available)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")  # Optional: SerpAPI for reliable Google Maps scraping

# Lead Finder browser extension integration.
# The extension pushes Google-Maps-scraped leads to /api/leads/ingest with an
# "x-api-key" header. Leave blank to accept any non-empty key (easy local use);
# set a value to lock the endpoint to that exact key.
LEADFINDER_API_KEY = os.getenv("LEADFINDER_API_KEY", "")

# Multi-channel config
ACTIVE_CHANNELS = os.getenv("ACTIVE_CHANNELS", "facebook,whatsapp,instagram,email").split(",")
