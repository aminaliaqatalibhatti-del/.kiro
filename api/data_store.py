"""
TripPilot AI — DataStore (Vercel-compatible)
Vercel mein filesystem read-only hai, isliye in-memory storage use karta hai.
Production mein MongoDB Atlas ya PlanetScale se replace kar sakte hain.
"""
from threading import Lock

# ── In-memory stores ──────────────────────────────────────────────────────────
_users: dict  = {}   # { user_id: user_dict }
_trips: dict  = {}   # { trip_id: trip_dict }
_lock         = Lock()


class DataStore:
    # ── Users ─────────────────────────────────────────────────────────────────
    def save_user(self, user: dict):
        with _lock:
            _users[user['id']] = user

    def get_user(self, user_id: str):
        return _users.get(user_id)

    def get_user_by_email(self, email: str):
        for u in _users.values():
            if u.get('email', '').lower() == email.lower():
                return u
        return None

    # ── Trips ─────────────────────────────────────────────────────────────────
    def save_trip(self, trip: dict):
        with _lock:
            _trips[trip['id']] = trip

    def get_trip(self, trip_id: str):
        return _trips.get(trip_id)

    def get_trips_by_user(self, user_id: str):
        return [t for t in _trips.values() if t.get('user_id') == user_id]

    def delete_trip(self, trip_id: str):
        with _lock:
            _trips.pop(trip_id, None)

    # ── Destinations ──────────────────────────────────────────────────────────
    def get_destinations(self):
        """Return destination catalogue from engine knowledge base."""
        from trip_engine import DESTINATIONS
        dests = []
        for key, d in DESTINATIONS.items():
            dests.append({
                'id':           key.replace(' ', '_'),
                'name':         key.title(),
                'country':      d.get('country', ''),
                'continent':    d.get('continent', ''),
                'description':  d.get('description', ''),
                'tags':         d.get('tags', []),
                'category':     d.get('category', ''),
                'travel_style': d.get('travel_style', []),
                'group_types':  d.get('group_types', []),
                'trip_duration':d.get('trip_duration', {'min': 2, 'ideal': 5, 'max': 14}),
                'difficulty':   d.get('difficulty', 'moderate'),
                'safety':       d.get('safety', 'moderate'),
                'image':        d.get('image', 'default.jpg'),
                'daily_budget': d.get('daily_budget', {}),
                'best_months':  d.get('best_months', []),
            })
        return dests

    def get_destination(self, dest_id: str):
        key = dest_id.replace('_', ' ')
        for d in self.get_destinations():
            if d['id'] == dest_id or d['name'].lower() == key:
                return d
        return None
