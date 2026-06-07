# TripPilot AI — Complete Run Guide

## What's in the project

```
rabia/
├── backend/backend/          ← Flask app (run from here)
│   ├── app.py                ← Entry point
│   ├── trip_engine.py        ← AI itinerary engine
│   ├── ai_advisor.py         ← AI chat + recommendations
│   ├── weather_service.py    ← Weather (live + offline)
│   ├── places_service.py     ← Hotels + attractions
│   ├── config.py             ← All environment config
│   ├── data_store.py         ← JSON persistence layer
│   ├── utils.py              ← Shared helpers
│   ├── routes/               ← Flask Blueprints
│   │   ├── auth.py           ← Register / Login / Logout
│   │   ├── trips.py          ← Trips + expenses + analytics
│   │   ├── destinations.py   ← Destinations + recommendations
│   │   └── ai.py             ← AI advisory + chat + compare
│   ├── template/             ← Jinja2 HTML templates
│   └── data/                 ← Auto-created JSON data files
├── frontend/static/          ← CSS + JavaScript
└── requirements.txt          ← Python dependencies
```

---

## Step-by-step: How to run

### Step 1 — Make sure Python is installed

Open a terminal and run:
```
python --version
```
You need **Python 3.9 or higher**. If not installed, download from https://python.org

---

### Step 2 — Open a terminal in the project folder

```
cd C:\Users\angry\OneDrive\Desktop\rabia
```

---

### Step 3 — Install Python dependencies

Run this **once**:
```
pip install -r requirements.txt
```

This installs: Flask, flask-cors, Werkzeug, Jinja2, gunicorn and all other required packages.

To verify they installed:
```
pip show flask flask-cors werkzeug
```

---

### Step 4 — Run the app

```
cd backend\backend
python app.py
```

You will see:
```
TripPilot AI — http://127.0.0.1:5000  (debug=False)
 * Running on http://127.0.0.1:5000
```

---

### Step 5 — Open in browser

Go to: **http://127.0.0.1:5000**

| Page | URL |
|---|---|
| Home | http://127.0.0.1:5000/ |
| Trip Planner | http://127.0.0.1:5000/planner |
| Explore | http://127.0.0.1:5000/explore |
| Dashboard | http://127.0.0.1:5000/dashboard |

---

### Step 6 — To stop the app

Press **Ctrl + C** in the terminal.

---

## Optional: Enable debug mode (development)

Set an environment variable before running:

**Windows CMD:**
```
set FLASK_DEBUG=true
python app.py
```

**Windows PowerShell:**
```
$env:FLASK_DEBUG="true"
python app.py
```

---

## Optional: Use live weather (free API key)

1. Sign up free at https://openweathermap.org/api
2. Get your API key
3. Set it before running:

**Windows CMD:**
```
set OPENWEATHER_API_KEY=your_key_here
python app.py
```

Without the key, the app uses **climate-model data** — fully functional offline.

---

## Full example (copy-paste ready)

```
cd C:\Users\angry\OneDrive\Desktop\rabia
pip install -r requirements.txt
cd backend\backend
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` from the project root |
| `Address already in use` | Another process is on port 5000. Change port: `python app.py` won't work — edit `app.py` last line to `port=5001` |
| `No module named 'flask_cors'` | Run `pip install flask-cors==6.0.2` |
| Page shows 404 | Make sure you're running from `backend\backend\` not the root |
| Dashboard redirects to login | Dashboard is protected — register or log in first |

---

## Data files (auto-created)

The first time you register or save a trip, these files are created automatically:
```
backend/backend/data/
├── users.json    ← Registered accounts
└── trips.json    ← Saved trip plans
```

These are plain JSON — you can delete them to reset all data.
