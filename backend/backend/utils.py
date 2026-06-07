"""
TripPilot AI — Shared Utilities
Single source for helpers used across multiple modules.
"""
from werkzeug.security import generate_password_hash, check_password_hash


# ── Auth helpers ──────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Returns a salted bcrypt-style hash via werkzeug (pbkdf2:sha256)."""
    return generate_password_hash(password)


def verify_password(password: str, pw_hash: str) -> bool:
    """Constant-time comparison of password against stored hash."""
    return check_password_hash(pw_hash, password)


# ── Request helpers ───────────────────────────────────────────────────────────
def validate_required(data: dict, fields: list) -> list:
    """Returns list of missing field names."""
    return [f for f in fields if not data.get(f)]


def safe_int(value, default: int = 0, min_val: int = None, max_val: int = None) -> int:
    """Parse int safely, clamping to optional bounds."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    if min_val is not None:
        v = max(min_val, v)
    if max_val is not None:
        v = min(max_val, v)
    return v


def safe_float(value, default: float = 0.0) -> float:
    """Parse float safely, stripping commas."""
    try:
        return float(str(value).replace(',', ''))
    except (TypeError, ValueError):
        return default


# ── Response helpers ──────────────────────────────────────────────────────────
def safe_user(u: dict) -> dict:
    """Strip password from user dict before sending to client."""
    return {k: v for k, v in u.items() if k != 'password'}


# ── Budget helpers ─────────────────────────────────────────────────────────────
def budget_level(budget: float, days: int, travelers: int) -> str:
    """Classify budget as low / medium / high based on per-person daily spend."""
    per_person_per_day = budget / max(days, 1) / max(travelers, 1)
    if per_person_per_day < 80:
        return 'low'
    if per_person_per_day < 250:
        return 'medium'
    return 'high'
