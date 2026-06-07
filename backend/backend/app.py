"""
TripPilot AI — Application Entry Point
Registers blueprints and serves HTML pages.
Protected pages require an active session.
Performance: gzip compression + HTTP cache headers.
"""
import os
import sys
import gzip
import io
import time
from functools import wraps

from flask      import Flask, render_template, session, redirect, jsonify, request
from flask_cors import CORS

# ── Path setup ────────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import config

from routes.auth         import auth_bp
from routes.trips        import trips_bp
from routes.destinations import destinations_bp
from routes.ai           import ai_bp

# ── Flask app ─────────────────────────────────────────────────────────────────
template_dir = os.path.join(current_dir, 'template')
static_dir   = os.path.abspath(os.path.join(current_dir, '..', '..', 'frontend', 'static'))

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
app.secret_key = config.SECRET_KEY

# Force Jinja2 to reload templates from disk on every request — never serve stale HTML
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# Cache-bust version — changes every server restart, forces browsers to reload CSS/JS
# This kills any stale cached assets from previous runs
ASSET_VERSION = str(int(time.time()))
app.jinja_env.globals['v'] = ASSET_VERSION

# Restrict CORS to local dev origins; set ALLOWED_ORIGINS env var in production
_allowed = os.environ.get('ALLOWED_ORIGINS', 'http://127.0.0.1:5000,http://localhost:5000').split(',')
CORS(app, supports_credentials=True, origins=_allowed)

app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)
app.register_blueprint(destinations_bp)
app.register_blueprint(ai_bp)


# ── Gzip compression ──────────────────────────────────────────────────────────
@app.after_request
def compress_response(response):
    """Gzip JSON/HTML responses >1 KB. Never touches static files (Flask handles those)."""
    # Skip static files — Flask's send_file already handles them correctly
    if request.path.startswith('/static/'):
        return response
    # Skip if already encoded or not a compressible type
    if response.headers.get('Content-Encoding'):
        return response
    if 'gzip' not in request.headers.get('Accept-Encoding', ''):
        return response
    ct = response.content_type or ''
    if not (ct.startswith('application/json') or
            ct.startswith('text/html') or
            ct.startswith('text/plain')):
        return response
    data = response.get_data()
    if len(data) < 1024:
        return response
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as f:
        f.write(data)
    compressed = buf.getvalue()
    response.set_data(compressed)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length']   = len(compressed)
    response.headers.add('Vary', 'Accept-Encoding')
    return response


# ── HTTP cache headers ────────────────────────────────────────────────────────
@app.after_request
def add_cache_headers(response):
    """
    - Static assets: 7-day cache (versioned URLs bust the cache on change)
    - HTML pages: no-cache — browser must revalidate every visit
    - API: no-store — never cache API responses
    """
    path = request.path
    if path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=604800, stale-while-revalidate=86400'
        response.headers['X-Content-Type-Options'] = 'nosniff'
    elif path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma']        = 'no-cache'
    else:
        # HTML pages — always revalidate so users get the latest version
        response.headers['Cache-Control'] = 'no-cache, must-revalidate'
        response.headers['Pragma']        = 'no-cache'
    return response


# ── Auth guard decorator ──────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_id'):
            return f(*args, **kwargs)
        if request.headers.get('Accept', '').startswith('application/json'):
            return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
        return redirect(f'/?next={request.path}&login=1')
    return decorated


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    path = request.path
    # Never swallow missing static files — return a real 404
    if path.startswith('/static/'):
        return jsonify({'status': 'error', 'message': f'Static file not found: {path}'}), 404
    if path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404
    # For page routes, return the home page (SPA fallback)
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405


# ── Public page routes ────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')


# ── Protected page routes ─────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/planner')
def planner():
    return render_template('planner.html')


# ── Route Planning API ────────────────────────────────────────────────────────
@app.route('/api/routes', methods=['GET'])
def get_routes():
    from trip_engine import TripEngine
    from utils       import safe_int

    destination = request.args.get('destination', '').strip()
    transport   = request.args.get('transport', 'public')
    travelers   = safe_int(request.args.get('travelers', 1), min_val=1)

    days        = safe_int(request.args.get('days', 3), min_val=1)

    if not destination:
        return jsonify({'status': 'error', 'message': 'destination required'}), 400

    engine = TripEngine(
        destination   = destination,
        days          = days,
        budget        = 1000,
        travel_type   = 'solo',
        interests     = [],
        accommodation = 'hotel',
        transport     = transport,
        start_date    = '',
        travelers     = travelers,
    )
    return jsonify({'status': 'success', 'routes': engine.generate_routes()})


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f"TripPilot AI — http://127.0.0.1:5000  (debug={config.DEBUG})")
    app.run(debug=config.DEBUG, port=5000)
