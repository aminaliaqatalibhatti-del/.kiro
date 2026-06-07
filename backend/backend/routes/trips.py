"""
TripPilot AI — Trips, Expenses & Analytics Routes Blueprint
"""
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request, session

from data_store      import DataStore
from trip_engine     import TripEngine
from weather_service import get_forecast
from places_service  import get_hotels as get_curated_hotels
from utils           import validate_required, safe_int, safe_float, budget_level

trips_bp = Blueprint('trips', __name__, url_prefix='/api')
db       = DataStore()


# ── Trip planning ─────────────────────────────────────────────────────────────
@trips_bp.route('/trips/plan', methods=['POST'])
def plan_trip():
    data    = request.get_json() or {}
    missing = validate_required(
        data, ['traveler_name', 'destination', 'start_date', 'days', 'budget', 'travel_type']
    )
    if missing:
        return jsonify({'status': 'error', 'message': f'Missing: {", ".join(missing)}'}), 400

    days   = safe_int(data['days'],   default=5, min_val=1, max_val=30)
    budget = safe_float(data['budget'])
    if budget <= 0:
        return jsonify({'status': 'error', 'message': 'Budget must be greater than 0'}), 400

    engine = TripEngine(
        destination    = data['destination'],
        days           = days,
        budget         = budget,
        travel_type    = data.get('travel_type', 'solo'),
        interests      = data.get('interests', []),
        accommodation  = data.get('accommodation', 'hotel'),
        transport      = data.get('transport', 'public'),
        start_date     = data['start_date'],
        travelers      = safe_int(data.get('travelers', 1), min_val=1, max_val=20),
        traveler_name  = data.get('traveler_name', ''),
        traveler_age   = data.get('traveler_age'),
        start_location = data.get('start_location', ''),
    )
    plan = engine.generate_full_plan()

    # Enrich with curated hotel data
    bl          = budget_level(budget, days, safe_int(data.get('travelers', 1), min_val=1))
    real_hotels = get_curated_hotels(
        destination        = data['destination'],
        budget_level       = bl,
        accommodation_pref = data.get('accommodation', 'hotel'),
    )
    if real_hotels:
        plan['hotels'] = real_hotels[:3]

    # Enrich with climate/live weather
    real_weather = get_forecast(
        city       = data['destination'],
        days       = days,
        start_date = data['start_date'],
    )
    if real_weather:
        plan['weather_overview'] = real_weather
        for day in plan.get('itinerary', []):
            idx = day['day'] - 1
            if idx < len(real_weather):
                day['weather'] = real_weather[idx]

    trip_id = str(uuid.uuid4())
    trip_record = {
        'id':            trip_id,
        'user_id':       session.get('user_id', 'guest'),
        'traveler_name': data['traveler_name'],
        'destination':   data['destination'],
        'start_date':    data['start_date'],
        'days':          days,
        'budget':        budget,
        'travel_type':   data['travel_type'],
        'travelers':     safe_int(data.get('travelers', 1), min_val=1),
        'interests':     data.get('interests', []),
        'plan':          plan,
        'created_at':    datetime.utcnow().isoformat(),
        'status':        'active',
        'expenses':      [],
    }
    db.save_trip(trip_record)
    return jsonify({'status': 'success', 'trip_id': trip_id, 'plan': plan})


@trips_bp.route('/trips', methods=['GET'])
def list_trips():
    uid   = session.get('user_id', 'guest')
    trips = db.get_trips_by_user(uid)
    summary = [
        {
            'id':          t['id'],
            'destination': t['destination'],
            'start_date':  t['start_date'],
            'days':        t['days'],
            'budget':      t['budget'],
            'travel_type': t['travel_type'],
            'travelers':   t.get('travelers', 1),
            'status':      t.get('status', 'active'),
            'created_at':  t.get('created_at', ''),
        }
        for t in trips
    ]
    return jsonify({'status': 'success', 'trips': summary})


@trips_bp.route('/trips/<trip_id>', methods=['GET'])
def get_trip(trip_id):
    trip = db.get_trip(trip_id)
    if not trip:
        return jsonify({'status': 'error', 'message': 'Trip not found'}), 404
    return jsonify({'status': 'success', 'trip': trip})


@trips_bp.route('/trips/<trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    db.delete_trip(trip_id)
    return jsonify({'status': 'success'})


# ── Expenses ──────────────────────────────────────────────────────────────────
@trips_bp.route('/trips/<trip_id>/expenses', methods=['GET'])
def get_expenses(trip_id):
    trip = db.get_trip(trip_id)
    if not trip:
        return jsonify({'status': 'error', 'message': 'Trip not found'}), 404
    return jsonify({'status': 'success', 'expenses': trip.get('expenses', [])})


@trips_bp.route('/trips/<trip_id>/expenses', methods=['POST'])
def add_expense(trip_id):
    trip    = db.get_trip(trip_id)
    if not trip:
        return jsonify({'status': 'error', 'message': 'Trip not found'}), 404

    data    = request.get_json() or {}
    missing = validate_required(data, ['category', 'amount', 'description'])
    if missing:
        return jsonify({'status': 'error', 'message': f'Missing: {", ".join(missing)}'}), 400

    amount = safe_float(data['amount'])
    if amount <= 0:
        return jsonify({'status': 'error', 'message': 'Amount must be greater than 0'}), 400

    expense = {
        'id':          str(uuid.uuid4()),
        'category':    data['category'],
        'amount':      amount,
        'description': data['description'],
        'date':        data.get('date', datetime.utcnow().strftime('%Y-%m-%d')),
    }
    expenses = trip.get('expenses', [])
    expenses.append(expense)
    trip['expenses'] = expenses
    db.save_trip(trip)
    return jsonify({'status': 'success', 'expense': expense}), 201


@trips_bp.route('/trips/<trip_id>/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(trip_id, expense_id):
    trip = db.get_trip(trip_id)
    if not trip:
        return jsonify({'status': 'error', 'message': 'Trip not found'}), 404
    trip['expenses'] = [e for e in trip.get('expenses', []) if e['id'] != expense_id]
    db.save_trip(trip)
    return jsonify({'status': 'success'})


@trips_bp.route('/trips/<trip_id>/expenses/<expense_id>', methods=['PUT'])
def update_expense(trip_id, expense_id):
    """Edit an existing expense — category, description, amount, date."""
    trip = db.get_trip(trip_id)
    if not trip:
        return jsonify({'status': 'error', 'message': 'Trip not found'}), 404

    data    = request.get_json() or {}
    expenses = trip.get('expenses', [])
    target   = next((e for e in expenses if e['id'] == expense_id), None)
    if not target:
        return jsonify({'status': 'error', 'message': 'Expense not found'}), 404

    # Only update provided fields
    if 'category' in data:
        target['category'] = data['category']
    if 'description' in data:
        desc = (data['description'] or '').strip()
        if not desc:
            return jsonify({'status': 'error', 'message': 'Description cannot be empty'}), 400
        target['description'] = desc
    if 'amount' in data:
        amount = safe_float(data['amount'])
        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'Amount must be greater than 0'}), 400
        target['amount'] = amount
    if 'date' in data:
        target['date'] = data['date']

    target['updated_at'] = datetime.utcnow().strftime('%Y-%m-%d')
    db.save_trip(trip)
    return jsonify({'status': 'success', 'expense': target})


# ── Analytics ─────────────────────────────────────────────────────────────────
@trips_bp.route('/analytics/summary', methods=['GET'])
def analytics_summary():
    uid    = session.get('user_id', 'guest')
    trips  = db.get_trips_by_user(uid)

    total_spent     = 0.0
    destinations    = set()
    category_totals = {}
    total_days      = 0

    for t in trips:
        destinations.add(t.get('destination', ''))
        total_days += t.get('days', 0)
        for exp in t.get('expenses', []):
            amt = safe_float(exp.get('amount', 0))
            total_spent += amt
            cat = exp.get('category', 'Other')
            category_totals[cat] = category_totals.get(cat, 0) + amt

    return jsonify({
        'status':  'success',
        'summary': {
            'total_trips':          len(trips),
            'total_spent':          round(total_spent, 2),
            'destinations_visited': len(destinations),
            'total_days':           total_days,
            'spending_by_category': category_totals,
        },
    })
