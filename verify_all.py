"""Full verification script — checks all systems."""
import sys, traceback
sys.path.insert(0, r'c:\Users\angry\OneDrive\Desktop\rabia\backend\backend')

errors = []

# 1. trip_engine
try:
    from trip_engine import DESTINATIONS, TripEngine
    print(f"[OK] trip_engine — {len(DESTINATIONS)} destinations")
    cats = {}
    for k,v in DESTINATIONS.items():
        c = v.get('category','MISSING')
        cats[c] = cats.get(c,0) + 1
    for cat, cnt in sorted(cats.items()):
        print(f"     {cat}: {cnt}")
except Exception as e:
    errors.append(f"trip_engine: {e}")
    traceback.print_exc()

# 2. ai_advisor
try:
    from ai_advisor import DEST_ADVISOR, AIAdvisor
    print(f"\n[OK] ai_advisor — DEST_ADVISOR entries: {len(DEST_ADVISOR)}")
    missing = [k for k in DESTINATIONS if k not in DEST_ADVISOR]
    print(f"     Destinations missing from DEST_ADVISOR: {len(missing)}")
    if missing:
        print(f"     {missing[:10]}{'...' if len(missing)>10 else ''}")
except Exception as e:
    errors.append(f"ai_advisor: {e}")
    traceback.print_exc()

# 3. data_store
try:
    from data_store import DataStore
    ds = DataStore()
    dests = ds.get_destinations()
    print(f"\n[OK] data_store — get_destinations() returns {len(dests)} entries")
    sample = dests[0]
    print(f"     Sample keys: {list(sample.keys())}")
except Exception as e:
    errors.append(f"data_store: {e}")
    traceback.print_exc()

# 4. recommendations engine
try:
    e = TripEngine('paris',5,1000,'couple',['food','art'],'hotel','public','2026-09-01',2)
    recs = e.recommend_destinations(['food','art'],'medium','couple',2,9,5)
    print(f"\n[OK] recommendations — {len(recs)} results")
    for r in recs:
        print(f"     {r['name']:20s} {r['match_pct']:3d}%  cat={r['category']}")
except Exception as e:
    errors.append(f"recommendations: {e}")
    traceback.print_exc()

# 5. routes
try:
    from routes.destinations import destinations_bp
    from routes.trips import trips_bp
    from routes.ai import ai_bp
    from routes.auth import auth_bp
    print(f"\n[OK] All Flask blueprints import OK")
except Exception as e:
    errors.append(f"blueprints: {e}")
    traceback.print_exc()

# 6. Full app
try:
    import app as application
    print(f"[OK] app.py imports OK — Flask app created")
except Exception as e:
    errors.append(f"app: {e}")
    traceback.print_exc()

print(f"\n{'='*50}")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for err in errors:
        print(f"  - {err}")
else:
    print("ALL CHECKS PASSED — server is ready to run")
    print("Start with: python app.py")
