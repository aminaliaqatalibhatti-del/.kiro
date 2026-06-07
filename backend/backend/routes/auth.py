"""
TripPilot AI — Auth Routes Blueprint
Handles: register, login, logout, /me
"""
import re
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request, session

from data_store import DataStore
from utils      import hash_password, verify_password, validate_required, safe_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
db      = DataStore()

# ── Input limits ──────────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_MAX_NAME     = 120
_MAX_EMAIL    = 254   # RFC 5321
_MAX_PASSWORD = 128


@auth_bp.route('/register', methods=['POST'])
def register():
    data     = request.get_json() or {}
    name     = (data.get('name')     or '').strip()[:_MAX_NAME]
    email    = (data.get('email')    or '').strip().lower()[:_MAX_EMAIL]
    password = (data.get('password') or '')[:_MAX_PASSWORD]

    if not name or not email or not password:
        return jsonify({'status': 'error', 'message': 'All fields required'}), 400
    if not _EMAIL_RE.match(email):
        return jsonify({'status': 'error', 'message': 'Invalid email address'}), 400
    if len(password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
    if db.get_user_by_email(email):
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 409

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
    session['user_id'] = user_id
    return jsonify({'status': 'success', 'user': safe_user(user)}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data     = request.get_json() or {}
    email    = (data.get('email')    or '').strip().lower()[:_MAX_EMAIL]
    password = (data.get('password') or '')[:_MAX_PASSWORD]

    user = db.get_user_by_email(email)
    if not user or not verify_password(password, user['password']):
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    session['user_id'] = user['id']
    return jsonify({'status': 'success', 'user': safe_user(user)})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})


@auth_bp.route('/me', methods=['GET'])
def me():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    user = db.get_user(uid)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    return jsonify({'status': 'success', 'user': safe_user(user)})
