# TripPilot AI — Route Blueprints Package
from routes.auth         import auth_bp
from routes.trips        import trips_bp
from routes.destinations import destinations_bp
from routes.ai           import ai_bp

__all__ = ['auth_bp', 'trips_bp', 'destinations_bp', 'ai_bp']
