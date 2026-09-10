"""
TripPilot AI — FastAPI Entry Point (Vercel)
Flask app.py ka replacement.
Vercel is file ko api/index.py ke roop mein serve karta hai.
"""
import sys
import os

# api/ folder ko Python path mein add karo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

import config
from routes.auth         import router as auth_router
from routes.trips        import router as trips_router
from routes.destinations import router as destinations_router
from routes.ai           import router as ai_router

# ── App init ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "TripPilot AI",
    description = "AI-powered travel planning API",
    version     = "2.0.0",
    docs_url    = "/api/docs",
    redoc_url   = None,
)

# ── Session middleware (cookie-based, same as Flask sessions) ─────────────────
app.add_middleware(
    SessionMiddleware,
    secret_key  = config.SECRET_KEY,
    session_cookie = "trippilot_session",
    max_age     = 86400 * 7,   # 7 days
    https_only  = False,        # True kar dena production mein custom domain ke saath
    same_site   = "lax",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
_allowed_origins = os.environ.get(
    'ALLOWED_ORIGINS',
    'http://127.0.0.1:5000,http://localhost:5000,http://localhost:3000'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins     = _allowed_origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router,         prefix="/api/auth",    tags=["auth"])
app.include_router(trips_router,        prefix="/api",         tags=["trips"])
app.include_router(destinations_router, prefix="/api",         tags=["destinations"])
app.include_router(ai_router,           prefix="/api/ai",      tags=["ai"])


# ── Route Planning (directly here, same as Flask app.py) ─────────────────────
@app.get("/api/routes")
async def get_routes(
    destination: str = "",
    transport:   str = "public",
    travelers:   str = "1",
    days:        str = "3",
):
    from trip_engine import TripEngine
    from utils       import safe_int

    destination = destination.strip()
    if not destination:
        return JSONResponse(
            {"status": "error", "message": "destination required"}, status_code=400
        )

    engine = TripEngine(
        destination = destination,
        days        = safe_int(days, default=3, min_val=1),
        budget      = 1000,
        travel_type = "solo",
        interests   = [],
        accommodation = "hotel",
        transport   = transport,
        start_date  = "",
        travelers   = safe_int(travelers, default=1, min_val=1),
    )
    return {"status": "success", "routes": engine.generate_routes()}


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "TripPilot AI", "version": "2.0.0"}


# ── Error handlers ────────────────────────────────────────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse({"status": "error", "message": "Not found"}, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse({"status": "error", "message": "Internal server error"}, status_code=500)


# ── Local dev server ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)
