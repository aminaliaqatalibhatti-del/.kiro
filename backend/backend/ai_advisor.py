"""
TripPilot AI — AI Advisor Engine
Produces contextual, natural-language travel intelligence:
  - Destination comparisons with real budget deltas
  - Alternative suggestions when destination is suboptimal
  - Weather-driven itinerary adjustments
  - Budget optimization recommendations
  - Travel-type personalization insights
  - Conversational question answering about a loaded trip plan
"""

from __future__ import annotations
import re
from datetime import datetime
from trip_engine import DESTINATIONS, WEATHER_CONDITIONS


# ─────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE LAYER  (extends DESTINATIONS with advisor-specific facts)
# ─────────────────────────────────────────────────────────────────────────────
DEST_ADVISOR = {
    "paris": {
        "similar": ["rome", "barcelona", "amsterdam", "lisbon"],
        "crowd_months": [6, 7, 8, 12],
        "visa_ease": "easy",   # for most Western passport holders
        "best_avoided_if": ["extreme heat aversion", "budget under $60/day"],
        "pro_tips": [
            "Buy the Paris Museum Pass to save up to 40% on entrance fees.",
            "Take the RER B train from CDG airport — it costs ~€11 vs. ~€55 taxi.",
            "Visit the Louvre on Friday evenings for smaller crowds and late opening.",
            "Book Eiffel Tower tickets online at least 2 weeks ahead.",
        ],
        "budget_hacks": [
            "Most national museums are free on the first Sunday of every month.",
            "Lunch menus (formule) at restaurants cost 30–50% less than dinner.",
            "Vélib' bike-share is €3/day — much cheaper than metro for short trips.",
        ],
        "weather_notes": {
            "summer": "July–August can be extremely hot (35°C+). Many locals leave the city.",
            "spring": "April–May: mild, beautiful, and far less crowded than summer.",
            "winter": "December has festive lights but cold, damp weather. Pack layers.",
        },
    },
    "tokyo": {
        "similar": ["osaka", "kyoto", "singapore", "seoul"],
        "crowd_months": [3, 4, 10, 11],
        "visa_ease": "easy",
        "best_avoided_if": ["budget under $50/day", "dislike crowds"],
        "pro_tips": [
            "Get a Suica card at the airport — works on all trains, buses, and vending machines.",
            "7-Eleven and FamilyMart have ATMs that accept foreign cards.",
            "Book teamLab Planets tickets at least 1 week ahead — it sells out.",
            "JR Pass only makes sense if you travel between cities; within Tokyo use Suica.",
        ],
        "budget_hacks": [
            "Ramen shops and soba restaurants serve full meals from ¥600 (~$4).",
            "Convenience store sushi and onigiri are surprisingly high quality.",
            "Free observation decks at Tokyo Metropolitan Government Building.",
        ],
        "weather_notes": {
            "spring": "March–April: cherry blossoms. Very crowded. Book 6 months ahead.",
            "summer": "July–September: hot and humid (32°C+), typhoon season.",
            "autumn": "October–November: crisp, beautiful foliage. Best overall season.",
        },
    },
    "dubai": {
        "similar": ["abu dhabi", "doha", "riyadh", "muscat"],
        "crowd_months": [11, 12, 1, 2, 3],
        "visa_ease": "easy",
        "best_avoided_if": ["summer travel (extreme heat)", "very tight budgets"],
        "pro_tips": [
            "Dubai Metro is clean, punctual, and costs a fraction of taxis.",
            "Visit the Burj Khalifa at sunset — the views are spectacular and less crowded than midday.",
            "Free beach access at JBR (Jumeirah Beach Residence).",
            "Dubai Frame is often overlooked but offers the best skyline view for $14.",
        ],
        "budget_hacks": [
            "Mall food courts serve full meals from AED 25 (~$7).",
            "Happy hours at many hotel bars offer 50% off drinks.",
            "Deira Gold Souk and Spice Souk are free to browse.",
        ],
        "weather_notes": {
            "summer": "June–September: 40–48°C. Outdoor activities are dangerous. Heavily discounted hotel rates.",
            "winter": "November–March: perfect 20–28°C. Peak season with higher prices.",
        },
    },
    "bali": {
        "similar": ["lombok", "phuket", "koh samui", "sri lanka"],
        "crowd_months": [7, 8],
        "visa_ease": "easy",
        "best_avoided_if": ["monsoon sensitivity", "budget over $400/day (overkill)"],
        "pro_tips": [
            "Hire a private driver for ~$35/day — far more flexible than taxis.",
            "Stay in Ubud for culture and Seminyak/Canggu for nightlife.",
            "The Monkey Forest is free if you walk in from the back entrance.",
            "Book Mount Batur sunrise trekking with a guide from Ubud the day before.",
        ],
        "budget_hacks": [
            "Warungs (local restaurants) serve nasi goreng and mie goreng from 20,000 IDR (~$1.30).",
            "Motorbike rental costs ~$5/day and is the fastest way around.",
            "Many temples have free entry if you wear a sarong.",
        ],
        "weather_notes": {
            "dry": "April–September: ideal conditions, minimal rain.",
            "wet": "November–March: daily afternoon rain, but still very manageable.",
            "peak": "July–August: most crowded and expensive. Book early.",
        },
    },
    "new york": {
        "similar": ["chicago", "boston", "london", "toronto"],
        "crowd_months": [6, 7, 8, 12],
        "visa_ease": "moderate",
        "best_avoided_if": ["extreme cold sensitivity (January–February)", "budget under $100/day"],
        "pro_tips": [
            "Get an OMNY card for unlimited subway/bus rides ($34/week).",
            "The Staten Island Ferry is free and offers stunning Statue of Liberty views.",
            "TKTS booth in Times Square offers same-day Broadway tickets at 40–60% off.",
            "Visit top-of-the-rock (Rockefeller) for better views than Empire State Building.",
        ],
        "budget_hacks": [
            "NYC public libraries often have free museum passes.",
            "Many world-class museums (MoMA, MET) have pay-what-you-wish hours.",
            "Trader Joe's and Whole Foods in Midtown are cheaper than restaurants for lunch.",
        ],
        "weather_notes": {
            "spring": "April–May: ideal. Mild temps, blooming Central Park.",
            "summer": "June–August: hot and humid. Very crowded. Higher hotel prices.",
            "winter": "December: magical holiday season but very cold (-5 to 5°C).",
        },
    },
    "istanbul": {
        "similar": ["athens", "cairo", "amman", "marrakech"],
        "crowd_months": [6, 7, 8],
        "visa_ease": "easy",
        "best_avoided_if": [],
        "pro_tips": [
            "Get an Istanbulkart transit card — saves up to 50% on all public transport.",
            "Hagia Sophia is free; queue early to avoid the 1-hour lines.",
            "Take the Bosphorus ferry for €1.50 instead of tourist cruise boats (€15+).",
            "Grand Bazaar prices are negotiable — always counter-offer at 50% of asking price.",
        ],
        "budget_hacks": [
            "Simit (sesame bread ring) from street carts costs ₺5 (~$0.15) and is a full snack.",
            "Turkish tea (çay) at lokanta restaurants is usually free or ₺5.",
            "Museum Pass Istanbul covers 12 major sites for €25.",
        ],
        "weather_notes": {
            "spring": "April–May: 18–22°C, ideal. Fewer tourists than summer.",
            "summer": "July–August: 28–33°C, very crowded. Book ahead.",
            "autumn": "September–October: excellent weather, thinning crowds.",
        },
    },
    "rome": {
        "similar": ["florence", "naples", "athens", "madrid"],
        "crowd_months": [6, 7, 8, 4],
        "visa_ease": "easy",
        "best_avoided_if": ["extreme heat aversion"],
        "pro_tips": [
            "Book Colosseum + Roman Forum tickets online 2–3 days ahead.",
            "Vatican Museums: pre-book to skip the 2-hour queue.",
            "Fontana di Trevi is magical at dawn (6–7am) with almost no crowds.",
            "Free walking tours run from Campo de' Fiori every morning.",
        ],
        "budget_hacks": [
            "Aperitivo hour (6–9pm) at many bars includes free food with a drink purchase.",
            "All water fountains (nasoni) have free, clean drinking water.",
            "Vatican Museums are free on the last Sunday of every month — arrive early.",
        ],
        "weather_notes": {
            "spring": "April–June: best weather, very busy. Book hotels 2+ months ahead.",
            "summer": "July–August: 32–38°C. Extremely crowded. Many locals on holiday.",
            "autumn": "September–October: ideal — warm, thinner crowds, lower prices.",
        },
    },
    "maldives": {
        "similar": ["seychelles", "mauritius", "fiji", "bora bora"],
        "crowd_months": [12, 1, 2, 3],
        "visa_ease": "easy",
        "best_avoided_if": ["budget under $200/day"],
        "pro_tips": [
            "Local islands (Maafushi, Fulidhoo) offer the same beaches at 80% lower cost.",
            "Book speedboat transfers in advance — seaplane upgrades cost $400–600 each way.",
            "Best snorkelling is at dawn before boat traffic stirs up the sand.",
            "Most mid-range resorts include snorkelling gear; ask before renting.",
        ],
        "budget_hacks": [
            "Stay on a local island guesthouse ($60–120/night) vs. resort ($600+/night).",
            "Local cafes serve fish curry and rice meals for $5–8.",
            "House reef snorkelling is free and often better than paid excursions.",
        ],
        "weather_notes": {
            "dry": "November–April: calm seas, excellent visibility. Peak prices.",
            "wet": "May–October: some rain, lower prices, still great diving.",
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# CORE ADVISOR CLASS
# ─────────────────────────────────────────────────────────────────────────────
class AIAdvisor:

    def __init__(self, trip_context: dict):
        """
        trip_context keys:
            destination, days, budget, travel_type, interests,
            accommodation, transport, travelers, start_date,
            plan (full plan dict, optional)
        """
        self.dest        = (trip_context.get("destination") or "").lower().strip()
        self.days        = int(trip_context.get("days") or 5)
        self.budget      = float(trip_context.get("budget") or 1000)
        self.travel_type = trip_context.get("travel_type") or "solo"
        self.interests   = trip_context.get("interests") or []
        self.accommodation = trip_context.get("accommodation") or "hotel"
        self.transport   = trip_context.get("transport") or "public"
        self.travelers   = int(trip_context.get("travelers") or 1)
        self.start_date  = trip_context.get("start_date") or ""
        self.plan        = trip_context.get("plan") or {}
        self._dest_data  = DESTINATIONS.get(self.dest, {})
        self._advisor    = DEST_ADVISOR.get(self.dest, {})
        self._budget_per_person_per_day = (
            self.budget / max(self.days, 1) / max(self.travelers, 1)
        )

    # ── Public: full advisory report ─────────────────────────────────────────
    def full_advisory(self) -> dict:
        return {
            "destination_verdict": self._destination_verdict(),
            "alternative_suggestions": self._find_alternatives(),
            "budget_optimization": self._budget_optimization(),
            "weather_adjustments": self._weather_adjustments(),
            "travel_type_tips": self._travel_type_tips(),
            "pro_tips": self._advisor.get("pro_tips", [])[:3],
            "budget_hacks": self._advisor.get("budget_hacks", [])[:3],
            "timing_advice": self._timing_advice(),
            "ai_summary": self._ai_summary(),
        }

    # ── Public: chat response ─────────────────────────────────────────────────
    def answer_question(self, question: str) -> str:
        """Route a natural-language question to the right advisor method."""
        q = question.lower().strip()

        if any(w in q for w in ["cheaper", "save", "budget", "cost", "expensive", "money"]):
            return self._answer_budget(q)
        if any(w in q for w in ["alternative", "instead", "other", "similar", "compare"]):
            return self._answer_alternatives(q)
        if any(w in q for w in ["weather", "rain", "temperature", "umbrella", "pack", "wear", "cold", "hot"]):
            return self._answer_weather(q)
        if any(w in q for w in ["best time", "when", "month", "season", "timing"]):
            return self._answer_timing(q)
        if any(w in q for w in ["hotel", "stay", "accommodation", "hostel", "resort"]):
            return self._answer_hotel(q)
        if any(w in q for w in ["food", "eat", "restaurant", "cuisine", "local"]):
            return self._answer_food(q)
        if any(w in q for w in ["itinerary", "schedule", "day", "plan", "activity", "adjust"]):
            return self._answer_itinerary(q)
        if any(w in q for w in ["visa", "passport", "entry", "requirement"]):
            return self._answer_visa(q)
        if any(w in q for w in ["tip", "advice", "recommend", "suggest", "know"]):
            return self._answer_tips(q)

        return self._answer_general(q)

    # ─────────────────────────────────────────────────────────────────────────
    # DESTINATION VERDICT
    # ─────────────────────────────────────────────────────────────────────────
    def _destination_verdict(self) -> dict:
        if not self._dest_data:
            return {
                "verdict": "unknown",
                "score": 50,
                "message": f"I don't have detailed data on {self.dest.title()} yet, but I've built your plan using general travel intelligence.",
                "flags": [],
            }

        score  = 100
        flags  = []
        daily  = self._dest_data.get("daily_budget", {})
        min_d  = daily.get("low", 60)

        # Budget check
        if self._budget_per_person_per_day < min_d * 0.7:
            score -= 30
            flags.append({
                "type": "warning",
                "icon": "💸",
                "message": (f"Your budget of ${self._budget_per_person_per_day:.0f}/person/day "
                            f"is below the recommended minimum of ${min_d}/day for {self.dest.title()}. "
                            f"You may find it difficult to cover accommodation and meals comfortably.")
            })
        elif self._budget_per_person_per_day > daily.get("high", 400) * 1.5:
            flags.append({
                "type": "info",
                "icon": "💎",
                "message": f"Your budget is very generous for {self.dest.title()}. You can access premium experiences, private tours, and top restaurants without concern."
            })

        # Season check
        try:
            travel_month = int(self.start_date.split("-")[1]) if self.start_date else datetime.today().month
        except (IndexError, ValueError):
            travel_month = datetime.today().month

        best = self._dest_data.get("best_months", [])
        crowd = self._advisor.get("crowd_months", [])

        if best and travel_month not in best:
            nearby_best = min(best, key=lambda m: min(abs(m - travel_month), 12 - abs(m - travel_month)))
            month_name  = datetime(2024, nearby_best, 1).strftime("%B")
            score -= 10
            flags.append({
                "type": "tip",
                "icon": "📅",
                "message": (f"You're not travelling in {self.dest.title()}'s peak season. "
                            f"The best months are {', '.join(datetime(2024,m,1).strftime('%B') for m in best[:3])}. "
                            f"Closer to {month_name} would give you the best experience.")
            })
        elif travel_month in crowd:
            score -= 5
            flags.append({
                "type": "tip",
                "icon": "👥",
                "message": (f"You're visiting {self.dest.title()} during its busiest period. "
                            f"Book accommodation and major attractions at least 4–6 weeks in advance to avoid sellouts and premium pricing.")
            })

        # Travel type check
        tags = set(self._dest_data.get("tags", []))
        type_ideal = {
            "solo":   {"adventure", "photography", "nightlife"},
            "couple": {"food", "shopping", "art", "luxury"},
            "family": {"nature", "history"},
            "friends":{"nightlife", "adventure", "food"},
        }
        ideal = type_ideal.get(self.travel_type, set())
        overlap = len(tags & ideal)
        if overlap == 0:
            score -= 10
            flags.append({
                "type": "tip",
                "icon": "🧳",
                "message": (f"{self.dest.title()} is primarily known for "
                            f"{', '.join(list(tags)[:3])}. For a {self.travel_type} trip, "
                            f"you might want to look at alternatives I've suggested below.")
            })

        verdict = "excellent" if score >= 80 else "good" if score >= 60 else "fair"

        msg_map = {
            "excellent": f"✅ {self.dest.title()} is an excellent match for your trip profile. Great choice.",
            "good":      f"👍 {self.dest.title()} is a solid choice with a few things to keep in mind.",
            "fair":      f"⚠️ {self.dest.title()} can work, but I've found some alternatives that might suit your preferences better.",
        }

        return {
            "verdict": verdict,
            "score": score,
            "message": msg_map[verdict],
            "flags": flags,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # ALTERNATIVES
    # ─────────────────────────────────────────────────────────────────────────
    def _find_alternatives(self) -> list:
        alts = []
        current_mid = self._dest_data.get("daily_budget", {}).get("medium", 150) if self._dest_data else 150

        similar_keys = self._advisor.get("similar", [])
        # Also scan the full DB for interest matches
        user_tags = set(self.interests)
        current_tags = set(self._dest_data.get("tags", []))

        candidates = []
        for key, data in DESTINATIONS.items():
            if key == self.dest:
                continue
            dest_tags = set(data.get("tags", []))
            tag_match = len(dest_tags & user_tags) / max(len(dest_tags | user_tags), 1)
            is_similar = key in similar_keys
            candidates.append((key, data, tag_match, is_similar))

        # Sort: similar first, then by tag match
        candidates.sort(key=lambda x: (-int(x[3]), -x[2]))

        for key, data, tag_match, is_similar in candidates[:4]:
            alt_mid     = data.get("daily_budget", {}).get("medium", 150)
            budget_diff = round((alt_mid - current_mid) / max(current_mid, 1) * 100)
            saving      = current_mid - alt_mid

            if budget_diff < 0:
                budget_note = f"saves ~${abs(saving)}/day per person (≈{abs(budget_diff)}% cheaper)"
                budget_icon = "💰"
            elif budget_diff > 0:
                budget_note = f"costs ~${saving}/day more per person (≈{budget_diff}% pricier)"
                budget_icon = "💸"
            else:
                budget_note = "similar budget"
                budget_icon = "≈"

            shared = list(current_tags & set(data.get("tags", [])))
            reason = self._build_alt_reason(key, data, shared, budget_diff, tag_match)

            alts.append({
                "destination": key.title(),
                "country":     data.get("country", ""),
                "description": data.get("description", ""),
                "tags":        data.get("tags", [])[:4],
                "daily_budget_mid": alt_mid,
                "budget_note": budget_note,
                "budget_icon": budget_icon,
                "budget_diff_pct": budget_diff,
                "saving_per_day": saving,
                "tag_overlap": shared[:3],
                "reason": reason,
                "difficulty": data.get("difficulty", "moderate"),
                "safety":     data.get("safety", "moderate"),
            })

        return alts

    def _build_alt_reason(self, key: str, data: dict, shared: list, budget_diff: int, tag_match: float) -> str:
        dest = key.title()
        parts = []

        if shared:
            parts.append(f"shares your interest in {', '.join(shared[:2])}")
        if budget_diff <= -15:
            parts.append(f"is significantly cheaper — freeing up budget for extra experiences")
        elif budget_diff >= 15:
            parts.append(f"is a premium upgrade if you can stretch the budget")
        if tag_match > 0.5:
            parts.append("closely matches your stated travel interests")

        safety = data.get("safety", "moderate")
        if safety in ("very safe", "safe"):
            parts.append(f"is rated as {safety} for solo travellers")

        if not parts:
            parts.append("offers a distinct experience worth considering")

        return f"{dest} {' and '.join(parts[:2])}."

    # ─────────────────────────────────────────────────────────────────────────
    # BUDGET OPTIMIZATION
    # ─────────────────────────────────────────────────────────────────────────
    def _budget_optimization(self) -> list:
        tips = []
        plan = self.plan
        b    = plan.get("budget", {}) if plan else {}
        bd   = b.get("breakdown", {}) if b else {}

        # Accommodation optimizations
        accom = bd.get("accommodation", 0)
        if accom and self.accommodation == "hotel":
            hostel_save = accom * 0.55
            tips.append({
                "category": "Accommodation",
                "icon": "🏨",
                "type": "swap",
                "message": (f"Switching from a hotel to a quality hostel private room "
                            f"could save approximately ${hostel_save:.0f} total "
                            f"(${hostel_save/max(self.days,1):.0f}/night). "
                            f"Hostels like Generator and Kabak have private rooms with hotel-quality comfort."),
                "saving": round(hostel_save),
            })
        elif accom and self.accommodation == "resort":
            apt_save = accom * 0.4
            tips.append({
                "category": "Accommodation",
                "icon": "🏠",
                "type": "swap",
                "message": (f"An apartment rental instead of a resort saves ~${apt_save:.0f} total "
                            f"and gives you a kitchen to reduce food costs further."),
                "saving": round(apt_save),
            })

        # Transport optimizations
        transport_cost = bd.get("transportation", 0)
        if self.transport == "taxi" and transport_cost:
            pub_save = transport_cost * 0.65
            tips.append({
                "category": "Transport",
                "icon": "🚌",
                "type": "swap",
                "message": (f"Using public transport instead of taxis could save ~${pub_save:.0f} "
                            f"over the trip. Most major cities have excellent metro systems that "
                            f"are also faster during peak hours."),
                "saving": round(pub_save),
            })
        elif self.transport == "rental car" and transport_cost:
            pub_save = transport_cost * 0.7
            tips.append({
                "category": "Transport",
                "icon": "🚌",
                "type": "swap",
                "message": (f"Public transport vs rental car saves ~${pub_save:.0f} total "
                            f"and eliminates parking costs (~$15–30/day in major cities)."),
                "saving": round(pub_save),
            })

        # Food optimizations
        food = bd.get("food", 0)
        if food and self._budget_per_person_per_day > 100:
            lunch_save = food * 0.25
            tips.append({
                "category": "Food",
                "icon": "🍽️",
                "type": "strategy",
                "message": (f"The 'lunch strategy': eat your main meal at lunch (fixed menus 30–50% cheaper) "
                            f"and keep dinner light. This alone could save ~${lunch_save:.0f} over your trip."),
                "saving": round(lunch_save),
            })

        if self._advisor.get("budget_hacks"):
            for hack in self._advisor["budget_hacks"][:2]:
                tips.append({
                    "category": "Local Tip",
                    "icon": "💡",
                    "type": "local",
                    "message": hack,
                    "saving": 0,
                })

        # Timing optimization
        try:
            travel_month = int(self.start_date.split("-")[1]) if self.start_date else datetime.today().month
        except (IndexError, ValueError):
            travel_month = datetime.today().month

        crowd = self._advisor.get("crowd_months", [])
        if travel_month in crowd:
            # Shoulder months
            shoulder = [m for m in range(1, 13) if m not in crowd and m in (self._dest_data.get("best_months") or range(1, 13))]
            if shoulder:
                nearby = min(shoulder, key=lambda m: min(abs(m - travel_month), 12 - abs(m - travel_month)))
                shoulder_name = datetime(2024, nearby, 1).strftime("%B")
                est_saving = self.budget * 0.15
                tips.append({
                    "category": "Timing",
                    "icon": "📅",
                    "type": "timing",
                    "message": (f"Shifting your trip to {shoulder_name} (shoulder season) "
                                f"could reduce hotel prices by 20–30% and save roughly ${est_saving:.0f} "
                                f"while giving you a less crowded, more authentic experience."),
                    "saving": round(est_saving),
                })

        total_saving = sum(t.get("saving", 0) for t in tips)
        if total_saving > 0:
            tips.insert(0, {
                "category": "Summary",
                "icon": "✨",
                "type": "summary",
                "message": (f"I've identified ways to save up to ${total_saving:.0f} "
                            f"on this trip ({round(total_saving/max(self.budget,1)*100)}% of your budget) "
                            f"without sacrificing key experiences."),
                "saving": total_saving,
            })

        return tips

    # ─────────────────────────────────────────────────────────────────────────
    # WEATHER ADJUSTMENTS
    # ─────────────────────────────────────────────────────────────────────────
    def _weather_adjustments(self) -> list:
        adjustments = []
        itinerary   = self.plan.get("itinerary", []) if self.plan else []

        for day in itinerary:
            w         = day.get("weather", {})
            condition = w.get("condition", "")
            rain_pct  = w.get("rain_probability", 0)

            if condition in ("thunderstorm", "heavy_rain"):
                outdoor = [t for t in day.get("timeline", [])
                           if t.get("type") in ("adventure", "nature", "landmark", "sightseeing")]
                indoor  = [t for t in day.get("timeline", [])
                           if t.get("type") in ("museum", "food", "art", "historic", "shopping")]

                if outdoor:
                    # Find a better day for outdoors
                    clear_days = [d for d in itinerary
                                  if d["day"] != day["day"]
                                  and d.get("weather", {}).get("rain_probability", 100) < 40]
                    swap_note = ""
                    if clear_days:
                        swap_day = clear_days[0]
                        swap_note = (f" Consider swapping outdoor activities to Day {swap_day['day']} "
                                     f"({swap_day.get('weather', {}).get('icon', '☀️')} "
                                     f"{swap_day.get('weather', {}).get('temp_c', '—')}°C).")

                    adjustments.append({
                        "day": day["day"],
                        "date": day.get("date", ""),
                        "severity": "high",
                        "icon": w.get("icon", "⛈"),
                        "condition": w.get("label", condition),
                        "message": (f"Day {day['day']}: {w.get('label', 'Bad weather')} expected "
                                    f"({rain_pct}% rain probability). "
                                    f"{outdoor[0]['activity']} should be moved indoors or rescheduled.{swap_note}"),
                        "original_activity": outdoor[0]["activity"],
                        "indoor_alternatives": self._indoor_alternatives(day),
                    })

            elif condition == "light_rain" and rain_pct > 55:
                outdoor = [t for t in day.get("timeline", [])
                           if t.get("type") in ("adventure", "nature")]
                if outdoor:
                    adjustments.append({
                        "day": day["day"],
                        "date": day.get("date", ""),
                        "severity": "medium",
                        "icon": w.get("icon", "🌦"),
                        "condition": w.get("label", condition),
                        "message": (f"Day {day['day']}: Light rain forecast ({rain_pct}% chance). "
                                    f"Pack a compact umbrella. {outdoor[0]['activity']} is still doable — "
                                    f"mornings are usually clearer."),
                        "original_activity": outdoor[0]["activity"],
                        "indoor_alternatives": [],
                    })

            elif condition == "hot" or w.get("temp_c", 0) >= 35:
                outdoor = [t for t in day.get("timeline", [])
                           if t.get("type") not in ("food", "museum") and t.get("time", "12:00") >= "11:00"]
                if outdoor:
                    adjustments.append({
                        "day": day["day"],
                        "date": day.get("date", ""),
                        "severity": "medium",
                        "icon": "🌡️",
                        "condition": "Extreme Heat",
                        "message": (f"Day {day['day']}: {w.get('temp_c', '—')}°C expected. "
                                    f"Reschedule outdoor activities to before 10am or after 5pm. "
                                    f"Use midday for air-conditioned museums, malls, or rest."),
                        "original_activity": outdoor[0]["activity"],
                        "indoor_alternatives": self._indoor_alternatives(day),
                    })

        return adjustments

    def _indoor_alternatives(self, day: dict) -> list:
        dest_data   = self._dest_data
        attractions = dest_data.get("attractions", []) if dest_data else []
        indoor_types = ("museum", "art", "food", "shopping", "historic")
        return [
            a["name"] for a in attractions
            if a.get("type") in indoor_types
        ][:3]

    # ─────────────────────────────────────────────────────────────────────────
    # TRAVEL TYPE TIPS
    # ─────────────────────────────────────────────────────────────────────────
    def _travel_type_tips(self) -> list:
        base = {
            "solo": [
                f"As a solo traveler in {self.dest.title()}, staying in a social hostel helps you meet people and often leads to spontaneous group activities.",
                "Book a free walking tour on Day 1 — it's the best way to orient yourself and meet other travelers.",
                f"Let your accommodation's front desk know your daily plans — they can advise on safety and recommend locals-only spots.",
            ],
            "couple": [
                f"{self.dest.title()} has excellent sunset spots — the most romantic moments often cost nothing.",
                "Book at least one special dinner reservation in advance — the best restaurants fill up weeks ahead.",
                "Consider a private city tour on Day 2 for a curated experience rather than joining a group.",
            ],
            "family": [
                "Check which attractions offer family tickets — savings of up to 40% are common.",
                f"Build in 1–2 rest days per week for a {self.days}-day trip with children to avoid burnout.",
                "Book accommodation with a kitchen or kitchenette — preparing some meals cuts costs significantly.",
                "Most tourist-heavy cities have kid-friendly museums with interactive exhibits.",
            ],
            "friends": [
                "Split costs using a shared expense app (Splitwise is free) to avoid awkward money conversations.",
                f"Book group accommodation (Airbnb house or hostel dorm) for significantly lower per-person costs.",
                "Assign a 'Day Lead' each day so decisions are made efficiently rather than by committee.",
            ],
        }
        tips = base.get(self.travel_type, [])
        # Add traveler-count-specific advice
        if self.travelers >= 4:
            tips.append(f"With {self.travelers} people, group transfers (private minivan) often cost less per person than individual taxis.")
        return tips[:3]

    # ─────────────────────────────────────────────────────────────────────────
    # TIMING ADVICE
    # ─────────────────────────────────────────────────────────────────────────
    def _timing_advice(self) -> dict:
        if not self._dest_data:
            return {"message": "No specific timing data available."}

        try:
            travel_month = int(self.start_date.split("-")[1]) if self.start_date else datetime.today().month
        except (IndexError, ValueError):
            travel_month = datetime.today().month

        month_name   = datetime(2024, travel_month, 1).strftime("%B")
        best         = self._dest_data.get("best_months", [])
        crowd        = self._advisor.get("crowd_months", [])
        weather_note = ""

        # Get climate note for this season
        if self._advisor.get("weather_notes"):
            notes = self._advisor["weather_notes"]
            if travel_month in [12, 1, 2] and "winter" in notes:
                weather_note = notes["winter"]
            elif travel_month in [3, 4, 5] and "spring" in notes:
                weather_note = notes["spring"]
            elif travel_month in [6, 7, 8] and "summer" in notes:
                weather_note = notes["summer"]
            elif travel_month in [9, 10, 11] and "autumn" in notes:
                weather_note = notes.get("autumn", notes.get("dry", ""))

        is_best    = travel_month in best
        is_crowded = travel_month in crowd

        if is_best and not is_crowded:
            rating = "ideal"
            message = f"✅ {month_name} is an ideal time to visit {self.dest.title()}. Great weather, manageable crowds."
        elif is_best and is_crowded:
            rating = "popular"
            message = f"📅 {month_name} is peak season for {self.dest.title()}. Excellent conditions but expect larger crowds and higher prices. Book early."
        elif is_crowded and not is_best:
            rating = "crowded"
            message = f"⚠️ {month_name} is a busy period in {self.dest.title()} without the best weather. You might get better value shifting by 4–6 weeks."
        else:
            rating = "shoulder"
            message = f"💡 {month_name} is shoulder season for {self.dest.title()}. Good value, fewer crowds, with acceptable conditions."

        return {
            "rating": rating,
            "month": month_name,
            "message": message,
            "weather_note": weather_note,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # AI SUMMARY (the opening statement the user sees first)
    # ─────────────────────────────────────────────────────────────────────────
    def _ai_summary(self) -> str:
        dest  = self.dest.title() or "your destination"
        b_ppd = self._budget_per_person_per_day
        days  = self.days
        ttype = self.travel_type
        t_str = f"{self.travelers} traveler{'s' if self.travelers > 1 else ''}"

        verdict = self._destination_verdict()
        alts    = self._find_alternatives()

        lines = [
            f"I've analysed your {days}-day {ttype} trip to {dest} for {t_str} "
            f"on a ${self.budget:,.0f} budget (${b_ppd:.0f}/person/day).",
        ]

        if verdict["verdict"] == "excellent":
            lines.append(f"{dest} is a strong match for your interests and budget.")
        elif verdict["verdict"] == "fair" and alts:
            top_alt = alts[0]
            saving  = top_alt.get("saving_per_day", 0)
            if saving > 0:
                lines.append(
                    f"You selected {dest}, but {top_alt['destination']} offers similar "
                    f"{', '.join(top_alt.get('tag_overlap', ['experiences'])[:2])} "
                    f"and would save approximately ${saving * days:,.0f} over your trip "
                    f"({abs(top_alt.get('budget_diff_pct', 0))}% cheaper per day)."
                )
            else:
                lines.append(
                    f"I've found {len(alts)} alternative destinations that closely match your interests."
                )

        flags = verdict.get("flags", [])
        if flags:
            lines.append(flags[0]["message"])

        weather_adjs = self._weather_adjustments()
        if weather_adjs:
            severe = [a for a in weather_adjs if a["severity"] == "high"]
            if severe:
                lines.append(
                    f"⚠️ Weather alert: Heavy rain is expected on {len(severe)} day(s) of your trip. "
                    f"I've suggested indoor alternatives in the itinerary."
                )

        opt = self._budget_optimization()
        total_save = sum(t.get("saving", 0) for t in opt if t.get("type") != "summary")
        if total_save > 50:
            lines.append(
                f"💰 I've identified ${total_save:,.0f} in potential savings through smarter choices — "
                f"see the Budget Optimization tab for details."
            )

        return " ".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAT ANSWER METHODS
    # ─────────────────────────────────────────────────────────────────────────
    def _answer_budget(self, q: str) -> str:
        dest  = self.dest.title()
        b_ppd = self._budget_per_person_per_day
        daily = self._dest_data.get("daily_budget", {}) if self._dest_data else {}
        mid   = daily.get("medium", 150)

        if b_ppd < mid * 0.7:
            return (
                f"Your budget of ${b_ppd:.0f}/person/day is below the comfortable minimum for {dest} "
                f"(~${mid}/day). Here's how to make it work: "
                f"① Stay in a hostel private room (~$30–60/night), "
                f"② Eat at local markets and lunch-only at restaurants (save 40%), "
                f"③ Use public transport exclusively. "
                f"Or consider {self._find_alternatives()[0]['destination'] if self._find_alternatives() else 'a more affordable destination'} "
                f"which fits your budget more comfortably."
            )

        opt = self._budget_optimization()
        hacks = [t for t in opt if t["type"] in ("swap", "local")][:2]
        if hacks:
            msgs = [h["message"] for h in hacks]
            return f"For {dest} on ${self.budget:,.0f}: " + " | ".join(msgs)

        return (
            f"Your ${b_ppd:.0f}/person/day budget is {'generous' if b_ppd > mid else 'workable'} for {dest}. "
            f"The mid-range daily cost is ~${mid}. "
            f"Key cost centres: accommodation ({self.accommodation}), "
            f"transport ({self.transport}), and dining. "
            f"Check my Budget tab for a full breakdown."
        )

    def _answer_alternatives(self, q: str) -> str:
        alts = self._find_alternatives()
        if not alts:
            return f"I don't have enough data to suggest specific alternatives to {self.dest.title()} right now."
        lines = [f"Here are my top alternatives to {self.dest.title()}:"]
        for i, alt in enumerate(alts[:3], 1):
            icon  = alt.get("budget_icon", "≈")
            lines.append(
                f"{i}. **{alt['destination']}** ({alt['country']}) — "
                f"{icon} {alt['budget_note']}. {alt['reason']}"
            )
        return "\n".join(lines)

    def _answer_weather(self, q: str) -> str:
        adjs = self._weather_adjustments()
        if not adjs:
            return (
                f"Based on the forecast for your dates, weather looks generally manageable in "
                f"{self.dest.title()}. I'll flag any bad weather days in your itinerary automatically."
            )
        severe = [a for a in adjs if a["severity"] == "high"]
        mild   = [a for a in adjs if a["severity"] == "medium"]
        parts  = []
        if severe:
            parts.append(f"⛈ Heavy rain/storm on Day(s) {', '.join(str(a['day']) for a in severe)}.")
        if mild:
            parts.append(f"🌦 Light rain on Day(s) {', '.join(str(a['day']) for a in mild)} — still manageable.")
        notes = self._advisor.get("weather_notes", {})
        try:
            m = int(self.start_date.split("-")[1]) if self.start_date else datetime.today().month
        except (IndexError, ValueError):
            m = datetime.today().month
        season = "winter" if m in [12,1,2] else "spring" if m in [3,4,5] else "summer" if m in [6,7,8] else "autumn"
        if season in notes:
            parts.append(notes[season])
        return " ".join(parts) if parts else f"Weather for {self.dest.title()} looks fine for your dates."

    def _answer_timing(self, q: str) -> str:
        timing = self._timing_advice()
        return f"{timing['message']} {timing.get('weather_note', '')}".strip()

    def _answer_hotel(self, q: str) -> str:
        dest = self.dest.title()
        if "budget" in q or "cheap" in q:
            return (
                f"Budget accommodation in {dest}: "
                f"Quality hostels with private rooms run $20–60/night. "
                f"Look at Generator Hostels (Europe), Khaosan (Asia), or local guesthouses. "
                f"I've included hotel recommendations in your Hotels tab."
            )
        if "resort" in q or "luxury" in q:
            return (
                f"For luxury in {dest}: "
                f"5-star hotels run ${int(self._dest_data.get('daily_budget', {}).get('high', 300)) * 0.6:.0f}–"
                f"{int(self._dest_data.get('daily_budget', {}).get('high', 300))}/night. "
                f"Book directly on hotel websites for the best rate and added perks like early check-in."
            )
        return (
            f"For {dest} with a {self.accommodation} preference and "
            f"${self._budget_per_person_per_day:.0f}/day budget: "
            f"I've curated 5 real hotel options in your Hotels tab, "
            f"sorted by value-for-money. The top pick costs "
            f"~${int(self._dest_data.get('daily_budget', {}).get('medium', 150) * 0.6)}/night."
        )

    def _answer_food(self, q: str) -> str:
        dest   = self.dest.title()
        rests  = self._dest_data.get("restaurants", []) if self._dest_data else []
        hacks  = self._advisor.get("budget_hacks", []) if self._advisor else []
        food_h = [h for h in hacks if any(w in h.lower() for w in ["food", "eat", "meal", "market", "restaurant"])]
        parts  = [f"Top restaurants in {dest}: {', '.join(rests[:3])}."]
        if food_h:
            parts.append(f"Budget tip: {food_h[0]}")
        parts.append(f"Your food budget is ~${int(self._budget_per_person_per_day * 0.35)}/day per person.")
        return " ".join(parts)

    def _answer_itinerary(self, q: str) -> str:
        adjs = self._weather_adjustments()
        if "adjust" in q or "change" in q or "weather" in q:
            if adjs:
                a = adjs[0]
                return (
                    f"I recommend adjusting Day {a['day']}: {a['message']} "
                    f"Indoor alternatives: {', '.join(a.get('indoor_alternatives', ['museum', 'gallery']))[:3]}."
                )
            return "Your current itinerary looks good — no major weather conflicts detected."
        return (
            f"Your {self.days}-day itinerary is structured with a theme per day "
            f"(cultural, adventure, food-focused, etc.) and weather-aware scheduling. "
            f"Each day includes 2–3 attractions with realistic travel time between them. "
            f"Open any day card to see the full timeline."
        )

    def _answer_visa(self, q: str) -> str:
        ease = self._advisor.get("visa_ease", "varies")
        return (
            f"Visa requirements for {self.dest.title()} are generally {ease} for most passport holders. "
            f"Always verify current entry requirements at your country's foreign affairs website "
            f"or iata.org/travel-centre before booking — requirements change frequently."
        )

    def _answer_tips(self, q: str) -> str:
        tips = self._advisor.get("pro_tips", [])
        if tips:
            return f"Top tips for {self.dest.title()}: " + " | ".join(tips[:3])
        return f"Check the AI Insights section in your plan for curated tips on {self.dest.title()}."

    def _answer_general(self, q: str) -> str:
        dest = self.dest.title()
        return (
            f"I'm your TripPilot advisor for your {self.days}-day trip to {dest}. "
            f"I can help you with: budget optimisation, destination comparisons, "
            f"weather adjustments, hotel choices, food recommendations, "
            f"timing advice, and itinerary changes. "
            f"What would you like to know?"
        )


# ─────────────────────────────────────────────────────────────────────────────
# MODULE-LEVEL HELPER  (used by app.py /api/ai/compare)
# Previously a free function in app.py — moved here where it belongs.
# ─────────────────────────────────────────────────────────────────────────────
def build_comparison_rec(dest1: str, dest2: str,
                          da: dict, db_dest: dict, context: dict) -> str:
    """
    Return a natural-language recommendation sentence comparing two destinations.
    Called by the /api/ai/compare route.
    """
    interests = context.get('interests', [])
    ttype     = context.get('travel_type', 'solo')
    budget    = float(context.get('budget', 1000))
    days      = int(context.get('days', 5))

    tags_a  = set(da.get('tags', []))
    tags_b  = set(db_dest.get('tags', []))
    user_i  = set(interests)
    score_a = len(tags_a & user_i)
    score_b = len(tags_b & user_i)

    mid_a   = da.get('daily_budget', {}).get('medium', 150)
    mid_b   = db_dest.get('daily_budget', {}).get('medium', 150)
    saving  = abs(mid_a - mid_b) * days
    cheaper = dest1.title() if mid_a <= mid_b else dest2.title()
    winner  = dest1.title() if score_a >= score_b else dest2.title()

    return (
        f"For a {ttype} trip with your interests, **{winner}** is the stronger match "
        f"(better alignment with your stated interests). "
        f"{cheaper} is the more budget-friendly option, saving approximately "
        f"${saving:,.0f} over {days} days. "
        f"If budget is a constraint, choose {cheaper}. "
        f"If experience quality is the priority, {winner} edges ahead."
    )
