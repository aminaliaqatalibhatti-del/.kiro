"""
TripPilot AI — Configuration
Set environment variables to enable live API integrations.
Without keys the app falls back to high-fidelity offline data.
"""
import os

# ── Weather ───────────────────────────────────────────────────────────────────
# Free tier: https://openweathermap.org/api  (no credit card required)
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')

# ── Maps / Geocoding ──────────────────────────────────────────────────────────
# OpenCage is free for 2 500 req/day: https://opencagedata.com/
OPENCAGE_API_KEY = os.environ.get('OPENCAGE_API_KEY', '')

# ── Currency ──────────────────────────────────────────────────────────────────
# Free: https://open.er-api.com/  (no key required for USD base)
EXCHANGE_RATE_BASE = 'USD'

# ── App ───────────────────────────────────────────────────────────────────────
SECRET_KEY   = os.environ.get('SECRET_KEY', 'trippilot-dev-secret-2024')
DEBUG        = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'  # OFF by default — set FLASK_DEBUG=true for dev
CACHE_TTL    = int(os.environ.get('CACHE_TTL', '1800'))   # 30-minute cache

# ── Feature flags ─────────────────────────────────────────────────────────────
USE_LIVE_WEATHER  = bool(OPENWEATHER_API_KEY)
USE_LIVE_GEOCODE  = bool(OPENCAGE_API_KEY)
