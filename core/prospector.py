"""
Lead Prospecting Engine
-----------------------
Find business owner contacts from external sources and import them into the CRM.

Supported sources:
  1. Google Maps (free HTTP scraping / SerpAPI / Places API)
  2. CSV bulk import (works with Apollo, Apify, LinkedIn, or any export)
  3. DuckDuckGo web search fallback
"""
import json
import re
import csv
import io
import time
import urllib.parse
import urllib.request
from datetime import datetime
from database import db
from core import crm
from config import GOOGLE_MAPS_API_KEY, SERPAPI_KEY


# ---------------------------------------------------------------------------
# 1.  Google Maps Search
# ---------------------------------------------------------------------------

def _valid_phone(s: str) -> str:
    """Return the phone string if it looks like a real phone number, else ''.
    Rejects dates (2025-01-06 / 20250106) and too-short/long digit runs."""
    if not s:
        return ""
    s = s.strip()
    if re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$', s):  # ISO date
        return ""
    digits = re.sub(r'\D', '', s)
    if len(digits) < 9 or len(digits) > 15:
        return ""
    if re.match(r'^(19|20)\d{6}$', digits):  # YYYYMMDD year-date
        return ""
    return s


def search_google_maps(query: str, location: str = "", limit: int = 20) -> list[dict]:
    """Search Google Maps for businesses matching query + location.

    Tries these methods in order:
      1. SerpAPI (if SERPAPI_KEY is set) — most reliable
      2. Google Places API (if GOOGLE_MAPS_API_KEY is set)
      3. Free scraping via Google Maps AJAX endpoint (no key needed)
    """
    full_query = f"{query} {location}".strip()

    if SERPAPI_KEY:
        results = _search_serpapi(full_query, limit)
    elif GOOGLE_MAPS_API_KEY:
        results = _search_places_api(full_query, limit)
    else:
        results = _search_maps_free(full_query, limit)

    # Cache results
    _log_search("google_maps", query, location, results)
    return results


def _search_serpapi(query: str, limit: int) -> list[dict]:
    """Use SerpAPI Google Maps endpoint."""
    try:
        params = urllib.parse.urlencode({
            "engine": "google_maps",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": min(limit, 20),
        })
        url = f"https://serpapi.com/search.json?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for place in data.get("local_results", [])[:limit]:
            results.append({
                "name": place.get("title", ""),
                "address": place.get("address", ""),
                "phone": place.get("phone", ""),
                "website": place.get("website", ""),
                "rating": place.get("rating"),
                "reviews": place.get("reviews"),
                "category": place.get("type", ""),
                "source": "google-maps",
            })
        return results
    except Exception as e:
        print(f"[Prospector] SerpAPI error: {e}")
        return _search_maps_free(query, limit)


def _search_places_api(query: str, limit: int) -> list[dict]:
    """Use Google Places Text Search API (free tier: up to $200/mo credit)."""
    try:
        params = urllib.parse.urlencode({
            "query": query,
            "key": GOOGLE_MAPS_API_KEY,
        })
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for place in data.get("results", [])[:limit]:
            # Get phone via Place Details
            phone = ""
            website = ""
            place_id = place.get("place_id")
            if place_id:
                phone, website = _get_place_details(place_id)

            results.append({
                "name": place.get("name", ""),
                "address": place.get("formatted_address", ""),
                "phone": phone,
                "website": website,
                "rating": place.get("rating"),
                "reviews": place.get("user_ratings_total"),
                "category": ", ".join(place.get("types", [])[:3]),
                "source": "google-maps",
            })
        return results
    except Exception as e:
        print(f"[Prospector] Places API error: {e}")
        return _search_maps_free(query, limit)


def _get_place_details(place_id: str) -> tuple:
    """Fetch phone & website from Place Details API."""
    try:
        params = urllib.parse.urlencode({
            "place_id": place_id,
            "fields": "formatted_phone_number,website",
            "key": GOOGLE_MAPS_API_KEY,
        })
        url = f"https://maps.googleapis.com/maps/api/place/details/json?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result = data.get("result", {})
        return result.get("formatted_phone_number", ""), result.get("website", "")
    except Exception:
        return "", ""


def _search_maps_free(query: str, limit: int) -> list[dict]:
    """Free Google Maps scraping fallback — no API key needed.

    Uses Google's public search pages to extract business data.
    Tries multiple strategies and falls back to DuckDuckGo.
    """
    results = []
    try:
        encoded = urllib.parse.quote(query)
        # Strategy 1: Google Local Pack search
        url = f"https://www.google.com/search?q={encoded}+near+me&tbm=lcl&num={limit}"
        req = urllib.request.Request(url, headers={
            "User-Agent": _get_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Try multiple CSS class selectors (Google changes these frequently)
        names = []
        for selector in ['dbg0pd', 'OSrXXb', 'qBF1Pd', 'lMbq3e']:
            names = re.findall(rf'class="[^"]*{selector}[^"]*"[^>]*>([^<]+)<', html)
            if names:
                break

        # Fallback: role="heading" elements
        if not names:
            names = re.findall(r'role="heading"[^>]*>([^<]+)<', html)
            names = [n for n in names if 3 < len(n) < 80]

        # Fallback: aria-label on links (filter noise)
        if not names:
            raw = re.findall(r'aria-label="([^"]+)"', html)
            names = [n for n in raw if 3 < len(n) < 80
                     and 'search' not in n.lower()
                     and 'google' not in n.lower()
                     and 'menu' not in n.lower()
                     and 'sign' not in n.lower()]

        # Extract phone numbers from the page
        phones = re.findall(r'[\+]?[\d\s\-\(\)]{7,18}', html)
        phone_numbers = []
        for p in phones:
            valid = _valid_phone(p)
            if valid and not re.sub(r'[^\d+]', '', valid).startswith('0000'):
                phone_numbers.append(valid)

        # Build results from what we can extract
        for i, name in enumerate(names[:limit]):
            if len(name) < 3 or len(name) > 100:
                continue
            results.append({
                "name": name.strip(),
                "address": "",
                "phone": phone_numbers[i] if i < len(phone_numbers) else "",
                "website": "",
                "rating": None,
                "reviews": None,
                "category": query.split(" in ")[0] if " in " in query else query,
                "source": "google-maps",
            })

        # If HTML scraping yields nothing, fall back to DuckDuckGo
        if not results:
            print("[Prospector] Google scraping yielded 0 results, falling back to DuckDuckGo")
            results = _search_duckduckgo(query, limit)

    except Exception as e:
        print(f"[Prospector] Free Maps scraping error: {e}")
        results = _search_duckduckgo(query, limit)

    return results


# Rotating User-Agent strings to avoid bot detection
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]
_ua_idx = 0

def _get_user_agent() -> str:
    """Rotate through User-Agent strings to reduce blocking."""
    global _ua_idx
    ua = _USER_AGENTS[_ua_idx % len(_USER_AGENTS)]
    _ua_idx += 1
    return ua


def _search_duckduckgo(query: str, limit: int) -> list[dict]:
    """DuckDuckGo HTML search for business info.

    Includes retry logic: DDG sometimes returns HTTP 202 with a bot-detection
    page instead of actual results.  We retry up to 3 times with a short delay.
    """
    results = []
    max_retries = 3

    for attempt in range(max_retries):
        try:
            encoded = urllib.parse.quote(f"{query} contact phone email")
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(url, headers={
                "User-Agent": _get_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://duckduckgo.com/",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.getcode()
                html = resp.read().decode("utf-8", errors="replace")

            # DDG returns 202 for bot-detection pages — retry
            if status == 202 or 'result__a' not in html:
                if attempt < max_retries - 1:
                    print(f"[Prospector] DDG attempt {attempt+1} got status {status} / no results, retrying...")
                    time.sleep(1.5 * (attempt + 1))
                    continue
                else:
                    print(f"[Prospector] DDG all {max_retries} attempts failed (status={status})")
                    break

            # Extract titles (text inside the result links)
            titles = re.findall(r'class="result__a"[^>]*>([^<]+)<', html)
            # Extract snippets
            snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a', html, re.DOTALL)
            # Extract actual URLs from href (DDG wraps them in a redirect)
            raw_urls = re.findall(r'class="result__url"[^>]*href="([^"]+)"', html)

            for i, title in enumerate(titles[:limit]):
                snippet = snippets[i] if i < len(snippets) else ""
                snippet_text = re.sub(r'<[^>]+>', '', snippet)

                # Try to extract phone from snippet (reject dates / junk)
                phone = ""
                for cand in re.findall(r'[\+]?[\d\s\-\(\)]{7,18}', snippet_text):
                    valid = _valid_phone(cand)
                    if valid:
                        phone = valid
                        break

                # Try to extract email
                email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', snippet_text)
                email = email_match.group() if email_match else ""

                # Extract actual website URL from DDG redirect
                website = ""
                if i < len(raw_urls):
                    url_match = re.search(r'uddg=([^&]+)', raw_urls[i])
                    if url_match:
                        website = urllib.parse.unquote(url_match.group(1))

                results.append({
                    "name": re.sub(r'<[^>]+>', '', title).strip(),
                    "address": "",
                    "phone": phone,
                    "email": email,
                    "website": website,
                    "rating": None,
                    "reviews": None,
                    "category": query.split(" in ")[0] if " in " in query else query,
                    "source": "web-search",
                })

            if results:
                print(f"[Prospector] DDG found {len(results)} results on attempt {attempt+1}")
                break

        except Exception as e:
            print(f"[Prospector] DuckDuckGo error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)

    return results


# ---------------------------------------------------------------------------
# 2.  CSV Bulk Import (Apollo / Apify / LinkedIn / generic)
# ---------------------------------------------------------------------------

# Common column name variations we auto-detect
_COLUMN_MAP = {
    "name":     ["name", "full name", "full_name", "contact name", "contact_name", "first name", "first_name", "person name"],
    "first_name": ["first name", "first_name", "firstname", "given name"],
    "last_name":  ["last name", "last_name", "lastname", "surname", "family name"],
    "email":    ["email", "email address", "email_address", "e-mail", "contact email", "work email", "work_email"],
    "phone":    ["phone", "phone number", "phone_number", "telephone", "mobile", "cell", "contact phone", "direct phone", "work phone"],
    "business": ["company", "company name", "company_name", "business", "business_name", "business name", "organization", "organisation"],
    "location": ["location", "city", "address", "full address", "city, state", "state", "country", "region", "headquarters"],
    "industry": ["industry", "sector", "vertical", "category", "business type"],
    "website":  ["website", "url", "company url", "company_url", "domain", "web", "company website"],
    "linkedin": ["linkedin", "linkedin url", "linkedin_url", "linkedin profile", "profile url", "person linkedin url"],
    "title":    ["title", "job title", "job_title", "position", "role", "designation"],
}


def parse_csv(file_content: str | bytes) -> dict:
    """Parse a CSV file and auto-detect column mapping.

    Returns:
        {
            "columns": [...detected columns...],
            "mapping": {"name": "Full Name", "email": "Email", ...},
            "rows": [{"name": "...", "email": "...", ...}, ...],
            "total": int,
            "raw_headers": [...original CSV headers...]
        }
    """
    if isinstance(file_content, bytes):
        # Try UTF-8 first, then latin-1
        try:
            file_content = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            file_content = file_content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(file_content))
    raw_headers = reader.fieldnames or []

    # Auto-detect column mapping
    mapping = {}
    for field, aliases in _COLUMN_MAP.items():
        for header in raw_headers:
            if header.lower().strip() in aliases:
                mapping[field] = header
                break

    # Parse rows with mapped columns
    rows = []
    for raw_row in reader:
        row = {}
        # Build name from first_name + last_name if no direct "name" column
        if "name" in mapping:
            row["name"] = (raw_row.get(mapping["name"]) or "").strip()
        elif "first_name" in mapping:
            first = (raw_row.get(mapping.get("first_name", "")) or "").strip()
            last = (raw_row.get(mapping.get("last_name", "")) or "").strip()
            row["name"] = f"{first} {last}".strip()
        else:
            # Try to find any column that looks like a name
            for h in raw_headers:
                val = (raw_row.get(h) or "").strip()
                if val and len(val) > 2 and " " in val and not "@" in val:
                    row["name"] = val
                    break
            if "name" not in row:
                row["name"] = ""

        for field in ["email", "phone", "business", "location", "industry", "website", "linkedin", "title"]:
            if field in mapping:
                row[field] = (raw_row.get(mapping[field]) or "").strip()
            else:
                row[field] = ""

        # Skip rows with no name and no email and no phone
        if not row["name"] and not row["email"] and not row["phone"]:
            continue

        rows.append(row)

    return {
        "columns": list(mapping.keys()),
        "mapping": mapping,
        "rows": rows,
        "total": len(rows),
        "raw_headers": raw_headers,
    }


# ---------------------------------------------------------------------------
# 3.  Duplicate Detection & CRM Import
# ---------------------------------------------------------------------------

def check_duplicates(prospects: list[dict]) -> list[dict]:
    """Check each prospect against existing CRM leads.

    Returns the same list with an 'is_duplicate' flag and 'duplicate_of' lead ID added.
    """
    for p in prospects:
        p["is_duplicate"] = False
        p["duplicate_of"] = None

        # Check by email
        email = p.get("email", "").strip()
        if email:
            existing = crm.get_lead_by_email(email)
            if existing:
                p["is_duplicate"] = True
                p["duplicate_of"] = existing["id"]
                continue

        # Check by phone
        phone = p.get("phone", "").strip()
        if phone:
            # Normalize: remove spaces, dashes, parens for comparison
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            existing = db.fetchone(
                "SELECT id FROM leads WHERE REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', '') = ?",
                (clean_phone,)
            )
            if existing:
                p["is_duplicate"] = True
                p["duplicate_of"] = existing["id"]

    return prospects


# ---------------------------------------------------------------------------
# Contact enrichment — scrape a prospect's website for phone/email
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
_MAILTO_RE = re.compile(r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', re.I)
_TEL_RE = re.compile(r'tel:\s*([+0-9][\d\s\-\(\)]{6,})', re.I)
_PHONE_RE = re.compile(r'(\+?\d[\d\s\-\(\)]{7,}\d)')

# Junk substrings that signal a fake/asset email, not a real contact.
_EMAIL_JUNK = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '@2x', '@3x',
               'example.com', 'domain.com', 'yourdomain', 'email.com',
               'sentry', 'wixpress', 'godaddy', 'cloudflare', 'schema.org',
               'sentry.io', 'wix.com', '.js', '.css')

def _fetch_page(url: str, timeout: int = 6) -> str:
    """Fetch a page's HTML (capped, best-effort)."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": _get_user_agent(),
            "Accept": "text/html,application/xhtml+xml",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(600_000)  # cap ~600KB
            charset = resp.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="ignore")
    except Exception:
        return ""

def _extract_email(html: str) -> str:
    for m in _MAILTO_RE.findall(html):
        e = m.strip().lower()
        if not any(j in e for j in _EMAIL_JUNK):
            return e
    for m in _EMAIL_RE.findall(html):
        e = m.strip().lower()
        if len(e) < 60 and not any(j in e for j in _EMAIL_JUNK):
            return e
    return ""

def _extract_phone(html: str) -> str:
    for m in _TEL_RE.findall(html):
        valid = _valid_phone(m)
        if valid:
            return valid
    for m in _PHONE_RE.findall(html):
        valid = _valid_phone(m)
        if valid:
            return valid
    return ""

def enrich_prospect(p: dict, timeout: int = 6) -> dict:
    """If a prospect has a website but is missing phone/email, scrape the site for contacts.
    Checks the homepage plus common contact pages. Mutates and returns the prospect."""
    website = (p.get("website") or "").strip()
    if not website or (p.get("email") and p.get("phone")):
        return p
    if not website.startswith("http"):
        website = "https://" + website
    base = website.rstrip("/")

    for url in (website, base + "/contact", base + "/contact-us", base + "/about"):
        if p.get("email") and p.get("phone"):
            break
        html = _fetch_page(url, timeout=timeout)
        if not html:
            continue
        if not p.get("email"):
            e = _extract_email(html)
            if e:
                p["email"] = e
        if not p.get("phone"):
            ph = _extract_phone(html)
            if ph:
                p["phone"] = ph
    p["enriched"] = True
    return p

def enrich_prospects(prospects: list[dict], max_sites: int = 15, timeout: int = 6) -> list[dict]:
    """Enrich prospects that have a website but are missing contacts (capped for speed)."""
    count = 0
    for p in prospects:
        if count >= max_sites:
            break
        if p.get("website") and not (p.get("email") and p.get("phone")):
            enrich_prospect(p, timeout=timeout)
            count += 1
    return prospects


def import_prospects(prospects: list[dict], source_tag: str = "prospected", enrich: bool = True) -> dict:
    """Import a list of prospects into the CRM as new leads.

    Args:
        prospects: List of prospect dicts with name, email, phone, business, etc.
        source_tag: Tag to add to imported leads for tracking.

    Returns:
        {"created": int, "skipped": int, "errors": int, "lead_ids": list}
    """
    created = 0
    skipped = 0
    errors = 0
    lead_ids = []

    for p in prospects:
        # Skip duplicates
        if p.get("is_duplicate"):
            skipped += 1
            continue

        # Enrich missing contacts from the prospect's website before saving.
        if enrich and p.get("website") and not (p.get("email") and p.get("phone")):
            try:
                enrich_prospect(p)
            except Exception as e:
                print(f"[Prospector] Enrich error for {p.get('name')}: {e}")

        try:
            name = p.get("name", "").strip()
            if not name:
                name = p.get("business", "Unknown")

            # Build notes from extra fields
            notes_parts = []
            if p.get("title"):
                notes_parts.append(f"Title: {p['title']}")
            if p.get("website"):
                notes_parts.append(f"Website: {p['website']}")
            if p.get("linkedin"):
                notes_parts.append(f"LinkedIn: {p['linkedin']}")
            if p.get("rating"):
                notes_parts.append(f"Rating: {p['rating']}")
            if p.get("reviews"):
                notes_parts.append(f"Reviews: {p['reviews']}")
            if p.get("address"):
                notes_parts.append(f"Address: {p['address']}")

            lead_id = crm.create_lead(
                name=name,
                business_name=p.get("business", "") or p.get("category", ""),
                phone=p.get("phone", ""),
                email=p.get("email", ""),
                source=p.get("source", "prospecting"),
                notes="\n".join(notes_parts),
                location=p.get("location", "") or p.get("address", ""),
                industry=p.get("industry", "") or p.get("category", ""),
                tags=source_tag,
            )
            lead_ids.append(lead_id)
            created += 1
        except Exception as e:
            print(f"[Prospector] Import error for {p.get('name')}: {e}")
            errors += 1

    return {
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "lead_ids": lead_ids,
    }


# ---------------------------------------------------------------------------
# 4.  Search History
# ---------------------------------------------------------------------------

def _log_search(search_type: str, query: str, location: str, results: list[dict]):
    """Save a prospecting search to the database for history/caching."""
    try:
        db.execute(
            """INSERT INTO prospect_searches (search_type, query, location, result_count, results_json)
               VALUES (?, ?, ?, ?, ?)""",
            (search_type, query, location, len(results), json.dumps(results, default=str))
        )
    except Exception as e:
        print(f"[Prospector] Log search error: {e}")


def get_search_history(limit: int = 20) -> list[dict]:
    """Get recent prospecting search history."""
    return db.fetchall(
        "SELECT id, search_type, query, location, result_count, imported_count, created_at FROM prospect_searches ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )


def get_search_results(search_id: int) -> list[dict]:
    """Get cached results for a previous search."""
    row = db.fetchone("SELECT results_json FROM prospect_searches WHERE id = ?", (search_id,))
    if row and row.get("results_json"):
        return json.loads(row["results_json"])
    return []
