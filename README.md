# ✈️ TripPilot AI

> **All-in-One AI Travel Planning Platform** — from discovery to departure, in one place.

---

## 🌍 Overview

TripPilot AI is a comprehensive, AI-powered travel planning platform that consolidates the entire trip-planning process into a single seamless experience. No more juggling between apps for destinations, budgets, weather, and itineraries — TripPilot AI brings it all together under one intelligent interface.

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| 🗺️ **Destination Catalog** | 50+ curated destinations across 6 travel categories |
| 🤖 **AI Itinerary Builder** | Auto-generated 5-day plans with activities, timings & cost estimates |
| 💰 **Budget Insights** | Real-time budget tracking, cost breakdowns, and spending forecasts |
| 🌤️ **Weather Forecasts** | Live weather data integrated directly into itinerary planning |
| 📍 **Route Planning** | Google Maps integration for navigation between itinerary stops |
| 💬 **AI Advisor Chat** | Conversational AI for real-time trip advice and adjustments |
| 📋 **Bookings Dashboard** | Central hub to manage bookings, locations, and trip progress |

---

## 🗂️ Project Structure

```
/
├── main.js              # Shared JS — auth, nav, toasts, hero search
├── explore.js           # Explore page — AI recommendation engine
├── dashboard.css        # Dashboard styles — sidebar, stats, trips, analytics
├── /api
│   ├── /auth            # Login, register, logout, session
│   ├── /destinations    # Destination catalog endpoints
│   └── /recommendations # Personalized AI recommendation engine
└── /pages
    ├── index            # Homepage with hero search
    ├── explore          # Destination discovery + AI matches
    ├── planner          # Itinerary builder
    └── dashboard        # User trip management
```

---

## 🧠 AI Recommendation Engine

The recommendation engine scores destinations across **5 dimensions** (max 100 pts):

| Dimension | Max Score | How It Works |
|-----------|-----------|--------------|
| Interests | 40 pts | Jaccard similarity match against user interests |
| Budget | 20 pts | Daily cost vs. user budget level |
| Travel Style | 20 pts | Solo / couple / family / group matching |
| Season | 10 pts | Best-season alignment with travel dates |
| Group Size | 10 pts | Destination suitability for party size |

Scores recalculate dynamically on every filter change with a 350ms debounce.

---

## 🔄 User Flow

```
Onboarding → Destination Discovery → Itinerary Generation
     → Budget Review → Weather Check → Route Planning
          → AI Chat Support → Dashboard Management
```

---

## 🛠️ Tech Stack

- **Frontend:** Vanilla JS (ES6+), CSS3 with custom properties
- **Maps:** Google Maps API (embedded route planning)
- **Auth:** Session-based authentication (`/api/auth`)
- **AI:** Conversational advisor + scoring recommendation engine
- **Weather:** Live forecast API integrated into itinerary view

---

## ⚡ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/aminaliaqatalibhatti-del/.kiro.git
cd .kiro
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Add your API keys: Google Maps, Weather API, etc.
```

### 4. Run the development server
```bash
npm run dev
```

### 5. Open in browser
```
http://localhost:3000
```

---

## 📸 Screenshots

> Screenshots coming soon — see `TripPilotAI_Platform_Documentation.docx` for the full platform walkthrough with figure references.

---

## 📋 Key Differentiators

| Other Tools | TripPilot AI |
|-------------|--------------|
| Multiple apps for planning | Single unified platform |
| Manual itinerary building | AI auto-generates complete 5-day plans |
| Generic destination lists | 50+ curated destinations matched to preferences |
| No real-time budget tracking | Live cost estimates tied to every decision |
| Separate weather apps | Forecasts embedded inside the itinerary |
| Third-party map redirection | Google Maps natively integrated |
| Static FAQ or no support | Live AI Advisor for personalized guidance |

---

## 👤 Author

**Amina Liaqat Ali Bhatti**
- GitHub: [@aminaliaqatalibhatti-del](https://github.com/aminaliaqatalibhatti-del)

---

## 📄 License

This project was built as part of a Hackathon submission — June 2026.

---

*TripPilot AI • All-in-One Travel Planning Platform • June 2026*
