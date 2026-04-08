"""
Tender Monitoring SaaS - Configuration
All modules read settings from here
"""

# ============================================
# GENERAL SETTINGS
# ============================================
PROJECT_NAME = "Upphandling24"
LANGUAGE = "sv"
TIMEZONE = "Europe/Stockholm"

# ============================================
# FREE STACK CONFIG
# ============================================
# GitHub Actions (for running scrapers)
GITHUB_REPO = "your-username/tender-system"

# Google Sheets (for MVP database)
GOOGLE_SHEETS_ID = "your-sheet-id-here"
GOOGLE_SERVICE_ACCOUNT = {}  # Will be loaded from env

# Email (Gmail SMTP for MVP)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"

# AI (Gemini Flash for filtering)
GEMINI_API_KEY = "your-gemini-api-key"
GEMINI_MODEL = "gemini-2.0-flash"

# ============================================
# SCRAPER SOURCES
# ============================================
SOURCES = {
    "opic": {
        "url": "https://www.opic.com/sweden/",
        "enabled": True,
    },
    "visma": {
        "url": "https://tendsign.com/Search/AllAvailableContracts.aspx",
        "enabled": True,
    },
    "ted": {
        "url": "https://ted.europa.eu/en/search/result?Query=Sweden",
        "enabled": True,
    }
}

# ============================================
# FILTER SETTINGS
# ============================================
RELEVANCE_THRESHOLD = 0.7  # Minimum score to send alert

# ============================================
# EMAIL SETTINGS
# ============================================
EMAIL_FROM = "Upphandling24 <noreply@upphandling24.se>"
EMAIL_SUBJECT_TEMPLATE = "📢 {count} nya upphandlingar för dig"
DAILY_DIGEST_TIME = "08:00"  # Send daily digest at 8 AM

# ============================================
# PRICING (for future use)
# ============================================
PLANS = {
    "free": {
        "name": "Beta",
        "price": 0,
        "alerts_per_day": 10,
    },
    "pro": {
        "name": "Pro",
        "price": 249,  # SEK/month
        "alerts_per_day": float("inf"),
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 499,  # SEK/month
        "alerts_per_day": float("inf"),
    }
}
