"""
TripPilot AI — Destinations, Recommendations, Weather & Hotels (FastAPI)
"""
from datetime import datetime

from fastapi           import APIRouter, Request
from fastapi.responses import JSONResponse

from data_store      import DataStore
from trip_engine     import TripEngine, DESTINATIONS
from weather_service import get_forecast
from places_service  import get_hotels as get_curated_hotels
from utils           import safe_int

router = APIRouter()
db     = DataStore()


# ── Destinations ──────────────────────────────────────────────────────────────
@router.get("/destinations")
async def get_destinations(q: str = "", category: str = ""):
    search = q.lower()
    cat    = category.lower()
    dests  = db.get_destinations()

    if search:
        dests = [d for d in dests
                 if search in d['name'].lower()
                 or search in d['country'].lower()
                 or search in d.get('category', '').lower()
                 or any(search in t for t in d.get('tags', []))]
    if cat:
        dests = [d for d in dests if cat in d.get('category', '').lower()]

    return JSONResponse({"status": "success", "destinations": dests})


@router.get("/destinations/{dest_id}")
async def get_destination(dest_id: str):
    dest = db.get_destination(dest_id)
    if not dest:
        return JSONResponse({"status": "error", "message": "Destination not found"}, status_code=404)
    return JSONResponse({"status": "success", "destination": dest})


# ── Recommendations ───────────────────────────────────────────────────────────
@router.post("/recommendations")
async def get_recommendations(request: Request):
    data        = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    interests   = data.get('interests', [])
    budget_lv   = data.get('budget_level', 'medium')
    travel_type = data.get('travel_type', 'solo')
    travelers   = safe_int(data.get('travelers', 1), min_val=1)
    start_date  = data.get('start_date', '')
    trip_days   = safe_int(data.get('days', 5), min_val=1)
    category    = (data.get('category') or '').strip()

    travel_month = None
    if start_date:
        try:
            travel_month = int(start_date.split('-')[1])
        except (IndexError, ValueError):
            travel_month = datetime.today().month

    engine = TripEngine(
        destination   = 'paris',
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
        interests       = interests,
        budget_level    = budget_lv,
        travel_type     = travel_type,
        travelers       = travelers,
        travel_month    = travel_month,
        trip_days       = trip_days,
        category_filter = category or None,
    )
    return JSONResponse({"status": "success", "recommendations": recs})


# ── Weather ───────────────────────────────────────────────────────────────────
@router.get("/weather")
async def get_weather(destination: str = "", days: str = "5", start_date: str = ""):
    destination = destination.strip()
    if not destination:
        return JSONResponse({"status": "error", "message": "destination required"}, status_code=400)
    weather = get_forecast(destination, safe_int(days, default=5, min_val=1, max_val=14), start_date)
    return JSONResponse({"status": "success", "weather": weather})


# ── Hotels ────────────────────────────────────────────────────────────────────
@router.get("/hotels")
async def get_hotels(
    destination:   str = "",
    budget_type:   str = "medium",
    accommodation: str = "hotel",
):
    destination = destination.strip()
    if not destination:
        return JSONResponse({"status": "error", "message": "destination required"}, status_code=400)
    hotels = get_curated_hotels(destination, budget_type, accommodation)
    return JSONResponse({"status": "success", "hotels": hotels})
