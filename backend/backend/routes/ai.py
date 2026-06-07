"""
TripPilot AI — AI Advisor Routes Blueprint
Handles: advisory, chat, compare
"""
from flask import Blueprint, jsonify, request

from trip_engine import DESTINATIONS
from ai_advisor  import AIAdvisor, DEST_ADVISOR, build_comparison_rec
from utils       import safe_int, safe_float, budget_level

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/advisory', methods=['POST'])
def ai_advisory():
    data = request.get_json() or {}
    if not data.get('destination'):
        return jsonify({'status': 'error', 'message': 'destination required'}), 400
    try:
        advisor = AIAdvisor(data)
        report  = advisor.full_advisory()
        return jsonify({'status': 'success', 'advisory': report})
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@ai_bp.route('/chat', methods=['POST'])
def ai_chat():
    data     = request.get_json() or {}
    question = (data.get('question') or '').strip()
    context  = data.get('context') or {}

    if not question:
        return jsonify({'status': 'error', 'message': 'question required'}), 400
    try:
        advisor = AIAdvisor(context)
        answer  = advisor.answer_question(question)
        return jsonify({'status': 'success', 'answer': answer})
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@ai_bp.route('/compare', methods=['POST'])
def ai_compare():
    data  = request.get_json() or {}
    dest1 = (data.get('destination_a') or '').strip().lower()
    dest2 = (data.get('destination_b') or '').strip().lower()

    if not dest1 or not dest2:
        return jsonify({'status': 'error',
                        'message': 'destination_a and destination_b required'}), 400

    advisor_a = AIAdvisor({**data, 'destination': dest1})
    advisor_b = AIAdvisor({**data, 'destination': dest2})
    verdict_a = advisor_a._destination_verdict()
    verdict_b = advisor_b._destination_verdict()

    da      = DESTINATIONS.get(dest1, {})
    db_dest = DESTINATIONS.get(dest2, {})
    days    = safe_int(data.get('days', 5), min_val=1)
    budget  = safe_float(data.get('budget', 1000))

    def est_cost(dest_data):
        bl = budget_level(budget, days, safe_int(data.get('travelers', 1), min_val=1))
        return dest_data.get('daily_budget', {}).get(bl, 150) * days

    comparison = {
        'destination_a': {
            'name':                dest1.title(),
            'verdict':             verdict_a,
            'estimated_trip_cost': est_cost(da),
            'tags':                da.get('tags', []),
            'difficulty':          da.get('difficulty', 'moderate'),
            'safety':              da.get('safety', 'moderate'),
            'best_months':         da.get('best_months', []),
            'pro_tips':            DEST_ADVISOR.get(dest1, {}).get('pro_tips', [])[:2],
        },
        'destination_b': {
            'name':                dest2.title(),
            'verdict':             verdict_b,
            'estimated_trip_cost': est_cost(db_dest),
            'tags':                db_dest.get('tags', []),
            'difficulty':          db_dest.get('difficulty', 'moderate'),
            'safety':              db_dest.get('safety', 'moderate'),
            'best_months':         db_dest.get('best_months', []),
            'pro_tips':            DEST_ADVISOR.get(dest2, {}).get('pro_tips', [])[:2],
        },
        'recommendation': build_comparison_rec(dest1, dest2, da, db_dest, data),
    }
    return jsonify({'status': 'success', 'comparison': comparison})
