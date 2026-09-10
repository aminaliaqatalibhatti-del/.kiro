"""
TripPilot AI — Configuration
Environment variables se config load karta hai.
Without API keys, app offline fallback data use karta hai.
"""
import os

# ── Weather ───────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')

# ── Maps / Geocoding ──────────────────────────────────────────────────────────
OPENCAGE_API_KEY = os.environ.get('OPENCAGE_API_KEY', '')

# ── Currency ──────────────────────────────────────────────────────────────────
EXCHANGE_RATE_BASE = 'USD'

# ── App ───────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'trippilot-dev-secret-2024')
DEBUG      = os.environ.get('DEBUG', 'false').lower() == 'true'
CACHE_TTL  = int(os.environ.get('CACHE_TTL', '1800'))

# ── Feature flags ─────────────────────────────────────────────────────────────
USE_LIVE_WEATHER = bool(OPENWEATHER_API_KEY)
USE_LIVE_GEOCODE = bool(OPENCAGE_API_KEY)
