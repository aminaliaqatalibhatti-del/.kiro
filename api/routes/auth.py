"""
TripPilot AI — Auth Routes (FastAPI)
Flask Blueprint -> FastAPI Router
"""
import re
import uuid
from datetime import datetime

from fastapi          import APIRouter, Request
from fastapi.responses import JSONResponse

from data_store import DataStore
from utils      import hash_password, verify_password, safe_user

router = APIRouter()
db     = DataStore()

_EMAIL_RE     = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_MAX_NAME     = 120
_MAX_EMAIL    = 254
_MAX_PASSWORD = 128


@router.post("/register")
async def register(request: Request):
    data     = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    name     = (data.get('name')     or '').strip()[:_MAX_NAME]
    email    = (data.get('email')    or '').strip().lower()[:_MAX_EMAIL]
    password = (data.get('password') or '')[:_MAX_PASSWORD]

    if not name or not email or not password:
        return JSONResponse({"status": "error", "message": "All fields required"}, status_code=400)
    if not _EMAIL_RE.match(email):
        return JSONResponse({"status": "error", "message": "Invalid email address"}, status_code=400)
    if len(password) < 6:
        return JSONResponse({"status": "error", "message": "Password must be at least 6 characters"}, status_code=400)
    if db.get_user_by_email(email):
        return JSONResponse({"status": "error", "message": "Email already registered"}, status_code=409)

    user_id = str(uuid.uuid4())
    user = {
        'id':          user_id,
        'name':        name,
        'email':       email,
        'password':    hash_password(password),
        'created_at':  datetime.utcnow().isoformat(),
        'avatar':      name[0].upper(),
        'trips_count': 0,
    }
    db.save_user(user)
    request.session['user_id'] = user_id
    return JSONResponse({"status": "success", "user": safe_user(user)}, status_code=201)


@router.post("/login")
async def login(request: Request):
    data     = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    email    = (data.get('email')    or '').strip().lower()[:_MAX_EMAIL]
    password = (data.get('password') or '')[:_MAX_PASSWORD]

    user = db.get_user_by_email(email)
    if not user or not verify_password(password, user['password']):
        return JSONResponse({"status": "error", "message": "Invalid credentials"}, status_code=401)

    request.session['user_id'] = user['id']
    return JSONResponse({"status": "success", "user": safe_user(user)})


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse({"status": "success"})


@router.get("/me")
async def me(request: Request):
    uid = request.session.get('user_id')
    if not uid:
        return JSONResponse({"status": "error", "message": "Not authenticated"}, status_code=401)
    user = db.get_user(uid)
    if not user:
        return JSONResponse({"status": "error", "message": "User not found"}, status_code=404)
    return JSONResponse({"status": "success", "user": safe_user(user)})
