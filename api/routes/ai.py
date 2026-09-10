"""
TripPilot AI — AI Advisor Routes (FastAPI)
"""
from fastapi           import APIRouter, Request
from fastapi.responses import JSONResponse

from trip_engine import DESTINATIONS
from ai_advisor  import AIAdvisor, DEST_ADVISOR, build_comparison_rec
from utils       import safe_int, safe_float, budget_level

router = APIRouter()


@router.post("/advisory")
async def ai_advisory(request: Request):
    data = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    if not data.get('destination'):
        return JSONResponse({"status": "error", "message": "destination required"}, status_code=400)
    try:
        advisor = AIAdvisor(data)
        report  = advisor.full_advisory()
        return JSONResponse({"status": "success", "advisory": report})
    except Exception as exc:
        return JSONResponse({"status": "error", "message": str(exc)}, status_code=500)


@router.post("/chat")
async def ai_chat(request: Request):
    data     = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    question = (data.get('question') or '').strip()
    context  = data.get('context') or {}

    if not question:
        return JSONResponse({"status": "error", "message": "question required"}, status_code=400)
    try:
        advisor = AIAdvisor(context)
        answer  = advisor.answer_question(question)
        return JSONResponse({"status": "success", "answer": answer})
    except Exception as exc:
        return JSONResponse({"status": "error", "message": str(exc)}, status_code=500)


@router.post("/compare")
async def ai_compare(request: Request):
    data  = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    dest1 = (data.get('destination_a') or '').strip().lower()
    dest2 = (data.get('destination_b') or '').strip().lower()

    if not dest1 or not dest2:
        return JSONResponse(
            {"status": "error", "message": "destination_a and destination_b required"},
            status_code=400,
        )

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
    return JSONResponse({"status": "success", "comparison": comparison})
