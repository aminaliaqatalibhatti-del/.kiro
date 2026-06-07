"""
TripPilot AI — DataStore
JSON-file based persistence layer (no external database required).
Designed to be swapped out for SQLite/PostgreSQL in production.
"""
import os
import json
from threading import Lock
from trip_engine import DESTINATIONS

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(_DATA_DIR, exist_ok=True)

_USERS_FILE  = os.path.join(_DATA_DIR, 'users.json')
_TRIPS_FILE  = os.path.join(_DATA_DIR, 'trips.json')
_DESTS_FILE  = os.path.join(_DATA_DIR, 'destinations.json')

_lock = Lock()


def _read(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _write(path, data):
    with _lock:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class DataStore:
    # ── Users ─────────────────────────────────────────────────────────────────
    def save_user(self, user: dict):
        data = _read(_USERS_FILE)
        data[user['id']] = user
        _write(_USERS_FILE, data)

    def get_user(self, user_id: str):
        return _read(_USERS_FILE).get(user_id)

    def get_user_by_email(self, email: str):
        for u in _read(_USERS_FILE).values():
            if u.get('email', '').lower() == email.lower():
                return u
        return None

    # ── Trips ─────────────────────────────────────────────────────────────────
    def save_trip(self, trip: dict):
        data = _read(_TRIPS_FILE)
        data[trip['id']] = trip
        _write(_TRIPS_FILE, data)

    def get_trip(self, trip_id: str):
        return _read(_TRIPS_FILE).get(trip_id)

    def get_trips_by_user(self, user_id: str):
        all_trips = _read(_TRIPS_FILE).values()
        return [t for t in all_trips if t.get('user_id') == user_id]

    def delete_trip(self, trip_id: str):
        data = _read(_TRIPS_FILE)
        data.pop(trip_id, None)
        _write(_TRIPS_FILE, data)

    # ── Destinations ──────────────────────────────────────────────────────────
    def get_destinations(self):
        """Return destination catalogue (built from engine knowledge base)."""
        dests = []
        for key, d in DESTINATIONS.items():
            dests.append({
                'id': key.replace(' ', '_'),
                'name': key.title(),
                'country': d.get('country', ''),
                'continent': d.get('continent', ''),
                'description': d.get('description', ''),
                'tags': d.get('tags', []),
                'category': d.get('category', ''),
                'travel_style': d.get('travel_style', []),
                'group_types': d.get('group_types', []),
                'trip_duration': d.get('trip_duration', {'min': 2, 'ideal': 5, 'max': 14}),
                'difficulty': d.get('difficulty', 'moderate'),
                'safety': d.get('safety', 'moderate'),
                'image': d.get('image', 'default.jpg'),
                'daily_budget': d.get('daily_budget', {}),
                'best_months': d.get('best_months', []),
            })
        return dests

    def get_destination(self, dest_id: str):
        key = dest_id.replace('_', ' ')
        for d in self.get_destinations():
            if d['id'] == dest_id or d['name'].lower() == key:
                return d
        return None
