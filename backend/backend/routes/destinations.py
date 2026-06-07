"""
TripPilot AI — Destinations, Recommendations, Weather & Hotels Blueprint
"""
from datetime import datetime
from flask import Blueprint, jsonify, request

from data_store      import DataStore
from trip_engine     import TripEngine, DESTINATIONS
from weather_service import get_forecast
from places_service  import get_hotels as get_curated_hotels
from utils           import safe_int

destinations_bp = Blueprint('destinations', __name__, url_prefix='/api')
db              = DataStore()


# ── Destinations ──────────────────────────────────────────────────────────────
@destinations_bp.route('/destinations', methods=['GET'])
def get_destinations():
    search   = (request.args.get('q') or '').lower()
    category = (request.args.get('category') or '').lower()
    dests    = db.get_destinations()
    if search:
        dests = [d for d in dests
                 if search in d['name'].lower() or search in d['country'].lower()
                 or search in d.get('category','').lower()
                 or any(search in t for t in d.get('tags',[]))]
    if category:
        dests = [d for d in dests if category in d.get('category','').lower()]
    return jsonify({'status': 'success', 'destinations': dests})


@destinations_bp.route('/destinations/<dest_id>', methods=['GET'])
def get_destination(dest_id):
    dest = db.get_destination(dest_id)
    if not dest:
        return jsonify({'status': 'error', 'message': 'Destination not found'}), 404
    return jsonify({'status': 'success', 'destination': dest})


# ── Recommendations ───────────────────────────────────────────────────────────
@destinations_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    data         = request.get_json() or {}
    interests    = data.get('interests', [])
    budget_lv    = data.get('budget_level', 'medium')
    travel_type  = data.get('travel_type', 'solo')
    travelers    = safe_int(data.get('travelers', 1), min_val=1)
    start_date   = data.get('start_date', '')
    trip_days    = safe_int(data.get('days', 5), min_val=1)
    category     = (data.get('category') or '').strip()

    # Derive travel_month from start_date if provided
    travel_month = None
    if start_date:
        try:
            travel_month = int(start_date.split('-')[1])
        except (IndexError, ValueError):
            travel_month = datetime.today().month

    # Use a minimal engine instance solely to call recommend_destinations
    # All profile fields are passed so scoring uses full context
    engine = TripEngine(
        destination   = 'paris',       # stub — recommendations scan all destinations
        days          = trip_days,
        budget        = {'low': 300, 'medium': 1000, 'high': 5000}.get(budget_lv, 1000),
        travel_type   = travel_type,
        interests     = interests,
        accommodation = 'hotel',
        transport     = 'public',
        start_date    = start_date,
        travelers     = travelers,
    )
    recs = engine.recommend_destinations(
        interests        = interests,
        budget_level     = budget_lv,
        travel_type      = travel_type,
        travelers        = travelers,
        travel_month     = travel_month,
        trip_days        = trip_days,
        category_filter  = category or None,
    )
    return jsonify({'status': 'success', 'recommendations': recs})


# ── Weather ───────────────────────────────────────────────────────────────────
@destinations_bp.route('/weather', methods=['GET'])
def get_weather():
    destination = request.args.get('destination', '').strip()
    days        = safe_int(request.args.get('days', 5), min_val=1, max_val=14)
    start_date  = request.args.get('start_date', '')

    if not destination:
        return jsonify({'status': 'error', 'message': 'destination required'}), 400

    weather = get_forecast(destination, days, start_date)
    return jsonify({'status': 'success', 'weather': weather})


# ── Hotels ────────────────────────────────────────────────────────────────────
@destinations_bp.route('/hotels', methods=['GET'])
def get_hotels():
    destination   = request.args.get('destination', '').strip()
    budget_type   = request.args.get('budget_type', 'medium')
    accommodation = request.args.get('accommodation', 'hotel')

    if not destination:
        return jsonify({'status': 'error', 'message': 'destination required'}), 400

    hotels = get_curated_hotels(destination, budget_type, accommodation)
    return jsonify({'status': 'success', 'hotels': hotels})
