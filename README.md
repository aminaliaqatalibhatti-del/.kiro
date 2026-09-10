# TripPilot AI ✈️

AI-powered travel planning platform. Vercel pe deploy karo — **ek bhi server nahi, ek bhi dollar nahi.**

---

## 🏗️ Project Structure

```
.kiro/
├── api/                        ← FastAPI backend (Vercel serverless)
│   ├── index.py                ← Entry point
│   ├── config.py               ← Environment variables
│   ├── data_store.py           ← In-memory storage
│   ├── utils.py                ← Shared helpers
│   ├── trip_engine.py          ← Core AI itinerary engine + 50+ destinations
│   ├── ai_advisor.py           ← AI chat + destination advisor
│   ├── weather_service.py      ← Weather (live OWM + offline fallback)
│   ├── places_service.py       ← Hotels + geocoding
│   └── routes/
│       ├── auth.py             ← /api/auth/*
│       ├── trips.py            ← /api/trips/*, /api/analytics/*
│       ├── destinations.py     ← /api/destinations, /api/recommendations, /api/weather, /api/hotels
│       └── ai.py               ← /api/ai/*
│
├── public/                     ← Static frontend (Vercel CDN)
│   ├── index.html              ← Homepage
│   ├── planner.html            ← Trip planning wizard
│   ├── explore.html            ← Destination explorer
│   ├── dashboard.html          ← User dashboard
│   └── static/
│       ├── main.css / main.js
│       ├── planner.css / planner.js
│       ├── dashboard.css / dashboard.js
│       ├── explore.js
│       └── ai_assistant.css / ai_assistant.js
│
├── vercel.json                 ← Vercel routing config
├── requirements.txt            ← Python dependencies
└── backend/                   ← Original Flask app (reference only, not deployed)
```

---

## 🚀 Vercel Pe Deploy Karo (5 Minutes)

### Step 1 — GitHub pe push karo

```bash
git add .
git commit -m "Migrated to FastAPI for Vercel deployment"
git push origin main
```

### Step 2 — Vercel mein import karo

1. [vercel.com](https://vercel.com) pe jao → **Add New Project**
2. GitHub repo select karo
3. **Framework Preset** → `Other` select karo
4. **Root Directory** → `.kiro` type karo (ya jahan yeh folder hai)
5. **Build & Output Settings** mein kuch change mat karo
6. **Deploy** dabao

### Step 3 — Environment Variables (Optional)

Vercel dashboard → Project → **Settings → Environment Variables** mein add karo:

| Variable | Value | Zaroorat |
|----------|-------|----------|
| `SECRET_KEY` | koi random string (32+ chars) | ✅ Recommended |
| `OPENWEATHER_API_KEY` | openweathermap.org se free key | ❌ Optional |
| `OPENCAGE_API_KEY` | opencagedata.com se free key | ❌ Optional |

> **Note:** API keys ke baghair bhi app poori tarah kaam karta hai — offline fallback data use karta hai.

---

## 💻 Local Development

```bash
# Dependencies install karo
pip install -r requirements.txt

# api/ folder se run karo
cd api
uvicorn index:app --reload --port 8000
```

Phir browser mein `http://localhost:8000/api/docs` pe FastAPI docs dekhoge.

Frontend ke liye `public/index.html` directly browser mein open karo, ya koi bhi static server:
```bash
# Python built-in server (public/ folder se)
python -m http.server 3000 --directory public
```

Phir `http://localhost:3000` pe app chalega.

---

## 🌐 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Account banao |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current user |
| POST | `/api/trips/plan` | Trip plan generate karo |
| GET | `/api/trips` | Apne saare trips |
| GET | `/api/trips/{id}` | Single trip |
| DELETE | `/api/trips/{id}` | Trip delete karo |
| POST | `/api/trips/{id}/expenses` | Expense add karo |
| PUT | `/api/trips/{id}/expenses/{eid}` | Expense edit karo |
| DELETE | `/api/trips/{id}/expenses/{eid}` | Expense delete karo |
| GET | `/api/analytics/summary` | Spending analytics |
| GET | `/api/destinations` | Saare destinations |
| POST | `/api/recommendations` | AI-matched recommendations |
| GET | `/api/weather` | Weather forecast |
| GET | `/api/hotels` | Hotel list |
| GET | `/api/routes` | Route planning |
| POST | `/api/ai/advisory` | Full AI advisory |
| POST | `/api/ai/chat` | AI Q&A |
| POST | `/api/ai/compare` | 2 destinations compare karo |
| GET | `/api/health` | Health check |

---

## ⚠️ Vercel Limitations

- **In-memory storage** — Server restart hone pe users/trips delete ho jaate hain. Production mein [MongoDB Atlas](https://www.mongodb.com/atlas) (free tier available) ya [PlanetScale](https://planetscale.com) add karo.
- **Cold starts** — Pehli request slow ho sakti hai (~2-3 sec). Normal hai Vercel serverless mein.
- **Function timeout** — Vercel free plan mein 10 sec timeout hai. Trip planning ~2-4 sec leta hai — safe hai.

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Frontend | Vanilla JS + CSS3 |
| Hosting | Vercel (Serverless) |
| Storage | In-memory (upgrade to MongoDB) |
| AI Engine | Rule-based Python (no OpenAI needed) |
| Weather | OpenWeatherMap API + offline fallback |
| Geocoding | OpenCage API + offline fallback |
