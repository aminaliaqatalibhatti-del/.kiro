"""
TripPilot AI — Trip Engine
Generates AI-powered itineraries, recommendations, weather, hotels, and budgets.
All data is deterministic/seeded so the app works without external API keys.
"""
import random
import hashlib
from datetime import datetime, timedelta


# ── Destination knowledge base ────────────────────────────────────────────────
DESTINATIONS = {
    "paris": {
        "country": "France", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "French",
        "climate": "temperate", "best_months": [4,5,6,9,10],
        "category": "International Cities",
        "travel_style": ["culture","romance","family","solo"],
        "group_types": ["couple","solo","family","friends"],
        "trip_duration": {"min": 3, "ideal": 5, "max": 10},
        "tags": ["history","food","photography","shopping","art"],
        "daily_budget": {"low": 80, "medium": 180, "high": 400},
        "attractions": [
            {"name": "Eiffel Tower", "type": "landmark", "duration": "2h",
             "cost": 26, "rating": 4.8, "desc": "Iconic iron lattice tower with panoramic city views."},
            {"name": "The Louvre", "type": "museum", "duration": "3h",
             "cost": 17, "rating": 4.9, "desc": "World's largest art museum housing the Mona Lisa."},
            {"name": "Notre-Dame Cathedral", "type": "historic", "duration": "1.5h",
             "cost": 0, "rating": 4.7, "desc": "Medieval Gothic cathedral on the Île de la Cité."},
            {"name": "Champs-Élysées", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "World-famous boulevard lined with luxury boutiques."},
            {"name": "Montmartre", "type": "neighbourhood", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Bohemian hilltop neighbourhood with the Sacré-Cœur."},
            {"name": "Palace of Versailles", "type": "landmark", "duration": "4h",
             "cost": 20, "rating": 4.8, "desc": "Opulent royal château with spectacular gardens."},
            {"name": "Musée d'Orsay", "type": "museum", "duration": "2.5h",
             "cost": 16, "rating": 4.8, "desc": "Impressionist masterpieces in a former railway station."},
        ],
        "restaurants": ["Café de Flore","Le Jules Verne","Septime","L'Ambroisie","Breizh Café"],
        "image": "paris.jpg",
        "description": "The City of Light dazzles with world-class cuisine, art, and timeless romance.",
        "difficulty": "easy", "safety": "moderate",
    },
    "tokyo": {
        "country": "Japan", "continent": "Asia", "timezone": "JST",
        "currency": "JPY", "lang": "Japanese",
        "climate": "humid subtropical", "best_months": [3,4,10,11],
        "category": "International Cities",
        "travel_style": ['culture', 'adventure', 'solo', 'group'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 14},
        "tags": ["food","photography","nightlife","shopping","history","adventure"],
        "daily_budget": {"low": 60, "medium": 130, "high": 350},
        "attractions": [
            {"name": "Shibuya Crossing", "type": "landmark", "duration": "1h",
             "cost": 0, "rating": 4.7, "desc": "World's busiest pedestrian scramble crossing."},
            {"name": "Senso-ji Temple", "type": "religious", "duration": "1.5h",
             "cost": 0, "rating": 4.8, "desc": "Tokyo's oldest temple in the historic Asakusa district."},
            {"name": "Tsukiji Outer Market", "type": "food", "duration": "2h",
             "cost": 30, "rating": 4.8, "desc": "Fresh seafood and street food paradise."},
            {"name": "teamLab Planets", "type": "art", "duration": "2h",
             "cost": 32, "rating": 4.9, "desc": "Immersive digital art installations."},
            {"name": "Shinjuku Gyoen", "type": "nature", "duration": "2h",
             "cost": 5, "rating": 4.7, "desc": "Stunning national garden, spectacular during cherry blossom season."},
            {"name": "Akihabara", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "Electric Town — the heart of anime, manga, and electronics culture."},
        ],
        "restaurants": ["Sukiyabashi Jiro","Ichiran Ramen","Narisawa","Sushi Saito","Ukai Tofuya"],
        "image": "tokyo.jpg",
        "description": "A city where ancient tradition and hyper-modern technology coexist seamlessly.",
        "difficulty": "moderate", "safety": "very safe",
    },
    "dubai": {
        "country": "UAE", "continent": "Asia", "timezone": "GST",
        "currency": "AED", "lang": "Arabic/English",
        "climate": "arid desert", "best_months": [11,12,1,2,3],
        "category": "International Cities",
        "travel_style": ['luxury', 'shopping', 'adventure', 'family'],
        "group_types": ['couple', 'family', 'friends', 'solo'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["shopping","adventure","nightlife","luxury","food"],
        "daily_budget": {"low": 100, "medium": 250, "high": 700},
        "attractions": [
            {"name": "Burj Khalifa", "type": "landmark", "duration": "2h",
             "cost": 35, "rating": 4.8, "desc": "World's tallest building with sky-high observation decks."},
            {"name": "Dubai Mall", "type": "shopping", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "One of the world's largest shopping malls with an aquarium."},
            {"name": "Desert Safari", "type": "adventure", "duration": "6h",
             "cost": 75, "rating": 4.9, "desc": "Dune bashing, camel riding, and a BBQ under the stars."},
            {"name": "The Palm Jumeirah", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "World-famous artificial palm-shaped island."},
            {"name": "Dubai Frame", "type": "landmark", "duration": "1.5h",
             "cost": 14, "rating": 4.6, "desc": "A massive picture-frame structure bridging old and new Dubai."},
            {"name": "Gold Souk", "type": "shopping", "duration": "1.5h",
             "cost": 0, "rating": 4.7, "desc": "Traditional market glittering with gold jewellery."},
        ],
        "restaurants": ["Nobu Dubai","Zuma","Al Fanar","Pierchic","Ossiano"],
        "image": "dubai.jpg",
        "description": "A gleaming desert metropolis of superlatives — tallest, largest, most luxurious.",
        "difficulty": "easy", "safety": "very safe",
    },
    "bali": {
        "country": "Indonesia", "continent": "Asia", "timezone": "WITA",
        "currency": "IDR", "lang": "Indonesian/Balinese",
        "climate": "tropical", "best_months": [4,5,6,7,8,9],
        "category": "Beaches & Coastal",
        "travel_style": ['nature', 'romance', 'adventure', 'budget'],
        "group_types": ['couple', 'solo', 'friends', 'family'],
        "trip_duration": {"min": 5, "ideal": 8, "max": 14},
        "tags": ["nature","adventure","photography","religious","food"],
        "daily_budget": {"low": 35, "medium": 90, "high": 280},
        "attractions": [
            {"name": "Tanah Lot Temple", "type": "religious", "duration": "2h",
             "cost": 3, "rating": 4.8, "desc": "Sea temple perched on a dramatic rocky outcrop."},
            {"name": "Ubud Monkey Forest", "type": "nature", "duration": "2h",
             "cost": 4, "rating": 4.7, "desc": "Sacred monkey sanctuary in the lush jungle."},
            {"name": "Mount Batur", "type": "adventure", "duration": "6h",
             "cost": 60, "rating": 4.9, "desc": "Sunrise trek up an active volcano."},
            {"name": "Tegallalang Rice Terraces", "type": "nature", "duration": "2h",
             "cost": 2, "rating": 4.8, "desc": "Stunning stepped rice paddies north of Ubud."},
            {"name": "Seminyak Beach", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Upscale beach strip with world-class sunsets."},
        ],
        "restaurants": ["Locavore","Merah Putih","Warung Babi Guling Ibu Oka","Mozaic","Sarong"],
        "image": "bali.jpg",
        "description": "Island of the Gods — a lush paradise of temples, rice terraces, and surf.",
        "difficulty": "easy", "safety": "safe",
    },
    "new york": {
        "country": "USA", "continent": "North America", "timezone": "EST",
        "currency": "USD", "lang": "English",
        "climate": "humid continental", "best_months": [4,5,9,10,11],
        "category": "International Cities",
        "travel_style": ['culture', 'shopping', 'nightlife', 'family'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nightlife","shopping","food","history","art","photography"],
        "daily_budget": {"low": 120, "medium": 280, "high": 700},
        "attractions": [
            {"name": "Central Park", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "843-acre urban oasis in the heart of Manhattan."},
            {"name": "Metropolitan Museum of Art", "type": "museum", "duration": "3h",
             "cost": 25, "rating": 4.9, "desc": "One of the world's greatest art museums."},
            {"name": "Times Square", "type": "landmark", "duration": "1h",
             "cost": 0, "rating": 4.5, "desc": "The neon-lit commercial hub of NYC."},
            {"name": "Brooklyn Bridge", "type": "landmark", "duration": "1h",
             "cost": 0, "rating": 4.7, "desc": "Iconic suspension bridge with stunning skyline views."},
            {"name": "Empire State Building", "type": "landmark", "duration": "1.5h",
             "cost": 44, "rating": 4.7, "desc": "Art Deco skyscraper with sweeping 360° views."},
            {"name": "The High Line", "type": "nature", "duration": "1.5h",
             "cost": 0, "rating": 4.7, "desc": "Elevated linear park built on former railway tracks."},
        ],
        "restaurants": ["Le Bernardin","Katz's Delicatessen","Per Se","Gramercy Tavern","J.G. Melon"],
        "image": "newyork.jpg",
        "description": "The city that never sleeps — relentlessly energetic, diverse, and iconic.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "istanbul": {
        "country": "Turkey", "continent": "Europe/Asia", "timezone": "TRT",
        "currency": "TRY", "lang": "Turkish",
        "climate": "mediterranean", "best_months": [4,5,9,10],
        "category": "Historical & Cultural",
        "travel_style": ['culture', 'food', 'photography', 'solo'],
        "group_types": ['solo', 'couple', 'family', 'friends'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["history","food","religious","photography","shopping"],
        "daily_budget": {"low": 40, "medium": 100, "high": 280},
        "attractions": [
            {"name": "Hagia Sophia", "type": "historic", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "Awe-inspiring Byzantine basilica turned mosque."},
            {"name": "Grand Bazaar", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "One of the world's oldest and largest covered markets."},
            {"name": "Topkapi Palace", "type": "historic", "duration": "3h",
             "cost": 15, "rating": 4.8, "desc": "Imperial palace of the Ottoman sultans."},
            {"name": "Blue Mosque", "type": "religious", "duration": "1.5h",
             "cost": 0, "rating": 4.8, "desc": "Stunning 17th-century mosque with six minarets."},
            {"name": "Bosphorus Cruise", "type": "nature", "duration": "2h",
             "cost": 15, "rating": 4.8, "desc": "Scenic boat ride between two continents."},
        ],
        "restaurants": ["Mikla","Karaköy Lokantası","Çiya Sofrası","Nusret","Asitane"],
        "image": "istanbul.jpg",
        "description": "Where East meets West — a mesmerizing blend of ancient empires and modern energy.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "rome": {
        "country": "Italy", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "Italian",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "International Cities",
        "travel_style": ['culture', 'history', 'romance', 'food'],
        "group_types": ['couple', 'solo', 'family', 'friends'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["history","food","photography","religious","art"],
        "daily_budget": {"low": 75, "medium": 160, "high": 380},
        "attractions": [
            {"name": "Colosseum", "type": "historic", "duration": "2h",
             "cost": 16, "rating": 4.9, "desc": "Ancient amphitheatre, symbol of the Roman Empire."},
            {"name": "Vatican Museums & Sistine Chapel", "type": "museum", "duration": "3h",
             "cost": 20, "rating": 4.9, "desc": "Home of Michelangelo's breathtaking ceiling fresco."},
            {"name": "Trevi Fountain", "type": "landmark", "duration": "45m",
             "cost": 0, "rating": 4.8, "desc": "Baroque masterpiece — toss a coin and return to Rome."},
            {"name": "Roman Forum", "type": "historic", "duration": "2h",
             "cost": 16, "rating": 4.7, "desc": "The nerve centre of ancient Roman public life."},
            {"name": "Pantheon", "type": "historic", "duration": "1h",
             "cost": 5, "rating": 4.8, "desc": "Best-preserved ancient Roman building still standing."},
        ],
        "restaurants": ["La Pergola","Da Enzo al 29","Roscioli","Il Sorpasso","Tonnarello"],
        "image": "rome.jpg",
        "description": "The Eternal City — a living museum where every street corner tells a 3,000-year story.",
        "difficulty": "easy", "safety": "moderate",
    },
    "maldives": {
        "country": "Maldives", "continent": "Asia", "timezone": "MVT",
        "currency": "MVR", "lang": "Dhivehi/English",
        "climate": "tropical", "best_months": [11,12,1,2,3,4],
        "category": "Beaches & Coastal",
        "travel_style": ['luxury', 'romance', 'nature', 'diving'],
        "group_types": ['couple', 'solo', 'family'],
        "trip_duration": {"min": 5, "ideal": 7, "max": 10},
        "tags": ["nature","adventure","luxury","photography"],
        "daily_budget": {"low": 150, "medium": 400, "high": 1200},
        "attractions": [
            {"name": "Snorkelling the House Reef", "type": "adventure", "duration": "3h",
             "cost": 30, "rating": 4.9, "desc": "Crystal-clear lagoons teeming with marine life."},
            {"name": "Sunset Dolphin Cruise", "type": "nature", "duration": "2h",
             "cost": 50, "rating": 4.9, "desc": "Spot spinner dolphins in their natural habitat."},
            {"name": "Male Fish Market", "type": "food", "duration": "1h",
             "cost": 0, "rating": 4.5, "desc": "Vibrant local market showcasing Maldivian seafood culture."},
        ],
        "restaurants": ["Ithaa Undersea Restaurant","Plates","Vilu Restaurant","Sea Breeze Cafe"],
        "image": "maldives.jpg",
        "description": "An archipelago of paradises — overwater bungalows and impossibly turquoise waters.",
        "difficulty": "easy", "safety": "very safe",
    },

    # ── Nature & Mountains — Pakistan ─────────────────────────────────────────
    "kaghan": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Hindko",
        "climate": "alpine", "best_months": [5,6,7,8,9],
        "category": "Nature & Mountains",
        "travel_style": ['nature', 'adventure', 'photography', 'trekking'],
        "group_types": ['solo', 'friends', 'couple', 'family'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 7},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 18, "medium": 45, "high": 110},
        "attractions": [
            {"name": "Shogran Hill Station", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.8, "desc": "Lush hilltop plateau with stunning views of the Makra Peak."},
            {"name": "Siri Payee Meadows", "type": "nature", "duration": "5h",
             "cost": 0, "rating": 4.9, "desc": "Remote alpine meadows above Shogran accessible only on foot."},
            {"name": "Dudipat Sar Lake", "type": "nature", "duration": "6h",
             "cost": 0, "rating": 4.8, "desc": "High-altitude glacial lake at 3,800m — a trekker's paradise."},
            {"name": "Ansoo Lake", "type": "nature", "duration": "8h",
             "cost": 0, "rating": 4.9, "desc": "Tear-shaped lake at 4,245m, one of Pakistan's most remote gems."},
        ],
        "restaurants": ["Shogran Huts","Kaghan Valley Hotels","PTDC Motel Kaghan"],
        "image": "kaghan.jpg",
        "description": "The enchanting Kaghan Valley — a ribbon of emerald meadows, blue lakes, and snowcapped peaks.",
        "difficulty": "moderate", "safety": "safe",
    },
    "hunza": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Burusho",
        "climate": "alpine", "best_months": [4,5,6,7,8,9],
        "category": "Nature & Mountains",
        "travel_style": ['nature', 'adventure', 'photography', 'culture'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 10},
        "tags": ["nature","adventure","photography","history"],
        "daily_budget": {"low": 25, "medium": 60, "high": 150},
        "attractions": [
            {"name": "Baltit Fort", "type": "historic", "duration": "2h",
             "cost": 5, "rating": 4.8, "desc": "900-year-old fort overlooking the Hunza valley."},
            {"name": "Eagle's Nest Viewpoint", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.9, "desc": "Panoramic views of Rakaposhi and surrounding peaks."},
            {"name": "Attabad Lake", "type": "nature", "duration": "3h",
             "cost": 5, "rating": 4.8, "desc": "Stunning turquoise lake formed by a 2010 landslide."},
            {"name": "Karimabad Bazaar", "type": "shopping", "duration": "1.5h",
             "cost": 0, "rating": 4.5, "desc": "Colourful local market with handicrafts and dried fruits."},
        ],
        "restaurants": ["Cafe De Hunza","Old Hunza Inn","Serena Hotel Restaurant","Baltit Kitchen"],
        "image": "hunza.jpg",
        "description": "A mythical valley where the Karakoram, Hindu Kush, and Himalayas converge.",
        "difficulty": "moderate", "safety": "safe",
    },
    "skardu": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Balti",
        "climate": "alpine", "best_months": [5,6,7,8,9],
        "category": "Nature & Mountains",
        "travel_style": ['adventure', 'trekking', 'photography', 'nature'],
        "group_types": ['solo', 'friends', 'couple'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 14},
        "tags": ["adventure","nature","photography"],
        "daily_budget": {"low": 20, "medium": 55, "high": 130},
        "attractions": [
            {"name": "Shangrila Resort Lake", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "Heaven on Earth — a paradise lake surrounded by mountains."},
            {"name": "Deosai National Park", "type": "nature", "duration": "8h",
             "cost": 10, "rating": 4.9, "desc": "World's second-highest plateau, home to Himalayan brown bear."},
            {"name": "Skardu Fort", "type": "historic", "duration": "1.5h",
             "cost": 3, "rating": 4.6, "desc": "Ancient fort with commanding views over the Indus valley."},
            {"name": "Upper Kachura Lake", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.9, "desc": "Crystal-blue high-altitude lake accessible by jeep track."},
        ],
        "restaurants": ["Shangrila Restaurant","Mashabrum Restaurant","Hotel Concordia Dining"],
        "image": "skardu.jpg",
        "description": "Gateway to the world's highest peaks — K2 base camp starts here.",
        "difficulty": "hard", "safety": "safe",
    },
    "fairy meadows": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Shina",
        "climate": "alpine", "best_months": [5,6,7,8],
        "category": "Nature & Mountains",
        "travel_style": ['adventure', 'trekking', 'photography', 'nature'],
        "group_types": ['solo', 'friends', 'couple'],
        "trip_duration": {"min": 2, "ideal": 3, "max": 5},
        "tags": ["adventure","nature","photography"],
        "daily_budget": {"low": 20, "medium": 50, "high": 100},
        "attractions": [
            {"name": "Nanga Parbat Base Camp Trek", "type": "adventure", "duration": "6h",
             "cost": 0, "rating": 4.9, "desc": "Trek to the base of the world's 9th highest mountain."},
            {"name": "Fairy Meadows Campsite", "type": "nature", "duration": "4h",
             "cost": 10, "rating": 4.9, "desc": "Alpine meadows with direct views of Nanga Parbat."},
            {"name": "Raikot Bridge", "type": "landmark", "duration": "1h",
             "cost": 0, "rating": 4.5, "desc": "Suspension bridge over the roaring Indus River."},
        ],
        "restaurants": ["Fairy Meadows Huts","Raikot Sarai Guesthouse"],
        "image": "fairy_meadows.jpg",
        "description": "A breathtaking alpine meadow at the foot of Nanga Parbat, the Killer Mountain.",
        "difficulty": "hard", "safety": "safe",
    },
    "naran": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Hindko",
        "climate": "alpine", "best_months": [5,6,7,8,9],
        "category": "Nature & Mountains",
        "travel_style": ['nature', 'photography', 'adventure', 'family'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 6},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 20, "medium": 50, "high": 120},
        "attractions": [
            {"name": "Saiful Muluk Lake", "type": "nature", "duration": "4h",
             "cost": 5, "rating": 4.9, "desc": "Legendary lake at 10,578 ft surrounded by snow-capped peaks."},
            {"name": "Lulusar Lake", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.8, "desc": "Serene turquoise lake on the Babusar Pass route."},
            {"name": "Babusar Pass", "type": "adventure", "duration": "5h",
             "cost": 0, "rating": 4.8, "desc": "4,173m mountain pass with sweeping Himalayan panoramas."},
        ],
        "restaurants": ["Pine Park Hotel","Lalazar Hotel Restaurant","PTDC Motel Naran"],
        "image": "naran.jpg",
        "description": "The crown jewel of Kaghan Valley — where mountains kiss the sky.",
        "difficulty": "moderate", "safety": "safe",
    },
    "swat": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Pashto",
        "climate": "temperate", "best_months": [4,5,6,7,8,9,10],
        "category": "Nature & Mountains",
        "travel_style": ['nature', 'history', 'adventure', 'photography'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 7},
        "tags": ["nature","history","adventure","photography"],
        "daily_budget": {"low": 20, "medium": 50, "high": 110},
        "attractions": [
            {"name": "Malam Jabba Ski Resort", "type": "adventure", "duration": "6h",
             "cost": 20, "rating": 4.7, "desc": "Pakistan's premier ski resort with panoramic mountain views."},
            {"name": "Swat Museum", "type": "museum", "duration": "2h",
             "cost": 3, "rating": 4.6, "desc": "Gandhara Buddhist artefacts spanning 2,000 years of history."},
            {"name": "Kalam Valley", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.8, "desc": "Lush alpine valley with dense forests and waterfalls."},
            {"name": "Fizagat Park", "type": "nature", "duration": "2h",
             "cost": 2, "rating": 4.4, "desc": "Riverside park along the Swat River with ancient ruins."},
        ],
        "restaurants": ["Pameer Hotel","White Palace Hotel Restaurant","Rock City Restaurant"],
        "image": "swat.jpg",
        "description": "The Switzerland of Pakistan — a valley of emerald meadows and ancient Buddhist sites.",
        "difficulty": "easy", "safety": "moderate",
    },
    "murree": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Punjabi",
        "climate": "temperate", "best_months": [3,4,5,6,7,8,9,10],
        "category": "Nature & Mountains",
        "travel_style": ['nature', 'family', 'weekend', 'photography'],
        "group_types": ['family', 'couple', 'friends'],
        "trip_duration": {"min": 1, "ideal": 2, "max": 4},
        "tags": ["nature","food","photography"],
        "daily_budget": {"low": 20, "medium": 50, "high": 100},
        "attractions": [
            {"name": "Mall Road Murree", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.5, "desc": "Charming colonial-era promenade with shops and viewpoints."},
            {"name": "Pindi Point Chairlift", "type": "adventure", "duration": "1.5h",
             "cost": 8, "rating": 4.7, "desc": "Cable car ride over pine forests with Himalayan views."},
            {"name": "Kashmir Point", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "Panoramic viewpoint overlooking the Murree hills."},
        ],
        "restaurants": ["Cecil Hotel Restaurant","Lockwood Hotel","Mall Road Cafes"],
        "image": "murree.jpg",
        "description": "Pakistan's favourite hill station — cool pine forests and British-era charm.",
        "difficulty": "easy", "safety": "safe",
    },
    "neelum valley": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Kashmiri",
        "climate": "temperate", "best_months": [4,5,6,7,8,9,10],
        "category": "Nature & Mountains",
        "travel_style": ['nature', 'adventure', 'photography', 'trekking'],
        "group_types": ['solo', 'friends', 'couple'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 20, "medium": 50, "high": 110},
        "attractions": [
            {"name": "Ratti Gali Lake", "type": "nature", "duration": "5h",
             "cost": 0, "rating": 4.9, "desc": "Remote high-altitude lake accessible by trekking only."},
            {"name": "Sharda Fort Ruins", "type": "historic", "duration": "2h",
             "cost": 0, "rating": 4.5, "desc": "Ancient ruins of Sharda university, one of India's oldest."},
            {"name": "Arang Kel Village", "type": "adventure", "duration": "6h",
             "cost": 0, "rating": 4.8, "desc": "Isolated hilltop village accessible only by ropeway."},
        ],
        "restaurants": ["Neelum Valley Guest Houses","Sharda Guesthouse"],
        "image": "neelum_valley.jpg",
        "description": "A pristine river valley in Azad Kashmir — nature at its most unspoiled.",
        "difficulty": "moderate", "safety": "safe",
    },

    # ── Historical & Cultural ─────────────────────────────────────────────────
    "lahore": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Punjabi",
        "climate": "semi-arid", "best_months": [10,11,12,1,2,3],
        "category": "Historical & Cultural",
        "travel_style": ['culture', 'food', 'history', 'photography'],
        "group_types": ['solo', 'couple', 'family', 'friends'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 6},
        "tags": ["history","food","shopping","art","religious"],
        "daily_budget": {"low": 20, "medium": 55, "high": 130},
        "attractions": [
            {"name": "Lahore Fort", "type": "historic", "duration": "3h",
             "cost": 5, "rating": 4.8, "desc": "Mughal imperial fort, UNESCO World Heritage Site."},
            {"name": "Badshahi Mosque", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "One of the world's largest mosques, built in 1673."},
            {"name": "Shalimar Gardens", "type": "nature", "duration": "2h",
             "cost": 3, "rating": 4.7, "desc": "UNESCO-listed Mughal pleasure garden with terraced fountains."},
            {"name": "Walled City Food Trail", "type": "food", "duration": "3h",
             "cost": 10, "rating": 4.9, "desc": "Legendary street food — nihari, paye, and anda shami in the old city."},
            {"name": "Minar-e-Pakistan", "type": "landmark", "duration": "1h",
             "cost": 2, "rating": 4.7, "desc": "Monument marking where Pakistan was declared in 1940."},
        ],
        "restaurants": ["Cuckoo's Den","Haveli Restaurant","Butt Karahi","Phajja Siri Paye"],
        "image": "lahore.jpg",
        "description": "The cultural capital of Pakistan — a city of Mughal grandeur, great food, and vibrant arts.",
        "difficulty": "easy", "safety": "moderate",
    },
    "taxila": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Punjabi",
        "climate": "semi-arid", "best_months": [10,11,12,1,2,3,4],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'photography', 'culture', 'education'],
        "group_types": ['solo', 'couple', 'family'],
        "trip_duration": {"min": 1, "ideal": 2, "max": 3},
        "tags": ["history","art","photography"],
        "daily_budget": {"low": 15, "medium": 40, "high": 90},
        "attractions": [
            {"name": "Taxila Museum", "type": "museum", "duration": "2h",
             "cost": 5, "rating": 4.7, "desc": "World-class Gandharan Buddhist artefacts from 3,000 years of history."},
            {"name": "Jaulian Monastery", "type": "historic", "duration": "2h",
             "cost": 5, "rating": 4.8, "desc": "Remarkably preserved 2nd-century Buddhist monastery."},
            {"name": "Dharmarajika Stupa", "type": "historic", "duration": "1.5h",
             "cost": 3, "rating": 4.6, "desc": "Ancient stupa marking one of Taxila's most sacred sites."},
        ],
        "restaurants": ["Taxila Hotel Restaurant","PTDC Taxila Motel"],
        "image": "taxila.jpg",
        "description": "Ancient Gandharan capital — one of Asia's most important archaeological sites.",
        "difficulty": "easy", "safety": "safe",
    },
    "multan": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Punjabi/Saraiki",
        "climate": "hot desert", "best_months": [10,11,12,1,2,3],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'culture', 'religious', 'shopping'],
        "group_types": ['solo', 'family', 'couple'],
        "trip_duration": {"min": 1, "ideal": 2, "max": 4},
        "tags": ["history","religious","shopping","art"],
        "daily_budget": {"low": 15, "medium": 40, "high": 90},
        "attractions": [
            {"name": "Shrine of Bahauddin Zakariya", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "Sufi shrine of the revered 13th-century saint."},
            {"name": "Multan Fort", "type": "historic", "duration": "2h",
             "cost": 3, "rating": 4.5, "desc": "Ancient fort dating back over 2,000 years."},
            {"name": "Hussain Agahi Bazaar", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "Famous for blue pottery, embroidery, and camel skin lamps."},
        ],
        "restaurants": ["Nayab Restaurant","Sohan Halwa Shops","Burns Road Multan"],
        "image": "multan.jpg",
        "description": "City of Saints, Sufis, and beautiful blue pottery — Pakistan's spiritual heartland.",
        "difficulty": "easy", "safety": "moderate",
    },
    "peshawar": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Pashto",
        "climate": "semi-arid", "best_months": [10,11,12,1,2,3,4],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'culture', 'food', 'photography'],
        "group_types": ['solo', 'couple', 'family'],
        "trip_duration": {"min": 2, "ideal": 3, "max": 5},
        "tags": ["history","food","shopping","art"],
        "daily_budget": {"low": 15, "medium": 40, "high": 90},
        "attractions": [
            {"name": "Qissa Khwani Bazaar", "type": "historic", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "The legendary Street of Storytellers — one of Asia's oldest bazaars."},
            {"name": "Peshawar Museum", "type": "museum", "duration": "2h",
             "cost": 3, "rating": 4.7, "desc": "Home to one of the finest Gandhara Buddhist collections in the world."},
            {"name": "Bala Hisar Fort", "type": "historic", "duration": "1.5h",
             "cost": 0, "rating": 4.5, "desc": "Ancient fort still used as a military headquarters."},
            {"name": "Sethi House Museum", "type": "museum", "duration": "1.5h",
             "cost": 3, "rating": 4.6, "desc": "Stunning 19th-century merchant mansion with intricate woodwork."},
        ],
        "restaurants": ["Namak Mandi Chapli Kebabs","Jahangir Restaurant","Dilbar Hotel"],
        "image": "peshawar.jpg",
        "description": "One of Asia's oldest cities — a crossroads of civilisations where the Silk Road began.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "bahawalpur": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Saraiki",
        "climate": "hot desert", "best_months": [10,11,12,1,2,3],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'photography', 'nature', 'culture'],
        "group_types": ['solo', 'couple', 'family'],
        "trip_duration": {"min": 1, "ideal": 2, "max": 4},
        "tags": ["history","nature","photography"],
        "daily_budget": {"low": 15, "medium": 40, "high": 80},
        "attractions": [
            {"name": "Noor Mahal Palace", "type": "historic", "duration": "2h",
             "cost": 5, "rating": 4.7, "desc": "Stunning Italian Baroque palace of the Nawabs of Bahawalpur."},
            {"name": "Derawar Fort", "type": "historic", "duration": "3h",
             "cost": 5, "rating": 4.8, "desc": "Massive 40-metre-high desert fort rising from the Cholistan desert."},
            {"name": "Lal Suhanra National Park", "type": "nature", "duration": "4h",
             "cost": 3, "rating": 4.6, "desc": "Desert wildlife sanctuary with blackbuck, deer, and migratory birds."},
        ],
        "restaurants": ["Sadiq Garh Palace Restaurant","Bahawalpur Hotel Dining"],
        "image": "bahawalpur.jpg",
        "description": "The princely city — Nawabi palaces, a desert fort, and sand dunes of Cholistan.",
        "difficulty": "easy", "safety": "safe",
    },

    # ── Religious Tourism ─────────────────────────────────────────────────────
    "makkah": {
        "country": "Saudi Arabia", "continent": "Asia", "timezone": "AST",
        "currency": "SAR", "lang": "Arabic",
        "climate": "hot desert", "best_months": [11,12,1,2,3],
        "category": "Religious Tourism",
        "travel_style": ['religious', 'pilgrimage', 'spiritual'],
        "group_types": ['solo', 'family', 'couple', 'group'],
        "trip_duration": {"min": 3, "ideal": 7, "max": 14},
        "tags": ["religious"],
        "daily_budget": {"low": 80, "medium": 180, "high": 500},
        "attractions": [
            {"name": "Masjid al-Haram", "type": "religious", "duration": "4h",
             "cost": 0, "rating": 5.0, "desc": "The holiest mosque in Islam, surrounding the Kaaba."},
            {"name": "Jabal al-Nour", "type": "religious", "duration": "3h",
             "cost": 0, "rating": 4.8, "desc": "Mountain with the Cave of Hira, where the first Quranic revelation came."},
            {"name": "Mina & Muzdalifah", "type": "religious", "duration": "4h",
             "cost": 0, "rating": 4.7, "desc": "Sacred plains central to the Hajj pilgrimage."},
        ],
        "restaurants": ["Al Baik","Makkah Marriott Dining","Zamzam Tower Restaurants"],
        "image": "makkah.jpg",
        "description": "The holiest city in Islam — the birthplace of the Prophet and destination of the Hajj.",
        "difficulty": "moderate", "safety": "very safe",
    },
    "madinah": {
        "country": "Saudi Arabia", "continent": "Asia", "timezone": "AST",
        "currency": "SAR", "lang": "Arabic",
        "climate": "hot desert", "best_months": [11,12,1,2,3],
        "category": "Religious Tourism",
        "travel_style": ['religious', 'pilgrimage', 'spiritual'],
        "group_types": ['solo', 'family', 'couple', 'group'],
        "trip_duration": {"min": 2, "ideal": 5, "max": 10},
        "tags": ["religious"],
        "daily_budget": {"low": 70, "medium": 160, "high": 450},
        "attractions": [
            {"name": "Masjid al-Nabawi", "type": "religious", "duration": "4h",
             "cost": 0, "rating": 5.0, "desc": "The Prophet's Mosque — second holiest site in Islam."},
            {"name": "Quba Mosque", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "The first mosque built in Islamic history."},
            {"name": "Uhud Mountain", "type": "historic", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Site of the Battle of Uhud, a pivotal moment in Islamic history."},
        ],
        "restaurants": ["Al Baik Madinah","Dar al Madinah Hotel Restaurant","Al Tazaj"],
        "image": "madinah.jpg",
        "description": "The City of the Prophet — a place of deep spiritual peace and Islamic heritage.",
        "difficulty": "easy", "safety": "very safe",
    },
    "jerusalem": {
        "country": "Israel/Palestine", "continent": "Asia", "timezone": "IST",
        "currency": "ILS", "lang": "Hebrew/Arabic/English",
        "climate": "mediterranean", "best_months": [3,4,5,9,10,11],
        "category": "Religious Tourism",
        "travel_style": ['religious', 'history', 'culture', 'photography'],
        "group_types": ['solo', 'couple', 'family', 'group'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["religious","history","photography"],
        "daily_budget": {"low": 60, "medium": 150, "high": 400},
        "attractions": [
            {"name": "Al-Aqsa Mosque", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "Third holiest site in Islam on the Temple Mount."},
            {"name": "Church of the Holy Sepulchre", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "Site of Jesus's crucifixion and resurrection for Christians."},
            {"name": "Western Wall", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "Holiest accessible site in Judaism."},
            {"name": "Old City Souq", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Ancient market streets selling spices, crafts, and holy items."},
        ],
        "restaurants": ["Abu Shukri","Machneyuda","Azura","Village Green"],
        "image": "jerusalem.jpg",
        "description": "The holiest city for three Abrahamic religions — 3,000 years of history in every stone.",
        "difficulty": "moderate", "safety": "moderate",
    },

    # ── Beaches & Coastal ─────────────────────────────────────────────────────
    "karachi": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Sindhi",
        "climate": "hot semi-arid", "best_months": [11,12,1,2,3],
        "category": "Beaches & Coastal",
        "travel_style": ['food', 'culture', 'shopping', 'nightlife'],
        "group_types": ['family', 'friends', 'solo', 'couple'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 6},
        "tags": ["food","shopping","nightlife","history"],
        "daily_budget": {"low": 20, "medium": 55, "high": 140},
        "attractions": [
            {"name": "Clifton Beach", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.4, "desc": "Popular urban beach with camel rides and street food."},
            {"name": "Quaid-e-Azam Mausoleum", "type": "historic", "duration": "1.5h",
             "cost": 0, "rating": 4.7, "desc": "Striking white marble tomb of Pakistan's founding father."},
            {"name": "Mohatta Palace Museum", "type": "museum", "duration": "2h",
             "cost": 3, "rating": 4.6, "desc": "Beautiful pink Jodhpur-stone palace turned art museum."},
            {"name": "Burns Road Food Street", "type": "food", "duration": "3h",
             "cost": 10, "rating": 4.9, "desc": "Legendary street with 100+ years of Karachi's best food."},
        ],
        "restaurants": ["Kolachi Restaurant","Sakura","BBQ Tonight","Barbecue Tonite"],
        "image": "karachi.jpg",
        "description": "Pakistan's economic capital — a megacity of 20 million with incredible food and energy.",
        "difficulty": "easy", "safety": "moderate",
    },
    "gwadar": {
        "country": "Pakistan", "continent": "Asia", "timezone": "PKT",
        "currency": "PKR", "lang": "Urdu/Balochi",
        "climate": "hot desert", "best_months": [10,11,12,1,2,3],
        "category": "Beaches & Coastal",
        "travel_style": ['nature', 'adventure', 'photography', 'coastal'],
        "group_types": ['solo', 'friends', 'couple'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 6},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 20, "medium": 50, "high": 110},
        "attractions": [
            {"name": "Hammerhead Point", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "Dramatic cliffside viewpoint over the Arabian Sea."},
            {"name": "Gwadar Harbour", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "Deep-sea port and CPEC hub transforming Balochistan."},
            {"name": "Ormara Beach", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Pristine unspoiled beach with crystal-clear Arabian Sea waters."},
        ],
        "restaurants": ["Pearl Continental Gwadar","Faran Hotel Restaurant"],
        "image": "gwadar.jpg",
        "description": "Pakistan's rising port city on the Arabian Sea — the jewel of CPEC.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "antalya": {
        "country": "Turkey", "continent": "Europe", "timezone": "TRT",
        "currency": "TRY", "lang": "Turkish",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "Beaches & Coastal",
        "travel_style": ['beach', 'history', 'family', 'nature'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nature","history","food","adventure"],
        "daily_budget": {"low": 35, "medium": 90, "high": 250},
        "attractions": [
            {"name": "Konyaalti Beach", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.7, "desc": "Stunning pebble beach against a backdrop of the Taurus Mountains."},
            {"name": "Antalya Old Town (Kaleici)", "type": "historic", "duration": "3h",
             "cost": 0, "rating": 4.8, "desc": "Charming Roman-era harbour district with winding lanes."},
            {"name": "Duden Waterfalls", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Spectacular waterfall plunging directly into the Mediterranean."},
            {"name": "Aspendos Theatre", "type": "historic", "duration": "2h",
             "cost": 8, "rating": 4.8, "desc": "Best-preserved Roman theatre in the world, still used today."},
        ],
        "restaurants": ["Vanilla Restaurant","Parlak Restaurant","Konyaalti Cafes","Serpme"],
        "image": "antalya.jpg",
        "description": "Turkey's turquoise coast — ancient ruins, crystal waters, and 300 days of sunshine.",
        "difficulty": "easy", "safety": "safe",
    },

    # ── International Cities ──────────────────────────────────────────────────
    "abu dhabi": {
        "country": "UAE", "continent": "Asia", "timezone": "GST",
        "currency": "AED", "lang": "Arabic/English",
        "climate": "arid desert", "best_months": [11,12,1,2,3],
        "category": "International Cities",
        "travel_style": ['luxury', 'culture', 'family', 'adventure'],
        "group_types": ['family', 'couple', 'solo', 'friends'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 7},
        "tags": ["luxury","history","art","food"],
        "daily_budget": {"low": 80, "medium": 200, "high": 600},
        "attractions": [
            {"name": "Sheikh Zayed Grand Mosque", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "One of the world's largest and most beautiful mosques."},
            {"name": "Louvre Abu Dhabi", "type": "museum", "duration": "3h",
             "cost": 18, "rating": 4.8, "desc": "Stunning cross-cultural art museum under a latticed dome."},
            {"name": "Yas Island", "type": "adventure", "duration": "6h",
             "cost": 60, "rating": 4.8, "desc": "Home to Ferrari World, Yas Waterworld, and Formula 1."},
            {"name": "Corniche Walk", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "8km waterfront promenade with views of the skyline."},
        ],
        "restaurants": ["Zuma Abu Dhabi","Hakkasan","Roberto's","Catch Abu Dhabi"],
        "image": "abu_dhabi.jpg",
        "description": "UAE's capital — a gleaming city balancing Islamic heritage with ultra-modern ambition.",
        "difficulty": "easy", "safety": "very safe",
    },
    "doha": {
        "country": "Qatar", "continent": "Asia", "timezone": "AST",
        "currency": "QAR", "lang": "Arabic/English",
        "climate": "hot desert", "best_months": [11,12,1,2,3],
        "category": "International Cities",
        "travel_style": ['luxury', 'culture', 'food', 'shopping'],
        "group_types": ['couple', 'solo', 'family', 'friends'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 6},
        "tags": ["luxury","art","food","shopping"],
        "daily_budget": {"low": 80, "medium": 200, "high": 600},
        "attractions": [
            {"name": "Museum of Islamic Art", "type": "museum", "duration": "3h",
             "cost": 0, "rating": 4.9, "desc": "I.M. Pei's masterpiece housing 1,400 years of Islamic art."},
            {"name": "Souq Waqif", "type": "shopping", "duration": "3h",
             "cost": 0, "rating": 4.8, "desc": "Traditional market with spices, falcons, and Qatari cuisine."},
            {"name": "The Pearl-Qatar", "type": "landmark", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Artificial island with luxury marinas and designer boutiques."},
            {"name": "Katara Cultural Village", "type": "art", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Beautifully designed cultural hub with galleries and restaurants."},
        ],
        "restaurants": ["Nobu Doha","Spice Market","Al Mourjan","Parisa"],
        "image": "doha.jpg",
        "description": "Qatar's capital — where ancient Bedouin culture meets one of the world's richest cities.",
        "difficulty": "easy", "safety": "very safe",
    },
    "kuala lumpur": {
        "country": "Malaysia", "continent": "Asia", "timezone": "MYT",
        "currency": "MYR", "lang": "Malay/English",
        "climate": "tropical", "best_months": [5,6,7,8],
        "category": "International Cities",
        "travel_style": ['food', 'culture', 'shopping', 'family'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["food","shopping","nightlife","history","art"],
        "daily_budget": {"low": 30, "medium": 80, "high": 220},
        "attractions": [
            {"name": "Petronas Twin Towers", "type": "landmark", "duration": "2h",
             "cost": 25, "rating": 4.8, "desc": "Iconic 452m skyscrapers with a sky bridge at Level 41."},
            {"name": "Batu Caves", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Hindu temple complex inside dramatic limestone caves."},
            {"name": "Jalan Alor Food Street", "type": "food", "duration": "2h",
             "cost": 10, "rating": 4.8, "desc": "Famous street food strip with hawker stalls and neon lights."},
            {"name": "KLCC Park", "type": "nature", "duration": "1.5h",
             "cost": 0, "rating": 4.6, "desc": "Beautiful park with fountain shows at the base of the Towers."},
        ],
        "restaurants": ["Jalan Alor Hawkers","Bijan","Fuego","Entier"],
        "image": "kuala_lumpur.jpg",
        "description": "Southeast Asia's most dynamic capital — a melting pot of Malay, Chinese, and Indian culture.",
        "difficulty": "easy", "safety": "safe",
    },
    "singapore": {
        "country": "Singapore", "continent": "Asia", "timezone": "SGT",
        "currency": "SGD", "lang": "English/Mandarin/Malay/Tamil",
        "climate": "tropical", "best_months": [2,3,4,5,6],
        "category": "International Cities",
        "travel_style": ['food', 'culture', 'family', 'shopping'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["food","shopping","nightlife","art","luxury"],
        "daily_budget": {"low": 60, "medium": 160, "high": 450},
        "attractions": [
            {"name": "Gardens by the Bay", "type": "nature", "duration": "3h",
             "cost": 20, "rating": 4.9, "desc": "Futuristic botanical garden with 50m Supertree structures."},
            {"name": "Marina Bay Sands", "type": "landmark", "duration": "2h",
             "cost": 23, "rating": 4.8, "desc": "Iconic infinity pool atop three hotel towers."},
            {"name": "Chinatown & Little India", "type": "neighbourhood", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Vibrant cultural enclaves with temples, markets, and food."},
            {"name": "Sentosa Island", "type": "adventure", "duration": "6h",
             "cost": 30, "rating": 4.7, "desc": "Resort island with Universal Studios, beaches, and cable cars."},
        ],
        "restaurants": ["Hawker Centre (Maxwell)","Burnt Ends","Odette","National Kitchen"],
        "image": "singapore.jpg",
        "description": "The city-state that does everything right — safety, food, greenery, and world-class design.",
        "difficulty": "easy", "safety": "very safe",
    },
    "bangkok": {
        "country": "Thailand", "continent": "Asia", "timezone": "ICT",
        "currency": "THB", "lang": "Thai",
        "climate": "tropical", "best_months": [11,12,1,2,3],
        "category": "International Cities",
        "travel_style": ['food', 'culture', 'nightlife', 'adventure'],
        "group_types": ['solo', 'friends', 'couple', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["food","shopping","nightlife","religious","history"],
        "daily_budget": {"low": 25, "medium": 70, "high": 200},
        "attractions": [
            {"name": "Wat Phra Kaew (Grand Palace)", "type": "religious", "duration": "3h",
             "cost": 15, "rating": 4.9, "desc": "Thailand's most sacred temple with the Emerald Buddha."},
            {"name": "Chatuchak Weekend Market", "type": "shopping", "duration": "4h",
             "cost": 0, "rating": 4.7, "desc": "One of Asia's largest markets with 15,000 stalls."},
            {"name": "Floating Markets", "type": "food", "duration": "4h",
             "cost": 10, "rating": 4.7, "desc": "Traditional canal markets selling food from boats."},
            {"name": "Khao San Road", "type": "nightlife", "duration": "3h",
             "cost": 0, "rating": 4.4, "desc": "The backpacker heartbeat of Bangkok — street food and bars."},
        ],
        "restaurants": ["Jay Fai","Gaggan Anand","Bo.lan","Or Tor Kor Market"],
        "image": "bangkok.jpg",
        "description": "Southeast Asia's most exciting capital — temples, street food, and non-stop energy.",
        "difficulty": "easy", "safety": "safe",
    },
    "seoul": {
        "country": "South Korea", "continent": "Asia", "timezone": "KST",
        "currency": "KRW", "lang": "Korean",
        "climate": "humid continental", "best_months": [4,5,9,10],
        "category": "International Cities",
        "travel_style": ['food', 'culture', 'shopping', 'nightlife'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["food","shopping","history","art","nightlife"],
        "daily_budget": {"low": 40, "medium": 100, "high": 280},
        "attractions": [
            {"name": "Gyeongbokgung Palace", "type": "historic", "duration": "2h",
             "cost": 3, "rating": 4.8, "desc": "Magnificent Joseon Dynasty palace in the heart of Seoul."},
            {"name": "Bukchon Hanok Village", "type": "neighbourhood", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Preserved village of traditional Korean hanok houses."},
            {"name": "Hongdae District", "type": "nightlife", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Young, vibrant arts district with street performances and clubs."},
            {"name": "N Seoul Tower", "type": "landmark", "duration": "2h",
             "cost": 10, "rating": 4.7, "desc": "Iconic tower with panoramic city views and love locks."},
        ],
        "restaurants": ["Jungsik","Tongin Market Dosirak","Gwangjang Market Bindaetteok"],
        "image": "seoul.jpg",
        "description": "South Korea's dazzling capital — K-pop, history, street food, and ultra-fast internet.",
        "difficulty": "easy", "safety": "very safe",
    },
    "london": {
        "country": "United Kingdom", "continent": "Europe", "timezone": "GMT",
        "currency": "GBP", "lang": "English",
        "climate": "temperate oceanic", "best_months": [5,6,7,8,9],
        "category": "International Cities",
        "travel_style": ['culture', 'history', 'food', 'family'],
        "group_types": ['family', 'couple', 'solo', 'friends'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["history","art","food","shopping","nightlife"],
        "daily_budget": {"low": 80, "medium": 200, "high": 600},
        "attractions": [
            {"name": "British Museum", "type": "museum", "duration": "3h",
             "cost": 0, "rating": 4.9, "desc": "World-class museum with 8 million objects spanning human history."},
            {"name": "Tower of London", "type": "historic", "duration": "2.5h",
             "cost": 30, "rating": 4.7, "desc": "900-year-old fortress housing the Crown Jewels."},
            {"name": "Borough Market", "type": "food", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "London's finest food market with artisan vendors since 1014."},
            {"name": "Tate Modern", "type": "art", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "World-class modern art gallery in a converted power station."},
            {"name": "Hyde Park", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "350-acre royal park in central London."},
        ],
        "restaurants": ["St. John","Dishoom","The Ledbury","Bao Soho"],
        "image": "london.jpg",
        "description": "One of the world's great cities — history, culture, and cosmopolitan energy.",
        "difficulty": "easy", "safety": "moderate",
    },
    "barcelona": {
        "country": "Spain", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "Spanish/Catalan",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "International Cities",
        "travel_style": ['art', 'food', 'beach', 'nightlife'],
        "group_types": ['friends', 'couple', 'solo', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["art","food","history","nightlife","photography"],
        "daily_budget": {"low": 60, "medium": 150, "high": 380},
        "attractions": [
            {"name": "Sagrada Familia", "type": "landmark", "duration": "2h",
             "cost": 26, "rating": 4.9, "desc": "Gaudi's unfinished masterpiece — the most visited monument in Spain."},
            {"name": "Park Guell", "type": "art", "duration": "2h",
             "cost": 10, "rating": 4.7, "desc": "Colorful Gaudi mosaic park with panoramic city views."},
            {"name": "La Boqueria Market", "type": "food", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Barcelona's iconic covered market with fresh produce and tapas."},
            {"name": "Barceloneta Beach", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.6, "desc": "City beach with vibrant atmosphere and seafood restaurants."},
        ],
        "restaurants": ["El Celler de Can Roca","Tickets","Bar Calders","La Mar Salada"],
        "image": "barcelona.jpg",
        "description": "Gaudi's city — where art nouveau architecture meets Mediterranean beach culture.",
        "difficulty": "easy", "safety": "moderate",
    },
    "amsterdam": {
        "country": "Netherlands", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "Dutch/English",
        "climate": "temperate oceanic", "best_months": [4,5,6,7,8,9],
        "category": "International Cities",
        "travel_style": ['culture', 'art', 'cycling', 'nightlife'],
        "group_types": ['couple', 'friends', 'solo', 'family'],
        "trip_duration": {"min": 3, "ideal": 4, "max": 6},
        "tags": ["history","art","food","nightlife","photography"],
        "daily_budget": {"low": 70, "medium": 170, "high": 400},
        "attractions": [
            {"name": "Rijksmuseum", "type": "museum", "duration": "3h",
             "cost": 22, "rating": 4.9, "desc": "Dutch masterpieces including Rembrandt and Vermeer."},
            {"name": "Anne Frank House", "type": "historic", "duration": "2h",
             "cost": 16, "rating": 4.8, "desc": "The hiding place of Anne Frank during WWII."},
            {"name": "Canal Ring Bike Tour", "type": "adventure", "duration": "3h",
             "cost": 15, "rating": 4.8, "desc": "Explore Amsterdam's UNESCO-listed canal belt by bicycle."},
            {"name": "Van Gogh Museum", "type": "museum", "duration": "2h",
             "cost": 22, "rating": 4.9, "desc": "World's largest collection of Van Gogh's work."},
        ],
        "restaurants": ["De Kas","Rijsel","Moeders","Brouwerij 't IJ"],
        "image": "amsterdam.jpg",
        "description": "The Venice of the North — canals, cycling culture, and world-class art.",
        "difficulty": "easy", "safety": "safe",
    },
    "los angeles": {
        "country": "USA", "continent": "North America", "timezone": "PST",
        "currency": "USD", "lang": "English",
        "climate": "mediterranean", "best_months": [3,4,5,9,10,11],
        "category": "International Cities",
        "travel_style": ['entertainment', 'beach', 'culture', 'nightlife'],
        "group_types": ['friends', 'couple', 'solo', 'family'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nightlife","art","food","shopping","photography"],
        "daily_budget": {"low": 100, "medium": 250, "high": 700},
        "attractions": [
            {"name": "Hollywood Walk of Fame", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.4, "desc": "Iconic walk with 2,700+ stars of entertainment legends."},
            {"name": "Getty Center", "type": "museum", "duration": "3h",
             "cost": 0, "rating": 4.8, "desc": "World-class art museum with stunning architecture and gardens."},
            {"name": "Santa Monica Pier", "type": "landmark", "duration": "3h",
             "cost": 0, "rating": 4.6, "desc": "End of Route 66 — pier with Pacific Park amusement rides."},
            {"name": "Griffith Observatory", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "Iconic observatory with panoramic LA views."},
        ],
        "restaurants": ["Nobu Malibu","Bestia","Republique","Langer's Deli"],
        "image": "los_angeles.jpg",
        "description": "The City of Angels — Hollywood, beaches, and the entertainment capital of the world.",
        "difficulty": "easy", "safety": "moderate",
    },
    "toronto": {
        "country": "Canada", "continent": "North America", "timezone": "EST",
        "currency": "CAD", "lang": "English/French",
        "climate": "humid continental", "best_months": [5,6,7,8,9],
        "category": "International Cities",
        "travel_style": ['culture', 'food', 'family', 'nature'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["food","art","history","shopping","nightlife"],
        "daily_budget": {"low": 70, "medium": 170, "high": 420},
        "attractions": [
            {"name": "CN Tower", "type": "landmark", "duration": "2h",
             "cost": 43, "rating": 4.7, "desc": "Iconic 553m tower with glass floor and revolving restaurant."},
            {"name": "Royal Ontario Museum", "type": "museum", "duration": "3h",
             "cost": 23, "rating": 4.8, "desc": "Canada's largest museum with global natural history collections."},
            {"name": "Kensington Market", "type": "neighbourhood", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Bohemian neighbourhood with vintage shops and world food."},
            {"name": "Niagara Falls Day Trip", "type": "nature", "duration": "8h",
             "cost": 30, "rating": 4.9, "desc": "World-famous waterfalls just 90 minutes from the city."},
        ],
        "restaurants": ["Canoe","Alo","Edulis","Richmond Station"],
        "image": "toronto.jpg",
        "description": "Canada's most multicultural city — vibrant, safe, and endlessly diverse.",
        "difficulty": "easy", "safety": "safe",
    },
    "sydney": {
        "country": "Australia", "continent": "Oceania", "timezone": "AEST",
        "currency": "AUD", "lang": "English",
        "climate": "humid subtropical", "best_months": [9,10,11,12,3,4,5],
        "category": "International Cities",
        "travel_style": ['nature', 'food', 'culture', 'adventure'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nature","food","nightlife","photography","adventure"],
        "daily_budget": {"low": 80, "medium": 200, "high": 550},
        "attractions": [
            {"name": "Sydney Opera House", "type": "art", "duration": "2h",
             "cost": 43, "rating": 4.9, "desc": "UNESCO-listed architectural icon on Sydney Harbour."},
            {"name": "Bondi Beach", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.8, "desc": "Australia's most famous beach with great surf and cafes."},
            {"name": "Sydney Harbour Bridge Climb", "type": "adventure", "duration": "3h",
             "cost": 174, "rating": 4.9, "desc": "Guided climb over the iconic Harbour Bridge arch."},
            {"name": "Taronga Zoo", "type": "nature", "duration": "4h",
             "cost": 48, "rating": 4.7, "desc": "World-class zoo overlooking Sydney Harbour."},
        ],
        "restaurants": ["Quay","Tetsuya's","The Boathouse","Icebergs Dining Room"],
        "image": "sydney.jpg",
        "description": "Australia's harbour city — opera, beaches, and a laid-back quality of life.",
        "difficulty": "easy", "safety": "safe",
    },

    # ── Adventure Destinations ────────────────────────────────────────────────
    "patagonia": {
        "country": "Argentina/Chile", "continent": "South America", "timezone": "ART",
        "currency": "ARS", "lang": "Spanish",
        "climate": "sub-polar", "best_months": [11,12,1,2,3],
        "category": "Adventure Destinations",
        "travel_style": ['adventure', 'trekking', 'photography', 'nature'],
        "group_types": ['solo', 'friends', 'couple'],
        "trip_duration": {"min": 7, "ideal": 14, "max": 21},
        "tags": ["adventure","nature","photography"],
        "daily_budget": {"low": 50, "medium": 130, "high": 350},
        "attractions": [
            {"name": "Torres del Paine W Trek", "type": "adventure", "duration": "5 days",
             "cost": 30, "rating": 4.9, "desc": "World-renowned multi-day trek through stunning granite towers."},
            {"name": "Perito Moreno Glacier", "type": "nature", "duration": "4h",
             "cost": 20, "rating": 4.9, "desc": "One of the world's few advancing glaciers — spectacular ice walls."},
            {"name": "El Chalten Trekking", "type": "adventure", "duration": "8h",
             "cost": 0, "rating": 4.8, "desc": "Trek to Mt Fitz Roy base camp through raw Patagonian wilderness."},
        ],
        "restaurants": ["El Calafate Restaurants","Pura Vida Cafe","La Tablita"],
        "image": "patagonia.jpg",
        "description": "End of the world — vast glaciers, jagged peaks, and wild Patagonian wilderness.",
        "difficulty": "hard", "safety": "safe",
    },
    "interlaken": {
        "country": "Switzerland", "continent": "Europe", "timezone": "CET",
        "currency": "CHF", "lang": "German/French/Italian",
        "climate": "alpine", "best_months": [6,7,8,9],
        "category": "Adventure Destinations",
        "travel_style": ['adventure', 'luxury', 'nature', 'photography'],
        "group_types": ['friends', 'couple', 'solo', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["adventure","nature","photography","luxury"],
        "daily_budget": {"low": 100, "medium": 250, "high": 700},
        "attractions": [
            {"name": "Jungfraujoch Top of Europe", "type": "adventure", "duration": "6h",
             "cost": 200, "rating": 4.9, "desc": "Train to Europe's highest railway station at 3,454m."},
            {"name": "Paragliding over Interlaken", "type": "adventure", "duration": "2h",
             "cost": 150, "rating": 4.9, "desc": "Tandem paragliding with panoramic Alps and lake views."},
            {"name": "Lake Thun & Lake Brienz", "type": "nature", "duration": "4h",
             "cost": 20, "rating": 4.8, "desc": "Twin turquoise lakes flanking the Interlaken valley."},
        ],
        "restaurants": ["Beatus Wellness Resort","Goldener Anker","El Azteca"],
        "image": "interlaken.jpg",
        "description": "Switzerland's adventure capital — the Alps, two turquoise lakes, and paragliding heaven.",
        "difficulty": "easy", "safety": "very safe",
    },
    "queenstown": {
        "country": "New Zealand", "continent": "Oceania", "timezone": "NZST",
        "currency": "NZD", "lang": "English",
        "climate": "oceanic", "best_months": [12,1,2,3],
        "category": "Adventure Destinations",
        "travel_style": ['adventure', 'nature', 'food', 'photography'],
        "group_types": ['friends', 'solo', 'couple', 'family'],
        "trip_duration": {"min": 4, "ideal": 6, "max": 10},
        "tags": ["adventure","nature","photography","food"],
        "daily_budget": {"low": 70, "medium": 170, "high": 450},
        "attractions": [
            {"name": "Bungy Jumping at Kawarau Bridge", "type": "adventure", "duration": "2h",
             "cost": 165, "rating": 4.9, "desc": "Birthplace of commercial bungy jumping — 43m above the Kawarau River."},
            {"name": "Milford Sound Day Trip", "type": "nature", "duration": "10h",
             "cost": 80, "rating": 4.9, "desc": "Fiordland's crown jewel — dramatic fjords and waterfalls."},
            {"name": "Remarkables Ski Area", "type": "adventure", "duration": "8h",
             "cost": 90, "rating": 4.8, "desc": "World-class ski resort overlooking Lake Wakatipu."},
        ],
        "restaurants": ["Botswana Butchery","Rata","Fergburger","The Skyline Restaurant"],
        "image": "queenstown.jpg",
        "description": "New Zealand's adventure capital — bungee, skiing, and jaw-dropping scenery.",
        "difficulty": "easy", "safety": "very safe",
    },
    "banff": {
        "country": "Canada", "continent": "North America", "timezone": "MST",
        "currency": "CAD", "lang": "English",
        "climate": "alpine", "best_months": [6,7,8,9],
        "category": "Adventure Destinations",
        "travel_style": ['nature', 'photography', 'adventure', 'family'],
        "group_types": ['family', 'couple', 'friends', 'solo'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 80, "medium": 180, "high": 450},
        "attractions": [
            {"name": "Lake Louise", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.9, "desc": "Glacial turquoise lake with the Victoria Glacier as a backdrop."},
            {"name": "Banff Gondola", "type": "adventure", "duration": "3h",
             "cost": 50, "rating": 4.8, "desc": "Cable car to Sulphur Mountain summit with 360° Rockies views."},
            {"name": "Moraine Lake", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.9, "desc": "Valley of the Ten Peaks — one of the world's most photographed scenes."},
            {"name": "Icefields Parkway Drive", "type": "nature", "duration": "6h",
             "cost": 0, "rating": 4.9, "desc": "230km scenic highway through the heart of the Canadian Rockies."},
        ],
        "restaurants": ["The Bison Restaurant","Eden Restaurant","Three Ravens"],
        "image": "banff.jpg",
        "description": "Canada's most stunning national park — turquoise lakes, glaciers, and wildlife.",
        "difficulty": "easy", "safety": "very safe",
    },

    # ── Luxury Destinations ───────────────────────────────────────────────────
    "monaco": {
        "country": "Monaco", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "French/Monegasque",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "Luxury Destinations",
        "travel_style": ['luxury', 'nightlife', 'food', 'culture'],
        "group_types": ['couple', 'solo', 'friends'],
        "trip_duration": {"min": 2, "ideal": 3, "max": 5},
        "tags": ["luxury","nightlife","food","shopping"],
        "daily_budget": {"low": 150, "medium": 400, "high": 2000},
        "attractions": [
            {"name": "Monte-Carlo Casino", "type": "landmark", "duration": "3h",
             "cost": 17, "rating": 4.7, "desc": "World's most glamorous casino, immortalised by James Bond."},
            {"name": "Oceanographic Museum", "type": "museum", "duration": "2h",
             "cost": 20, "rating": 4.8, "desc": "Founded by Jacques Cousteau — world-class marine exhibits."},
            {"name": "Prince's Palace of Monaco", "type": "historic", "duration": "1.5h",
             "cost": 10, "rating": 4.6, "desc": "Official residence of the Grimaldi family since 1297."},
            {"name": "Formula 1 Monaco Grand Prix Circuit", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "Walk the legendary street circuit of the world's most glamorous race."},
        ],
        "restaurants": ["Louis XV-Alain Ducasse","Joel Robuchon Monaco","Cipriani","Sass Cafe"],
        "image": "monaco.jpg",
        "description": "The world's most glamorous microstate — casinos, yachts, and Formula 1.",
        "difficulty": "easy", "safety": "very safe",
    },
    "santorini": {
        "country": "Greece", "continent": "Europe", "timezone": "EET",
        "currency": "EUR", "lang": "Greek",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "Luxury Destinations",
        "travel_style": ['luxury', 'romance', 'photography', 'nature'],
        "group_types": ['couple', 'solo', 'family', 'friends'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["luxury","photography","food","nature"],
        "daily_budget": {"low": 80, "medium": 200, "high": 700},
        "attractions": [
            {"name": "Oia Sunset", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.9, "desc": "World's most famous sunset over the volcanic caldera."},
            {"name": "Akrotiri Archaeological Site", "type": "historic", "duration": "2h",
             "cost": 12, "rating": 4.7, "desc": "Minoan Bronze Age city preserved by volcanic ash."},
            {"name": "Caldera Boat Tour", "type": "adventure", "duration": "4h",
             "cost": 30, "rating": 4.8, "desc": "Sail around the volcanic caldera and hot springs."},
            {"name": "Black Sand Beach (Perissa)", "type": "nature", "duration": "3h",
             "cost": 0, "rating": 4.6, "desc": "Unique volcanic black sand beach with crystal-clear water."},
        ],
        "restaurants": ["Selene","Metaxy Mas","Ambrosia","Lucky's Souvlakis"],
        "image": "santorini.jpg",
        "description": "Greece's most iconic island — whitewashed clifftop villages above a volcanic caldera.",
        "difficulty": "easy", "safety": "very safe",
    },
    "swiss alps": {
        "country": "Switzerland", "continent": "Europe", "timezone": "CET",
        "currency": "CHF", "lang": "German/French/Italian",
        "climate": "alpine", "best_months": [12,1,2,3,6,7,8],
        "category": "Luxury Destinations",
        "travel_style": ['luxury', 'adventure', 'nature', 'photography'],
        "group_types": ['couple', 'family', 'friends', 'solo'],
        "trip_duration": {"min": 5, "ideal": 7, "max": 14},
        "tags": ["luxury","adventure","nature","photography"],
        "daily_budget": {"low": 120, "medium": 280, "high": 800},
        "attractions": [
            {"name": "Matterhorn Viewing (Zermatt)", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.9, "desc": "Iconic 4,478m pyramidal peak — the symbol of the Alps."},
            {"name": "Glacier Express Train", "type": "adventure", "duration": "8h",
             "cost": 120, "rating": 4.9, "desc": "The world's slowest express train through Alpine scenery."},
            {"name": "Verbier Ski Slopes", "type": "adventure", "duration": "8h",
             "cost": 80, "rating": 4.8, "desc": "World-class skiing with 412km of piste and off-piste terrain."},
        ],
        "restaurants": ["The Restaurant Zermatt","Chez Vrony","Monte Rose Hotel Dining"],
        "image": "swiss_alps.jpg",
        "description": "The pinnacle of Alpine luxury — skiing, hiking, and storybook mountain villages.",
        "difficulty": "moderate", "safety": "very safe",
    },
    "bora bora": {
        "country": "French Polynesia", "continent": "Oceania", "timezone": "TAHT",
        "currency": "XPF", "lang": "French/Tahitian",
        "climate": "tropical", "best_months": [5,6,7,8,9,10],
        "category": "Luxury Destinations",
        "travel_style": ['luxury', 'romance', 'diving', 'nature'],
        "group_types": ['couple', 'solo', 'family'],
        "trip_duration": {"min": 5, "ideal": 7, "max": 10},
        "tags": ["luxury","nature","adventure","photography"],
        "daily_budget": {"low": 200, "medium": 600, "high": 2000},
        "attractions": [
            {"name": "Overwater Bungalow Experience", "type": "luxury", "duration": "all day",
             "cost": 0, "rating": 5.0, "desc": "Wake up directly over the world's most transparent lagoon."},
            {"name": "Mount Otemanu Hike", "type": "adventure", "duration": "5h",
             "cost": 50, "rating": 4.8, "desc": "Trek to the extinct volcano summit for 360° island views."},
            {"name": "Shark & Ray Snorkelling", "type": "adventure", "duration": "3h",
             "cost": 80, "rating": 4.9, "desc": "Swim with harmless lemon sharks and stingrays in the lagoon."},
        ],
        "restaurants": ["Bloody Mary's","La Villa Mahana","St James Bora Bora"],
        "image": "bora_bora.jpg",
        "description": "The jewel of French Polynesia — the ultimate luxury island with a turquoise lagoon.",
        "difficulty": "easy", "safety": "very safe",
    },

    # ── Additional Global Destinations ────────────────────────────────────────
    "kyoto": {
        "country": "Japan", "continent": "Asia", "timezone": "JST",
        "currency": "JPY", "lang": "Japanese",
        "climate": "humid subtropical", "best_months": [3,4,10,11],
        "category": "Historical & Cultural",
        "travel_style": ['culture', 'history', 'photography', 'food'],
        "group_types": ['solo', 'couple', 'family', 'friends'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["history","religious","photography","food","art"],
        "daily_budget": {"low": 50, "medium": 120, "high": 320},
        "attractions": [
            {"name": "Fushimi Inari Shrine", "type": "religious", "duration": "3h",
             "cost": 0, "rating": 4.9, "desc": "Thousands of vermillion torii gates winding up a forested mountain."},
            {"name": "Arashiyama Bamboo Grove", "type": "nature", "duration": "2h",
             "cost": 0, "rating": 4.8, "desc": "Otherworldly pathway through towering bamboo stalks."},
            {"name": "Kinkaku-ji (Golden Pavilion)", "type": "historic", "duration": "1.5h",
             "cost": 5, "rating": 4.9, "desc": "Iconic gold-leafed Zen temple reflected in a mirror pond."},
            {"name": "Gion Geisha District", "type": "neighbourhood", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Historic district where geiko and maiko walk cobblestone streets."},
        ],
        "restaurants": ["Kikunoi","Nishiki Market Stalls","Izuju Sushi","Tofu Kaiseki Okutan"],
        "image": "kyoto.jpg",
        "description": "Japan's ancient capital — 17 UNESCO sites, 1,600 temples, and living cultural tradition.",
        "difficulty": "easy", "safety": "very safe",
    },
    "prague": {
        "country": "Czech Republic", "continent": "Europe", "timezone": "CET",
        "currency": "CZK", "lang": "Czech",
        "climate": "oceanic", "best_months": [4,5,6,9,10],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'culture', 'nightlife', 'photography'],
        "group_types": ['couple', 'friends', 'solo', 'family'],
        "trip_duration": {"min": 3, "ideal": 4, "max": 6},
        "tags": ["history","art","food","nightlife","photography"],
        "daily_budget": {"low": 40, "medium": 100, "high": 260},
        "attractions": [
            {"name": "Prague Castle", "type": "historic", "duration": "3h",
             "cost": 15, "rating": 4.8, "desc": "World's largest ancient castle complex overlooking the city."},
            {"name": "Charles Bridge", "type": "landmark", "duration": "1.5h",
             "cost": 0, "rating": 4.8, "desc": "Medieval stone bridge lined with Baroque sculptures."},
            {"name": "Old Town Square & Astronomical Clock", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "Gothic and Baroque architecture surrounding a 600-year-old clock."},
        ],
        "restaurants": ["La Degustation","Lokál Dlouha","Cafe Savoy","U Fleků Brewery"],
        "image": "prague.jpg",
        "description": "The City of a Hundred Spires — Europe's most beautiful medieval city centre.",
        "difficulty": "easy", "safety": "safe",
    },
    "cairo": {
        "country": "Egypt", "continent": "Africa", "timezone": "EET",
        "currency": "EGP", "lang": "Arabic",
        "climate": "hot desert", "best_months": [10,11,12,1,2,3,4],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'culture', 'photography', 'adventure'],
        "group_types": ['solo', 'couple', 'family', 'friends'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 8},
        "tags": ["history","religious","photography","food"],
        "daily_budget": {"low": 25, "medium": 70, "high": 200},
        "attractions": [
            {"name": "Pyramids of Giza", "type": "landmark", "duration": "4h",
             "cost": 15, "rating": 4.9, "desc": "The last remaining Wonder of the Ancient World."},
            {"name": "Egyptian Museum", "type": "museum", "duration": "3h",
             "cost": 10, "rating": 4.8, "desc": "Tutankhamun's treasures and 120,000 ancient artefacts."},
            {"name": "Khan el-Khalili Bazaar", "type": "shopping", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Cairo's historic souk, operating since the 14th century."},
            {"name": "Egyptian National Museum GEM", "type": "museum", "duration": "3h",
             "cost": 20, "rating": 4.9, "desc": "World's largest archaeological museum, opened in 2023."},
        ],
        "restaurants": ["Koshary El Tahrir","Naguib Mahfouz Cafe","Sequoia Restaurant","The Grill"],
        "image": "cairo.jpg",
        "description": "Egypt's capital — 5,000 years of civilisation with the Pyramids on the doorstep.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "cape town": {
        "country": "South Africa", "continent": "Africa", "timezone": "SAST",
        "currency": "ZAR", "lang": "English/Afrikaans/Xhosa",
        "climate": "mediterranean", "best_months": [10,11,12,1,2,3,4],
        "category": "Adventure Destinations",
        "travel_style": ['nature', 'adventure', 'food', 'photography'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 5, "ideal": 7, "max": 10},
        "tags": ["nature","adventure","food","photography"],
        "daily_budget": {"low": 35, "medium": 90, "high": 280},
        "attractions": [
            {"name": "Table Mountain Cable Car", "type": "nature", "duration": "3h",
             "cost": 30, "rating": 4.9, "desc": "Rotating cable car to the flat-topped mountain summit."},
            {"name": "Cape of Good Hope", "type": "nature", "duration": "4h",
             "cost": 15, "rating": 4.8, "desc": "Dramatic cliffs at Africa's south-western tip."},
            {"name": "Boulders Beach Penguins", "type": "nature", "duration": "2h",
             "cost": 10, "rating": 4.8, "desc": "African penguin colony on a sheltered beach."},
            {"name": "V&A Waterfront", "type": "shopping", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Vibrant harbour precinct with restaurants and craft beer."},
        ],
        "restaurants": ["The Test Kitchen","La Colombe","Tashas","Boulders Beach Cafe"],
        "image": "cape_town.jpg",
        "description": "The Mother City — Table Mountain, penguins, wine country, and incredible food.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "marrakech": {
        "country": "Morocco", "continent": "Africa", "timezone": "WET",
        "currency": "MAD", "lang": "Arabic/French/Berber",
        "climate": "hot semi-arid", "best_months": [3,4,5,10,11],
        "category": "Historical & Cultural",
        "travel_style": ['culture', 'food', 'shopping', 'photography'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["history","food","shopping","photography","art"],
        "daily_budget": {"low": 30, "medium": 80, "high": 250},
        "attractions": [
            {"name": "Djemaa el-Fna Square", "type": "landmark", "duration": "4h",
             "cost": 0, "rating": 4.8, "desc": "UNESCO-listed square with storytellers, musicians, and food stalls."},
            {"name": "Majorelle Garden", "type": "nature", "duration": "2h",
             "cost": 12, "rating": 4.8, "desc": "Cobalt-blue Yves Saint Laurent botanical garden."},
            {"name": "The Medina Souk", "type": "shopping", "duration": "3h",
             "cost": 0, "rating": 4.7, "desc": "Labyrinthine market overflowing with spices, leather, and lanterns."},
            {"name": "Bahia Palace", "type": "historic", "duration": "1.5h",
             "cost": 7, "rating": 4.7, "desc": "Ornate 19th-century palace with intricate Moroccan craftwork."},
        ],
        "restaurants": ["Nomad","Le Jardin","Cafe des Epices","Naranj Restaurant"],
        "image": "marrakech.jpg",
        "description": "Morocco's rose-red city — a sensory overload of colour, spices, and ancient medina lanes.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "vienna": {
        "country": "Austria", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "German",
        "climate": "oceanic", "best_months": [4,5,6,9,10],
        "category": "International Cities",
        "travel_style": ['culture', 'music', 'art', 'food'],
        "group_types": ['couple', 'solo', 'family', 'friends'],
        "trip_duration": {"min": 3, "ideal": 4, "max": 6},
        "tags": ["history","art","food","music"],
        "daily_budget": {"low": 60, "medium": 150, "high": 380},
        "attractions": [
            {"name": "Schoenbrunn Palace", "type": "historic", "duration": "3h",
             "cost": 22, "rating": 4.8, "desc": "Habsburg imperial palace with 1,441 rooms and formal gardens."},
            {"name": "Kunsthistorisches Museum", "type": "museum", "duration": "3h",
             "cost": 21, "rating": 4.8, "desc": "One of Europe's finest art museums with Habsburg imperial collection."},
            {"name": "Vienna State Opera", "type": "art", "duration": "3h",
             "cost": 10, "rating": 4.8, "desc": "World's leading opera house with 300+ performances per year."},
            {"name": "Belvedere Palace & Gardens", "type": "art", "duration": "2.5h",
             "cost": 22, "rating": 4.8, "desc": "Baroque palace housing Klimt's The Kiss."},
        ],
        "restaurants": ["Steirereck","Figlmueller Bäckerstrasse","Cafe Central","Meixner's"],
        "image": "vienna.jpg",
        "description": "The City of Music — Mozart, Beethoven, Freud, and some of Europe's finest coffee houses.",
        "difficulty": "easy", "safety": "very safe",
    },
    "lisbon": {
        "country": "Portugal", "continent": "Europe", "timezone": "WET",
        "currency": "EUR", "lang": "Portuguese",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "International Cities",
        "travel_style": ['culture', 'food', 'nightlife', 'photography'],
        "group_types": ['solo', 'couple', 'friends', 'family'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["history","food","nightlife","art","photography"],
        "daily_budget": {"low": 45, "medium": 110, "high": 280},
        "attractions": [
            {"name": "Belem Tower", "type": "historic", "duration": "1.5h",
             "cost": 8, "rating": 4.7, "desc": "16th-century fortress and symbol of Portugal's Age of Discovery."},
            {"name": "Alfama Fado District", "type": "neighbourhood", "duration": "3h",
             "cost": 0, "rating": 4.8, "desc": "Lisbon's oldest neighbourhood where Fado music was born."},
            {"name": "Pasteis de Belem", "type": "food", "duration": "1h",
             "cost": 5, "rating": 4.9, "desc": "Original home of the pastel de nata — Portugal's iconic custard tart."},
            {"name": "Sintra Day Trip", "type": "adventure", "duration": "8h",
             "cost": 15, "rating": 4.9, "desc": "UNESCO palaces and fairytale castles 40 minutes from Lisbon."},
        ],
        "restaurants": ["Belcanto","Taberna da Rua das Flores","Solar dos Presuntos","Zé da Mouraria"],
        "image": "lisbon.jpg",
        "description": "Europe's sunniest capital — seven hills, Fado music, pastel de nata, and Atlantic charm.",
        "difficulty": "easy", "safety": "very safe",
    },
    "florence": {
        "country": "Italy", "continent": "Europe", "timezone": "CET",
        "currency": "EUR", "lang": "Italian",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "Historical & Cultural",
        "travel_style": ['art', 'history', 'food', 'photography'],
        "group_types": ['couple', 'solo', 'family', 'friends'],
        "trip_duration": {"min": 2, "ideal": 4, "max": 6},
        "tags": ["art","history","food","photography"],
        "daily_budget": {"low": 60, "medium": 150, "high": 380},
        "attractions": [
            {"name": "Uffizi Gallery", "type": "museum", "duration": "3h",
             "cost": 20, "rating": 4.9, "desc": "Home to Botticelli's Birth of Venus and hundreds of Renaissance masterpieces."},
            {"name": "Duomo di Firenze", "type": "landmark", "duration": "2h",
             "cost": 20, "rating": 4.9, "desc": "Brunelleschi's dome — the greatest feat of Renaissance engineering."},
            {"name": "Ponte Vecchio", "type": "landmark", "duration": "1h",
             "cost": 0, "rating": 4.7, "desc": "Medieval bridge lined with jewellery shops over the Arno."},
            {"name": "Accademia Gallery (David)", "type": "museum", "duration": "2h",
             "cost": 20, "rating": 4.9, "desc": "Michelangelo's David — the world's most famous sculpture."},
        ],
        "restaurants": ["Buca Mario","Trattoria Mario","Golden View Open Bar","Osteria dell'Enoteca"],
        "image": "florence.jpg",
        "description": "Birthplace of the Renaissance — the world's greatest concentration of art and architecture.",
        "difficulty": "easy", "safety": "safe",
    },
    "athens": {
        "country": "Greece", "continent": "Europe", "timezone": "EET",
        "currency": "EUR", "lang": "Greek",
        "climate": "mediterranean", "best_months": [4,5,6,9,10],
        "category": "Historical & Cultural",
        "travel_style": ['history', 'culture', 'food', 'photography'],
        "group_types": ['couple', 'solo', 'family', 'friends'],
        "trip_duration": {"min": 3, "ideal": 5, "max": 7},
        "tags": ["history","food","photography","art"],
        "daily_budget": {"low": 45, "medium": 110, "high": 280},
        "attractions": [
            {"name": "Acropolis & Parthenon", "type": "historic", "duration": "3h",
             "cost": 20, "rating": 4.9, "desc": "The crown of Western civilisation — 2,500-year-old temple to Athena."},
            {"name": "Acropolis Museum", "type": "museum", "duration": "2h",
             "cost": 10, "rating": 4.8, "desc": "World-class museum displaying the Acropolis' original sculptures."},
            {"name": "Monastiraki Flea Market", "type": "shopping", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "Chaotic and charming market near the ancient Agora."},
            {"name": "Cape Sounion Sunset", "type": "nature", "duration": "4h",
             "cost": 10, "rating": 4.8, "desc": "Temple of Poseidon on a cliff with legendary Mediterranean sunsets."},
        ],
        "restaurants": ["Spondi","Kuzina","Nolan","To Kafeneio"],
        "image": "athens.jpg",
        "description": "The cradle of democracy — where Western civilisation was born 2,500 years ago.",
        "difficulty": "easy", "safety": "safe",
    },
    "rio de janeiro": {
        "country": "Brazil", "continent": "South America", "timezone": "BRT",
        "currency": "BRL", "lang": "Portuguese",
        "climate": "tropical", "best_months": [5,6,7,8,9],
        "category": "International Cities",
        "travel_style": ['nature', 'nightlife', 'culture', 'adventure'],
        "group_types": ['friends', 'couple', 'solo', 'family'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nature","nightlife","food","photography","adventure"],
        "daily_budget": {"low": 40, "medium": 100, "high": 300},
        "attractions": [
            {"name": "Christ the Redeemer", "type": "landmark", "duration": "3h",
             "cost": 23, "rating": 4.9, "desc": "Iconic 38m Art Deco statue with panoramic city views."},
            {"name": "Copacabana & Ipanema Beaches", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.8, "desc": "Rio's legendary urban beaches with volleyball and caipirinhas."},
            {"name": "Sugarloaf Cable Car", "type": "adventure", "duration": "3h",
             "cost": 30, "rating": 4.8, "desc": "Twin cable car rides to the summit of Pao de Acucar."},
            {"name": "Lapa Arches (Arcos da Lapa)", "type": "landmark", "duration": "2h",
             "cost": 0, "rating": 4.6, "desc": "18th-century aqueduct at the heart of Rio's nightlife district."},
        ],
        "restaurants": ["Olympe","Roberta Sudbrack","Churrascaria Palace","Bar do Mineiro"],
        "image": "rio_de_janeiro.jpg",
        "description": "A Cidade Maravilhosa — one of the world's most beautiful cities between mountains and sea.",
        "difficulty": "moderate", "safety": "moderate",
    },
    "new zealand south island": {
        "country": "New Zealand", "continent": "Oceania", "timezone": "NZST",
        "currency": "NZD", "lang": "English/Maori",
        "climate": "oceanic", "best_months": [11,12,1,2,3],
        "category": "Adventure Destinations",
        "travel_style": ['adventure', 'nature', 'photography', 'trekking'],
        "group_types": ['solo', 'friends', 'couple', 'family'],
        "trip_duration": {"min": 7, "ideal": 14, "max": 21},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 60, "medium": 150, "high": 400},
        "attractions": [
            {"name": "Fiordland National Park", "type": "nature", "duration": "2 days",
             "cost": 30, "rating": 4.9, "desc": "Dramatic fjords, waterfalls, and near-untouched wilderness."},
            {"name": "Abel Tasman Coastal Track", "type": "adventure", "duration": "3 days",
             "cost": 30, "rating": 4.9, "desc": "Golden beaches and turquoise water on a multi-day kayak trail."},
            {"name": "Mount Cook National Park", "type": "nature", "duration": "8h",
             "cost": 0, "rating": 4.9, "desc": "New Zealand's highest peak in a UNESCO World Heritage area."},
        ],
        "restaurants": ["Rata Queenstown","The Boat Shed Nelson","Hai Christchurch"],
        "image": "nz_south.jpg",
        "description": "Middle-earth come to life — glaciers, fiords, and the world's finest trekking.",
        "difficulty": "moderate", "safety": "very safe",
    },
    "iceland": {
        "country": "Iceland", "continent": "Europe", "timezone": "GMT",
        "currency": "ISK", "lang": "Icelandic/English",
        "climate": "sub-polar oceanic", "best_months": [6,7,8],
        "category": "Adventure Destinations",
        "travel_style": ['nature', 'adventure', 'photography', 'northern lights'],
        "group_types": ['couple', 'solo', 'friends', 'family'],
        "trip_duration": {"min": 5, "ideal": 8, "max": 12},
        "tags": ["nature","adventure","photography"],
        "daily_budget": {"low": 80, "medium": 200, "high": 500},
        "attractions": [
            {"name": "Northern Lights", "type": "nature", "duration": "4h",
             "cost": 80, "rating": 4.9, "desc": "Aurora borealis viewing in some of the world's darkest skies."},
            {"name": "Golden Circle", "type": "adventure", "duration": "10h",
             "cost": 60, "rating": 4.9, "desc": "Geysir, Gullfoss waterfall, and Thingvellir National Park."},
            {"name": "Blue Lagoon", "type": "adventure", "duration": "4h",
             "cost": 60, "rating": 4.7, "desc": "Geothermal spa in a black lava field on the Reykjanes Peninsula."},
            {"name": "Glacier Hiking (Solheimajokull)", "type": "adventure", "duration": "4h",
             "cost": 80, "rating": 4.9, "desc": "Guided hike on an active glacier with crampons and ice axes."},
        ],
        "restaurants": ["Dill","Nostra","Grillmarkadurinn","Cafe Loki"],
        "image": "iceland.jpg",
        "description": "Land of Fire and Ice — volcanoes, glaciers, geysers, and the Northern Lights.",
        "difficulty": "moderate", "safety": "very safe",
    },
    "phuket": {
        "country": "Thailand", "continent": "Asia", "timezone": "ICT",
        "currency": "THB", "lang": "Thai",
        "climate": "tropical", "best_months": [11,12,1,2,3,4],
        "category": "Beaches & Coastal",
        "travel_style": ['beach', 'nightlife', 'adventure', 'food'],
        "group_types": ['friends', 'couple', 'solo', 'family'],
        "trip_duration": {"min": 4, "ideal": 7, "max": 10},
        "tags": ["nature","nightlife","food","adventure"],
        "daily_budget": {"low": 30, "medium": 80, "high": 250},
        "attractions": [
            {"name": "Phi Phi Islands Boat Tour", "type": "adventure", "duration": "8h",
             "cost": 40, "rating": 4.9, "desc": "Turquoise bays and dramatic limestone cliffs made famous by The Beach."},
            {"name": "Patong Beach", "type": "nature", "duration": "4h",
             "cost": 0, "rating": 4.5, "desc": "Phuket's most famous beach with watersports and nightlife."},
            {"name": "Big Buddha Phuket", "type": "religious", "duration": "2h",
             "cost": 0, "rating": 4.7, "desc": "45m white marble Buddha with sweeping island views."},
            {"name": "Bangla Road Night Market", "type": "nightlife", "duration": "4h",
             "cost": 0, "rating": 4.4, "desc": "Phuket's legendary nightlife street with bars, shows, and street food."},
        ],
        "restaurants": ["Mom Tri's Boathouse","Acqua Restaurant","Suay Restaurant","Roti Chaofa"],
        "image": "phuket.jpg",
        "description": "Thailand's Pearl of the Andaman — tropical beaches, islands, and vibrant nightlife.",
        "difficulty": "easy", "safety": "safe",
    },
}

WEATHER_CONDITIONS = {
    "clear": {"icon": "☀️", "label": "Clear & Sunny", "clothing": "Light clothing, sunscreen, sunglasses"},
    "partly_cloudy": {"icon": "⛅", "label": "Partly Cloudy", "clothing": "Light layers, comfortable footwear"},
    "overcast": {"icon": "☁️", "label": "Overcast", "clothing": "Light jacket recommended"},
    "light_rain": {"icon": "🌦", "label": "Light Rain", "clothing": "Compact umbrella, light waterproof jacket"},
    "heavy_rain": {"icon": "🌧", "label": "Heavy Rain", "clothing": "Full waterproof gear, waterproof shoes"},
    "thunderstorm": {"icon": "⛈", "label": "Thunderstorm", "clothing": "Stay indoors, full waterproof gear if venturing out"},
    "snow": {"icon": "🌨", "label": "Snowy", "clothing": "Warm layers, waterproof boots, gloves, hat"},
    "windy": {"icon": "💨", "label": "Windy", "clothing": "Windproof jacket, secure loose items"},
    "hot": {"icon": "🌡", "label": "Very Hot", "clothing": "Breathable light fabrics, hat, extra water"},
    "foggy": {"icon": "🌫", "label": "Foggy", "clothing": "Warm layers, reflective accessories"},
}


class TripEngine:
    def __init__(self, destination, days, budget, travel_type, interests,
                 accommodation, transport, start_date, travelers=1,
                 traveler_name="", traveler_age=None, start_location=""):
        self.destination     = destination.strip()
        self.dest_key        = destination.lower().strip()
        self.days            = days
        self.budget          = budget
        self.travel_type     = travel_type
        self.interests       = interests if isinstance(interests, list) else []
        self.accommodation   = accommodation
        self.transport       = transport
        self.start_date      = start_date
        self.travelers       = travelers
        self.traveler_name   = traveler_name or ""
        self.traveler_age    = int(traveler_age) if traveler_age else None
        self.start_location  = start_location or ""
        self._seed           = int(hashlib.md5(f"{destination}{start_date}".encode()).hexdigest(), 16) % (10**9)
        self._rng            = random.Random(self._seed)
        self._dest_data      = self._find_dest_data()

    # ── Internal helpers ──────────────────────────────────────────────────────
    def _find_dest_data(self):
        """Fuzzy-match destination name to knowledge base."""
        key = self.dest_key
        if key in DESTINATIONS:
            return DESTINATIONS[key]
        for k, v in DESTINATIONS.items():
            if k in key or key in k:
                return v
        # Return a generic fallback
        return self._generic_dest()

    def _generic_dest(self):
        return {
            "country": "Unknown", "continent": "Unknown", "timezone": "UTC",
            "currency": "USD", "lang": "English", "climate": "temperate",
            "best_months": list(range(1, 13)),
            "tags": ["history", "food", "photography"],
            "daily_budget": {"low": 60, "medium": 150, "high": 400},
            "attractions": [
                {"name": f"City Centre of {self.destination}", "type": "landmark",
                 "duration": "2h", "cost": 0, "rating": 4.2,
                 "desc": "Explore the heart of the city on foot."},
                {"name": "Local Market", "type": "food", "duration": "1.5h",
                 "cost": 15, "rating": 4.4,
                 "desc": "Sample authentic local street food and crafts."},
                {"name": "National Museum", "type": "museum", "duration": "2h",
                 "cost": 10, "rating": 4.3,
                 "desc": "Discover the history and culture of the region."},
            ],
            "restaurants": ["Local Restaurant A", "Street Food Alley", "Rooftop Café"],
            "image": "default.jpg",
            "description": f"Explore the hidden gems and rich culture of {self.destination}.",
            "difficulty": "moderate", "safety": "moderate",
        }

    def _budget_level(self):
        per_person_daily = self.budget / max(self.days, 1) / max(self.travelers, 1)
        if per_person_daily < 80:
            return "low"
        if per_person_daily < 250:
            return "medium"
        return "high"

    def _accom_cost_per_night(self):
        accom_map = {
            "hostel": {"low": 15, "medium": 30, "high": 60},
            "apartment": {"low": 40, "medium": 90, "high": 200},
            "hotel": {"low": 60, "medium": 140, "high": 350},
            "resort": {"low": 100, "medium": 250, "high": 700},
        }
        costs = accom_map.get(self.accommodation, accom_map["hotel"])
        return costs[self._budget_level()]

    def _transport_cost_per_day(self):
        transport_map = {
            "walking": 0, "public": 10, "taxi": 30,
            "rental car": 55, "car": 45,
        }
        return transport_map.get(self.transport, 15)

    # ── Budget breakdown ──────────────────────────────────────────────────────
    def _calculate_budget(self):
        nights    = self.days
        travelers = self.travelers
        accom     = self._accom_cost_per_night() * nights * travelers
        transport = self._transport_cost_per_day() * self.days * travelers
        # Food: 3 meals per person per day
        food_daily = {"low": 25, "medium": 55, "high": 130}[self._budget_level()]
        food = food_daily * self.days * travelers
        # Attractions
        att_cost = sum(a.get("cost", 0) for a in self._dest_data.get("attractions", [])[:5])
        attractions = att_cost * travelers
        # Misc (10%)
        misc = (accom + transport + food + attractions) * 0.10
        emergency = self.budget * 0.08

        total_estimated = accom + transport + food + attractions + misc + emergency
        remaining       = self.budget - total_estimated

        return {
            "total_budget": round(self.budget, 2),
            "estimated_total": round(total_estimated, 2),
            "remaining": round(remaining, 2),
            "utilization_pct": round(min(total_estimated / max(self.budget, 1) * 100, 100), 1),
            "breakdown": {
                "accommodation": round(accom, 2),
                "transportation": round(transport, 2),
                "food": round(food, 2),
                "attractions": round(attractions, 2),
                "miscellaneous": round(misc, 2),
                "emergency_fund": round(emergency, 2),
            }
        }

    # ── Itinerary ─────────────────────────────────────────────────────────────
    def _generate_itinerary(self):
        attractions = list(self._dest_data.get("attractions", []))
        restaurants = list(self._dest_data.get("restaurants", []))

        # ── Interest-based attraction prioritisation ───────────────────────
        # Map user interests to attraction types
        interest_type_map = {
            "history":    ["historic", "museum", "landmark"],
            "food":       ["food"],
            "photography":["landmark", "nature", "neighbourhood"],
            "shopping":   ["shopping"],
            "nature":     ["nature", "adventure"],
            "adventure":  ["adventure", "nature"],
            "religious":  ["religious", "historic"],
            "nightlife":  ["neighbourhood", "shopping"],
            "art":        ["art", "museum"],
            "luxury":     ["landmark", "nature"],
        }
        preferred_types = set()
        for interest in self.interests:
            preferred_types.update(interest_type_map.get(interest, []))

        if preferred_types:
            # Sort: preferred types first, then rest
            def att_priority(a):
                return 0 if a.get("type") in preferred_types else 1
            attractions.sort(key=att_priority)
        else:
            self._rng.shuffle(attractions)

        # ── Age-aware difficulty filtering ────────────────────────────────
        traveler_age = getattr(self, 'traveler_age', None)
        if traveler_age:
            if traveler_age >= 65:
                # Deprioritise strenuous adventure activities for seniors
                heavy = [a for a in attractions if a.get("type") == "adventure"
                         and a.get("duration", "2h").replace("h","").split(".")[0].isdigit()
                         and float(a.get("duration","2h").replace("h","")) >= 4]
                light = [a for a in attractions if a not in heavy]
                attractions = light + heavy
            elif traveler_age <= 12:
                # Deprioritise museums for children, prioritise nature/adventure
                child_first = [a for a in attractions if a.get("type") in ("nature","adventure","landmark")]
                others      = [a for a in attractions if a not in child_first]
                attractions  = child_first + others

        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
        except Exception:
            start = datetime.today()

        itinerary = []
        att_idx = 0
        for day_num in range(1, self.days + 1):
            date = start + timedelta(days=day_num - 1)
            day_date = date.strftime("%A, %B %d %Y")

            # Pick 2–3 attractions per day
            day_atts = []
            for _ in range(min(3, len(attractions))):
                if att_idx < len(attractions):
                    day_atts.append(attractions[att_idx])
                    att_idx += 1

            restaurant = restaurants[day_num % len(restaurants)] if restaurants else "Local Restaurant"

            daily_spending = (
                self._accom_cost_per_night() +
                self._transport_cost_per_day() +
                sum(a.get("cost", 0) for a in day_atts) +
                {"low": 25, "medium": 55, "high": 130}[self._budget_level()]
            ) * self.travelers

            weather = self._day_weather(day_num)

            timeline = [
                {"time": "08:00", "activity": "Breakfast at hotel / local café", "type": "food",
                 "duration": "45m", "cost": 0},
            ]
            for i, att in enumerate(day_atts):
                hour = 9 + i * 3
                timeline.append({
                    "time": f"{hour:02d}:00",
                    "activity": att["name"],
                    "type": att.get("type", "sightseeing"),
                    "duration": att.get("duration", "2h"),
                    "cost": att.get("cost", 0) * self.travelers,
                    "desc": att.get("desc", ""),
                    "rating": att.get("rating", 0),
                })
            timeline.append({"time": "13:00", "activity": f"Lunch at {restaurant}",
                              "type": "food", "duration": "1h",
                              "cost": {"low": 15, "medium": 35, "high": 80}[self._budget_level()] * self.travelers})
            timeline.append({"time": "19:00", "activity": "Dinner & evening stroll",
                              "type": "food", "duration": "1.5h",
                              "cost": {"low": 20, "medium": 45, "high": 100}[self._budget_level()] * self.travelers})

            # ── Weather-based adjustment note ──────────────────────────
            adj_note = None
            condition    = weather["condition"]
            rain_pct     = weather.get("rain_probability", 0)
            temp_c       = weather.get("temp_c", 20)
            outdoor_acts = [t for t in timeline
                            if t.get("type") in ("sightseeing","adventure","nature","landmark")]

            if condition in ("heavy_rain", "thunderstorm"):
                if outdoor_acts:
                    # Find a better day for outdoor activities
                    clear_days = [d for d in range(1, self.days + 1)
                                  if d != day_num]  # placeholder — full scan done in advisor
                    adj_note = (
                        f"⚠️ {weather['label']} expected ({rain_pct}% rain probability). "
                        f"Consider moving {outdoor_acts[0]['activity']} indoors or to another day. "
                        f"Recommended indoor alternatives: museums, galleries, restaurants, or spa."
                    )
            elif condition == "light_rain" and rain_pct > 55:
                if outdoor_acts:
                    adj_note = (
                        f"🌦 Light rain likely ({rain_pct}%). Pack a compact umbrella. "
                        f"{outdoor_acts[0]['activity']} is still doable — mornings are usually clearer."
                    )
            elif condition == "snow":
                if outdoor_acts:
                    adj_note = (
                        f"🌨 Snow forecast today. Check if {outdoor_acts[0]['activity']} "
                        f"is accessible. Allow extra travel time — surfaces may be slippery."
                    )
            elif condition == "hot" or temp_c >= 34:
                midday_outdoor = [t for t in outdoor_acts
                                  if t.get("time", "09:00") >= "11:00"
                                  and t.get("time", "09:00") <= "16:00"]
                if midday_outdoor:
                    adj_note = (
                        f"🌡️ Extreme heat: {temp_c}°C. "
                        f"Reschedule {midday_outdoor[0]['activity']} to before 10am or after 5pm. "
                        f"Stay hydrated and use air-conditioned transit. Consider indoor options 11am–4pm."
                    )
            elif condition == "windy":
                if outdoor_acts:
                    adj_note = (
                        f"💨 Strong winds expected. {outdoor_acts[0]['activity']} may be affected. "
                        f"Secure loose belongings and check for any attraction closures."
                    )

            itinerary.append({
                "day": day_num,
                "date": day_date,
                "theme": self._day_theme(day_num, day_atts),
                "weather": weather,
                "timeline": timeline,
                "daily_spending": round(daily_spending, 2),
                "adjustment_note": adj_note,
            })

        return itinerary

    def _day_theme(self, day, atts):
        # ── Interest-driven themes ────────────────────────────────────────────
        # If user has specific interests, try to name the day after them
        interest_theme_map = {
            "food":       "Food & Markets",
            "history":    "Cultural Immersion",
            "art":        "Art & Culture",
            "shopping":   "Shopping & Nightlife",
            "nature":     "Nature & Outdoors",
            "adventure":  "Adventure Day",
            "religious":  "Sacred Spaces",
            "nightlife":  "Evening & Nightlife",
            "photography":"Photography Walk",
            "luxury":     "Luxury Experience",
        }
        fallback_themes = ["Arrival & Orientation", "Cultural Immersion", "Adventure Day",
                           "Food & Markets", "Hidden Gems", "Relaxation Day", "Day Trip",
                           "Photography Walk", "Shopping & Nightlife", "Farewell Day"]

        if day == 1:
            return "Arrival & Orientation"
        if day == self.days:
            return "Farewell Day"

        # Match theme to the dominant attraction type of the day
        if atts:
            types = [a.get("type", "") for a in atts]
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
            dominant_type = max(type_counts, key=type_counts.get)

            type_to_theme = {
                "museum":     "Art & Culture",
                "historic":   "Cultural Immersion",
                "adventure":  "Adventure Day",
                "nature":     "Nature & Outdoors",
                "food":       "Food & Markets",
                "shopping":   "Shopping & Nightlife",
                "religious":  "Sacred Spaces",
                "art":        "Art & Culture",
                "landmark":   "Iconic Sights",
                "neighbourhood": "Local Discovery",
            }
            if dominant_type in type_to_theme:
                return type_to_theme[dominant_type]

        # If user has a primary interest, use that for mid-trip days
        if self.interests and 1 < day < self.days:
            primary_interest = self.interests[day % len(self.interests)]
            if primary_interest in interest_theme_map:
                return interest_theme_map[primary_interest]

        return fallback_themes[day % len(fallback_themes)]

    def _day_weather(self, day_num):
        self._rng.seed(self._seed + day_num)
        condition_keys = list(WEATHER_CONDITIONS.keys())
        weights        = [20,18,12,15,8,5,4,8,8,2]
        condition      = self._rng.choices(condition_keys, weights=weights, k=1)[0]
        base_temps = {
            "paris": (16,22), "tokyo": (18,26), "dubai": (28,38),
            "bali": (26,32), "new york": (14,24), "istanbul": (17,25),
            "rome": (19,27), "maldives": (28,33),
        }
        base = base_temps.get(self.dest_key, (18, 28))
        temp = self._rng.randint(base[0], base[1])
        rain_prob = {"clear": 5,"partly_cloudy": 15,"overcast": 35,"light_rain": 65,
                     "heavy_rain": 90,"thunderstorm": 95,"snow": 70,"windy": 20,
                     "hot": 5,"foggy": 25}
        cond_info = WEATHER_CONDITIONS[condition]
        return {
            "condition": condition,
            "label": cond_info["label"],
            "icon": cond_info["icon"],
            "temp_c": temp,
            "temp_f": round(temp * 9/5 + 32),
            "rain_probability": rain_prob.get(condition, 20),
            "clothing": cond_info["clothing"],
        }

    # ── Hotels ────────────────────────────────────────────────────────────────
    def get_hotels(self, destination=None, budget_type=None):
        bl = budget_type or self._budget_level()
        dest = destination or self.destination

        price_ranges = {"low": (20, 80), "medium": (80, 250), "high": (250, 800)}
        lo, hi = price_ranges.get(bl, (60, 200))

        hotel_templates = [
            {"name": f"Grand {dest} Hotel", "stars": 5, "type": "hotel",
             "amenities": ["Pool","Spa","Gym","Restaurant","Bar","Concierge"],
             "rating": 4.8, "distance_km": 0.8, "image": "hotel1.jpg"},
            {"name": f"{dest} City Boutique", "stars": 4, "type": "hotel",
             "amenities": ["Breakfast Included","WiFi","Rooftop Bar"],
             "rating": 4.6, "distance_km": 1.2, "image": "hotel2.jpg"},
            {"name": f"The {dest} Residences", "stars": 4, "type": "apartment",
             "amenities": ["Full Kitchen","Laundry","Gym","24h Reception"],
             "rating": 4.5, "distance_km": 1.8, "image": "hotel3.jpg"},
            {"name": f"{dest} Heritage Inn", "stars": 3, "type": "hotel",
             "amenities": ["Breakfast","WiFi","Historic Building"],
             "rating": 4.3, "distance_km": 2.1, "image": "hotel4.jpg"},
            {"name": f"Nomad Hostel {dest}", "stars": 2, "type": "hostel",
             "amenities": ["Shared Kitchen","Lockers","Social Events","Free Tours"],
             "rating": 4.4, "distance_km": 1.5, "image": "hotel5.jpg"},
        ]

        hotels = []
        self._rng.seed(self._seed)
        for i, h in enumerate(hotel_templates):
            price = round(self._rng.uniform(lo, hi), 0)
            rooms = self._rng.randint(3, 12)
            h["price_per_night"] = price
            h["available_rooms"] = rooms
            h["id"] = f"hotel_{i+1}"
            hotels.append(h)

        return hotels

    # ── Weather forecast ──────────────────────────────────────────────────────
    def generate_weather_forecast(self, destination, days):
        self.dest_key = destination.lower().strip()
        self._seed    = int(hashlib.md5(destination.encode()).hexdigest(), 16) % (10**9)
        self._rng     = random.Random(self._seed)
        forecast = []
        try:
            start = datetime.today()
        except Exception:
            start = datetime(2024, 1, 1)
        for day in range(1, days + 1):
            date = start + timedelta(days=day - 1)
            w    = self._day_weather(day)
            w["date"] = date.strftime("%A, %b %d")
            forecast.append(w)
        return forecast

    # ── Destination recommendations ───────────────────────────────────────────
    def recommend_destinations(self, interests, budget_level, travel_type,
                                travelers=1, travel_month=None, trip_days=None,
                                category_filter=None):
        """
        Enhanced recommendation engine — scores all destinations across 7 dimensions:
          1. Interest match (Jaccard similarity)           — up to 35 pts
          2. Budget fit                                    — up to 20 pts
          3. Travel-type & travel-style alignment          — up to 20 pts
          4. Season / timing quality                       — up to 10 pts
          5. Group type & traveler-count suitability       — up to 7 pts
          6. Trip duration suitability                     — up to 5 pts
          7. Category bonus (if category_filter set)       — up to 3 pts
        Total is capped at 99.
        """
        if travel_month is None:
            travel_month = datetime.today().month
        if trip_days is None:
            trip_days = self.days

        recs = []
        for key, dest in DESTINATIONS.items():
            tags         = set(dest.get("tags", []))
            user_i       = set(interests)
            dest_styles  = dest.get("travel_style", [])
            dest_groups  = dest.get("group_types", [])
            dest_dur     = dest.get("trip_duration", {"min": 2, "ideal": 5, "max": 14})
            dest_cat     = dest.get("category", "")

            # ── 1. Interest match (0–35) ──────────────────────────────────
            if user_i:
                jaccard   = len(tags & user_i) / max(len(tags | user_i), 1)
                int_score = round(jaccard * 35)
            else:
                int_score = 17   # neutral when no interests selected

            # ── 2. Budget fit (0–20) ──────────────────────────────────────
            daily_costs = dest.get("daily_budget", {})
            budget_thresholds = {"low": 80, "medium": 250, "high": 9999}
            dest_min = daily_costs.get("low", 60)
            dest_mid = daily_costs.get("medium", 150)
            user_max = budget_thresholds[budget_level]
            if daily_costs.get(budget_level, 9999) <= user_max:
                budget_score = 20   # perfect fit
            elif dest_min <= user_max * 1.2:
                budget_score = 10   # slightly over but reachable
            else:
                budget_score = 3    # out of budget

            # ── 3. Travel-type & travel-style alignment (0–20) ─────────────
            # Map travel type to preferred tags AND travel styles
            type_tag_map = {
                "solo":      ["nature","adventure","photography","nightlife","history"],
                "couple":    ["food","shopping","luxury","art","romance","nature"],
                "family":    ["nature","history","food","adventure","religious"],
                "friends":   ["nightlife","adventure","food","shopping","nature"],
                "religious": ["religious","history","pilgrimage"],
                "pilgrimage":["religious","history","pilgrimage"],
                "luxury":    ["luxury","food","art","shopping","nightlife"],
                "backpacker":["nature","adventure","history","food"],
            }
            type_style_map = {
                "solo":      ["solo","culture","adventure","nature","photography","budget"],
                "couple":    ["romance","luxury","food","culture","beach"],
                "family":    ["family","nature","culture","adventure","food"],
                "friends":   ["group","nightlife","adventure","food","beach"],
                "religious": ["religious","pilgrimage","spiritual","culture"],
                "pilgrimage":["religious","pilgrimage","spiritual"],
                "luxury":    ["luxury","romance","food"],
                "backpacker":["budget","adventure","culture","nature"],
            }
            preferred_tags   = type_tag_map.get(travel_type, ["nature","food","history"])
            preferred_styles = type_style_map.get(travel_type, [])

            tag_matches   = sum(3 for t in preferred_tags if t in tags)
            style_matches = sum(3 for s in preferred_styles if s in dest_styles)
            type_score    = min(tag_matches + style_matches, 20)

            # ── 4. Season / timing quality (0–10) ────────────────────────
            best_months  = dest.get("best_months", list(range(1, 13)))
            from ai_advisor import DEST_ADVISOR
            crowd_months = DEST_ADVISOR.get(key, {}).get("crowd_months", [])

            if travel_month in best_months and travel_month not in crowd_months:
                season_score = 10   # ideal: good season, not crowded
            elif travel_month in best_months:
                season_score = 6    # good season but crowded
            elif travel_month not in crowd_months:
                season_score = 4    # not peak but not worst
            else:
                season_score = 1    # off-season AND crowded

            # ── 5. Group type & traveler-count suitability (0–7) ──────────
            group_map = {
                1:  "solo",
                2:  "couple",
            }
            if travelers == 1:
                user_group = "solo"
            elif travelers == 2:
                user_group = "couple"
            elif travelers <= 5:
                user_group = "friends"
            else:
                user_group = "family"

            if user_group in dest_groups:
                idx_bonus = max(0, 3 - dest_groups.index(user_group))  # first pos = 3, later = less
                count_score = 4 + idx_bonus  # 4–7
            else:
                count_score = 3

            # Safety bonus for solo/family
            safety = dest.get("safety", "moderate")
            if user_group in ("solo", "family") and safety in ("very safe", "safe"):
                count_score = min(count_score + 1, 7)

            # ── 6. Trip duration suitability (0–5) ───────────────────────
            ideal_dur = dest_dur.get("ideal", 5)
            min_dur   = dest_dur.get("min", 2)
            max_dur   = dest_dur.get("max", 14)
            if min_dur <= trip_days <= max_dur:
                # Within valid range — score by proximity to ideal
                diff = abs(trip_days - ideal_dur)
                if diff == 0:
                    dur_score = 5
                elif diff <= 1:
                    dur_score = 4
                elif diff <= 2:
                    dur_score = 3
                else:
                    dur_score = 2
            else:
                dur_score = 1   # trip length outside comfortable range

            # ── 7. Category bonus (0–3) ──────────────────────────────────
            cat_score = 0
            if category_filter and dest_cat.lower() == category_filter.lower():
                cat_score = 3
            elif category_filter:
                cat_score = 0
            else:
                cat_score = 1   # neutral when no filter

            total_match = min(
                int_score + budget_score + type_score + season_score +
                count_score + dur_score + cat_score,
                99
            )

            # ── Build why-recommended reasons ─────────────────────────────
            why = self._why_recommended(dest, interests, travel_type)

            # Append season context to reasons
            if season_score == 10:
                why.append("Excellent time to visit — currently in peak season")
            elif season_score <= 2:
                m_name = datetime(2024, travel_month, 1).strftime("%B")
                why.append(f"{m_name} is off-season — expect lower prices but variable weather")

            # Duration context
            if dur_score >= 4:
                why.append(f"Ideal for a {trip_days}-day trip")
            elif dur_score <= 1:
                ideal_str = f"{ideal_dur} days"
                why.append(f"Best experienced over {ideal_str} — consider adjusting your trip length")

            recs.append({
                "id":                   key.replace(" ", "_"),
                "name":                 key.title(),
                "country":              dest["country"],
                "description":          dest["description"],
                "category":             dest_cat,
                "match_pct":            total_match,
                "score_breakdown": {
                    "interests":   int_score,
                    "budget":      budget_score,
                    "travel_type": type_score,
                    "season":      season_score,
                    "group_size":  count_score,
                },
                "why":                  why[:3],
                "estimated_daily_cost": daily_costs.get(budget_level, 0),
                "difficulty":           dest.get("difficulty", "moderate"),
                "safety":               dest.get("safety", "moderate"),
                "best_months":          best_months,
                "tags":                 dest.get("tags", []),
                "image":                dest.get("image", "default.jpg"),
                "travel_style":         dest_styles,
                "group_types":          dest_groups,
                "trip_duration":        dest_dur,
            })

        recs.sort(key=lambda x: x["match_pct"], reverse=True)
        return recs[:6]

    def _why_recommended(self, dest, interests, travel_type):
        reasons = []
        tags   = dest.get("tags", [])
        styles = dest.get("travel_style", [])
        cat    = dest.get("category", "")

        # Interest-specific reasons
        matched = [i for i in interests if i in tags]
        if matched:
            if len(matched) == 1:
                reasons.append(f"Excellent for {matched[0]}")
            else:
                reasons.append(f"Matches your interests: {', '.join(matched[:3])}")

        # Category context
        if cat:
            reasons.append(f"{cat} — {dest.get('description', '')[:60].rstrip()}…" if len(dest.get('description','')) > 60 else cat)

        # Travel type reason
        type_map = {
            "solo":      "Great destination for solo exploration",
            "couple":    "Perfect romantic getaway",
            "family":    "Family-friendly with activities for all ages",
            "friends":   "Amazing group experiences and nightlife",
            "religious": "Significant religious and spiritual destination",
            "pilgrimage":"Revered pilgrimage site",
            "luxury":    "Premium luxury experience awaits",
            "backpacker":"Budget-friendly backpacker favourite",
        }
        if travel_type in type_map and not matched:
            reasons.append(type_map[travel_type])

        # Style match
        style_reasons = {
            "romance":   "Romantic atmosphere perfect for couples",
            "adventure": "Outstanding adventure activities",
            "trekking":  "World-class trekking and hiking",
            "diving":    "Exceptional diving and snorkelling",
            "spiritual": "Deep spiritual significance and peaceful ambience",
            "pilgrimage":"Sacred pilgrimage destination",
            "nightlife": "Vibrant nightlife scene",
            "beach":     "Beautiful beaches and coastal scenery",
            "luxury":    "Luxurious resorts and premium experiences",
        }
        for s in styles:
            if s in style_reasons and len(reasons) < 3:
                reasons.append(style_reasons[s])
                break

        # Safety reason for solo/family
        safety = dest.get("safety", "moderate")
        if travel_type in ("solo", "family") and safety in ("very safe", "safe"):
            reasons.append(f"Rated {safety} — peace of mind for {travel_type} travel")

        if not reasons:
            reasons = ["Popular destination with diverse experiences"]
        return reasons[:3]

    # ── Full plan ─────────────────────────────────────────────────────────────
    def generate_full_plan(self):
        dest_info = self._dest_data
        budget    = self._calculate_budget()
        itinerary = self._generate_itinerary()
        hotels    = self.get_hotels()
        weather   = self.generate_weather_forecast(self.destination, self.days)

        return {
            "destination": {
                "name":        self.destination,
                "country":     dest_info.get("country", ""),
                "description": dest_info.get("description", ""),
                "currency":    dest_info.get("currency", "USD"),
                "language":    dest_info.get("lang", "English"),
                "difficulty":  dest_info.get("difficulty", "moderate"),
                "safety":      dest_info.get("safety", "moderate"),
                "tags":        dest_info.get("tags", []),
                "image":       dest_info.get("image", "default.jpg"),
                "best_months": dest_info.get("best_months", []),
            },
            "trip_summary": {
                "traveler_name":  getattr(self, "traveler_name", ""),
                "traveler_age":   getattr(self, "traveler_age", None),
                "travel_type":    self.travel_type,
                "travelers":      self.travelers,
                "days":           self.days,
                "start_date":     self.start_date,
                "start_location": getattr(self, "start_location", ""),
                "accommodation":  self.accommodation,
                "transport":      self.transport,
                "interests":      self.interests,
                "budget_level":   self._budget_level(),
            },
            "budget":                 budget,
            "itinerary":              itinerary,
            "hotels":                 hotels[:3],
            "weather_overview":       weather,
            "top_attractions":        dest_info.get("attractions", [])[:5],
            "recommended_restaurants": dest_info.get("restaurants", [])[:5],
            "ai_insights":            self._generate_insights(budget, weather),
            "routes":                 self.generate_routes(),
        }

    # ── Route Planning ────────────────────────────────────────────────────────
    def generate_routes(self) -> dict:
        """
        Generates three route options for the destination:
          - fastest:  optimised for travel time (transit/taxi)
          - cheapest: optimised for cost (walking/public transport)
          - scenic:   optimised for experience (landmarks, viewpoints)

        Each route covers the top attractions with realistic travel times,
        estimated costs, and direct Google Maps links.
        """
        dest_key     = self.dest_key
        dest_data    = self._dest_data
        attractions  = dest_data.get("attractions", [])[:6]
        transport    = self.transport
        travelers    = self.travelers

        # ── Per-city route knowledge ──────────────────────────────────────────
        ROUTE_DATA = {
            "paris": {
                "transit":     {"name": "Métro + RER",   "cost_per_day": 10,  "avg_min_between": 15},
                "taxi":        {"name": "Uber/Taxi",      "cost_per_trip": 12, "avg_min_between": 10},
                "walking":     {"name": "Walking",        "cost_per_day": 0,   "avg_min_between": 25},
                "scenic_path": "Seine riverbank → Île de la Cité → Le Marais → Montmartre",
                "scenic_tip":  "Follow the Seine on foot for a classic Paris experience.",
                "transit_tip": "Navigo Day Pass (€8.65) covers all zones — best value for multiple stops.",
                "walk_tip":    "Paris is very walkable. Most major sights are within 30 min on foot.",
                "map_centre":  (48.8566, 2.3522),
            },
            "tokyo": {
                "transit":     {"name": "JR + Tokyo Metro", "cost_per_day": 12, "avg_min_between": 12},
                "taxi":        {"name": "Taxi",              "cost_per_trip": 18, "avg_min_between": 8},
                "walking":     {"name": "Walking",           "cost_per_day": 0,  "avg_min_between": 20},
                "scenic_path": "Asakusa → Ueno → Akihabara → Shibuya → Shinjuku",
                "scenic_tip":  "The Yamanote Loop Line gives a 360° tour of Tokyo's districts.",
                "transit_tip": "Get a Suica card — works on all JR, Metro and buses.",
                "walk_tip":    "Shinjuku to Shibuya is a pleasant 45-min walk through Harajuku.",
                "map_centre":  (35.6762, 139.6503),
            },
            "dubai": {
                "transit":     {"name": "Dubai Metro",  "cost_per_day": 8,  "avg_min_between": 18},
                "taxi":        {"name": "Uber/Careem",  "cost_per_trip": 8, "avg_min_between": 10},
                "walking":     {"name": "Walking",      "cost_per_day": 0,  "avg_min_between": 35},
                "scenic_path": "Dubai Frame → Creek → Gold Souk → Dubai Mall → Burj Khalifa",
                "scenic_tip":  "The Dubai Water Canal walk at night offers stunning city views.",
                "transit_tip": "The Red and Green metro lines cover most major tourist spots.",
                "walk_tip":    "Outdoor walking only recommended Oct–Apr. Use air-conditioned malls in summer.",
                "map_centre":  (25.2048, 55.2708),
            },
            "bali": {
                "transit":     {"name": "Ride-share (Gojek/Grab)", "cost_per_day": 8, "avg_min_between": 20},
                "taxi":        {"name": "Private Driver",           "cost_per_trip": 35, "avg_min_between": 25},
                "walking":     {"name": "Walking (Ubud only)",      "cost_per_day": 0,  "avg_min_between": 30},
                "scenic_path": "Tegallalang Rice Terraces → Ubud → Monkey Forest → Seminyak Beach",
                "scenic_tip":  "Hire a driver for full-day Ubud tour ($35–45) — most efficient.",
                "transit_tip": "Gojek motorbike taxi is cheapest ($1–3/ride) and fastest in traffic.",
                "walk_tip":    "Ubud centre is walkable. Outside Ubud, a driver is essential.",
                "map_centre":  (-8.4095, 115.1889),
            },
            "new york": {
                "transit":     {"name": "Subway",       "cost_per_day": 7,  "avg_min_between": 12},
                "taxi":        {"name": "Uber/Yellow Cab", "cost_per_trip": 15, "avg_min_between": 8},
                "walking":     {"name": "Walking",      "cost_per_day": 0,  "avg_min_between": 18},
                "scenic_path": "High Line → Chelsea → Times Square → Central Park → Upper East Side",
                "scenic_tip":  "The High Line elevated park is the most scenic pedestrian route.",
                "transit_tip": "OMNY unlimited weekly pass ($34) is best value for 5+ days.",
                "walk_tip":    "Manhattan below 59th Street is very walkable — most sights within 2 miles.",
                "map_centre":  (40.7128, -74.0060),
            },
            "istanbul": {
                "transit":     {"name": "Metro + Tram + Ferry", "cost_per_day": 5, "avg_min_between": 15},
                "taxi":        {"name": "Taxi",                 "cost_per_trip": 6, "avg_min_between": 12},
                "walking":     {"name": "Walking",              "cost_per_day": 0, "avg_min_between": 22},
                "scenic_path": "Sultanahmet → Grand Bazaar → Galata Bridge → Beyoğlu → Galata Tower",
                "scenic_tip":  "The Bosphorus ferry ($1.50) between continents is the most scenic ride.",
                "transit_tip": "Istanbulkart prepaid card saves 50% vs single tickets.",
                "walk_tip":    "The Old City (Sultanahmet) is very walkable — all major sites within 1km.",
                "map_centre":  (41.0082, 28.9784),
            },
            "rome": {
                "transit":     {"name": "Bus + Metro",  "cost_per_day": 7,  "avg_min_between": 14},
                "taxi":        {"name": "Taxi",          "cost_per_trip": 10, "avg_min_between": 10},
                "walking":     {"name": "Walking",       "cost_per_day": 0,  "avg_min_between": 20},
                "scenic_path": "Colosseum → Roman Forum → Palatine Hill → Circus Maximus → Trastevere",
                "scenic_tip":  "All of central Rome is a 3km walk — the best way to discover hidden gems.",
                "transit_tip": "48h transit pass (€12.50) covers unlimited bus and metro.",
                "walk_tip":    "Rome's historic centre is fully walkable — taxi only needed for Vatican area.",
                "map_centre":  (41.9028, 12.4964),
            },
            "maldives": {
                "transit":     {"name": "Speedboat",       "cost_per_day": 30, "avg_min_between": 45},
                "taxi":        {"name": "Seaplane Transfer", "cost_per_trip": 300, "avg_min_between": 35},
                "walking":     {"name": "Island Walking",   "cost_per_day": 0,   "avg_min_between": 10},
                "scenic_path": "North Malé Atoll → Local Island → Sandbank → House Reef snorkel",
                "scenic_tip":  "Speedboat at sunset between islands is unforgettable.",
                "transit_tip": "Book speedboat transfers when booking accommodation — bundled deals save 30%.",
                "walk_tip":    "Each island is tiny — everything is walkable within the resort or local island.",
                "map_centre":  (3.2028, 73.2207),
            },
        }

        rd = ROUTE_DATA.get(dest_key, {
            "transit":     {"name": "Public Transport", "cost_per_day": 8, "avg_min_between": 20},
            "taxi":        {"name": "Taxi/Rideshare",   "cost_per_trip": 10, "avg_min_between": 12},
            "walking":     {"name": "Walking",           "cost_per_day": 0,  "avg_min_between": 25},
            "scenic_path": f"City Centre → Main Attractions → {self.destination} highlights",
            "scenic_tip":  "Ask your hotel concierge for the best local walking route.",
            "transit_tip": "Purchase a multi-day transit pass for significant savings.",
            "walk_tip":    "Many city centres are walkable — check your hotel's local map.",
            "map_centre":  (0, 0),
        })

        # ── Build attraction waypoints ─────────────────────────────────────────
        def make_waypoints(atts, max_n=5):
            waypoints = []
            for i, att in enumerate(atts[:max_n]):
                waypoints.append({
                    "order":    i + 1,
                    "name":     att["name"],
                    "type":     att.get("type", "landmark"),
                    "duration": att.get("duration", "1.5h"),
                    "cost":     att.get("cost", 0) * travelers,
                    "desc":     att.get("desc", ""),
                })
            return waypoints

        # ── Cost calculations ──────────────────────────────────────────────────
        transit_daily  = rd["transit"]["cost_per_day"] * travelers * self.days
        scenic_waypts  = make_waypoints(attractions)
        fastest_waypts = sorted(
            make_waypoints(attractions),
            key=lambda x: float(x["duration"].replace("h","").replace("m","").split(".")[0]) if "h" in x["duration"] else 0
        )
        cheapest_waypts = sorted(
            make_waypoints(attractions),
            key=lambda x: x["cost"]
        )

        # ── Total travel times ─────────────────────────────────────────────────
        def total_travel_min(waypts, mins_between):
            return (len(waypts) - 1) * mins_between if len(waypts) > 1 else 0

        fastest_travel   = total_travel_min(fastest_waypts,  rd["taxi"]["avg_min_between"])
        cheapest_travel  = total_travel_min(cheapest_waypts, rd["walking"]["avg_min_between"])
        scenic_travel    = total_travel_min(scenic_waypts,   rd["transit"]["avg_min_between"])

        # ── Google Maps route URLs ─────────────────────────────────────────────
        def maps_url(waypts):
            if not waypts:
                return f"https://www.google.com/maps/search/{self.destination}"
            origin = waypts[0]["name"] if waypts else self.destination
            dest_w = waypts[-1]["name"] if len(waypts) > 1 else self.destination
            stops  = waypts[1:-1]
            waypoints_param = ""
            if stops:
                import urllib.parse
                wp = "|".join(s["name"] + f", {self.destination}" for s in stops[:3])
                waypoints_param = f"&waypoints={urllib.parse.quote(wp)}"
            import urllib.parse
            return (
                f"https://www.google.com/maps/dir/"
                f"{urllib.parse.quote(origin + ', ' + self.destination)}/"
                f"{urllib.parse.quote(dest_w + ', ' + self.destination)}"
                f"{waypoints_param}"
            )

        return {
            "fastest": {
                "label":        "Fastest Route",
                "icon":         "⚡",
                "description":  f"Optimised for speed using {rd['taxi']['name']}.",
                "transport":    rd["taxi"]["name"],
                "cost_note":    f"~${rd['taxi']['cost_per_trip'] * max(len(fastest_waypts)-1, 1) * travelers} total transfers",
                "total_travel_min": fastest_travel,
                "tip":          f"Best when time is tight. {rd.get('transit_tip','')}",
                "waypoints":    fastest_waypts,
                "maps_url":     maps_url(fastest_waypts),
            },
            "cheapest": {
                "label":        "Budget Route",
                "icon":         "💰",
                "description":  f"Minimises cost using {rd['walking']['name']} and public transport.",
                "transport":    rd["walking"]["name"],
                "cost_note":    f"~${rd['transit']['cost_per_day'] * travelers}/day transit",
                "total_travel_min": cheapest_travel,
                "tip":          rd.get("walk_tip", ""),
                "waypoints":    cheapest_waypts,
                "maps_url":     maps_url(cheapest_waypts),
            },
            "scenic": {
                "label":        "Scenic Route",
                "icon":         "🎭",
                "description":  f"The best visual experience: {rd.get('scenic_path','')}",
                "transport":    rd["transit"]["name"],
                "cost_note":    f"~${transit_daily} total transport ({self.days} days)",
                "total_travel_min": scenic_travel,
                "tip":          rd.get("scenic_tip", ""),
                "waypoints":    scenic_waypts,
                "maps_url":     maps_url(scenic_waypts),
            },
            "map_centre": rd.get("map_centre", (0, 0)),
            "destination": self.destination,
        }

    def _generate_insights(self, budget, weather):
        """
        Generates rich, personalised AI insights using all traveler profile data.
        Combines budget level, travel type, interests, age, group size, and weather.
        """
        insights = []
        bl         = self._budget_level()
        traveler_age  = getattr(self, "traveler_age", None)
        traveler_name = getattr(self, "traveler_name", "")

        # ── Budget insights ───────────────────────────────────────────────
        if bl == "low":
            insights.append(
                "💡 Budget tip: Prioritise free attractions and street food. "
                "Most cities have excellent free museums, parks, and walking routes."
            )
        elif bl == "high":
            insights.append(
                "✨ Premium budget unlocked. Consider a private guided tour on Day 2 — "
                "it typically costs $80–150 and transforms your understanding of the destination."
            )
        else:
            daily_pp = self.budget / max(self.days, 1) / max(self.travelers, 1)
            insights.append(
                f"💰 Your ${daily_pp:.0f}/person/day budget covers comfortable mid-range travel. "
                "Lunch at local restaurants (not tourist traps) keeps food costs 40% lower."
            )

        # ── Weather insights ──────────────────────────────────────────────
        rainy = [w for w in weather if w.get("rain_probability", 0) > 70]
        if rainy:
            insights.append(
                f"🌧 Rain is likely on {len(rainy)} day(s) of your trip. "
                "Pack a compact umbrella. Indoor alternatives (museums, galleries, spas) "
                "are pre-selected for those days in your itinerary."
            )
        hot_days = [w for w in weather if w.get("temp_c", 0) >= 34]
        if hot_days:
            insights.append(
                f"🌡️ Expect extreme heat ({hot_days[0].get('temp_c')}°C+) on {len(hot_days)} day(s). "
                "Plan outdoor activities before 10am or after 5pm. Stay hydrated."
            )

        # ── Travel type insights ──────────────────────────────────────────
        type_insights = {
            "solo":    "🧳 Solo tip: Book your first night's accommodation before arrival. "
                       "Meeting other travellers is easiest at hostels with social common areas.",
            "couple":  "💑 Couple tip: Book at least one special dinner in advance — "
                       "top restaurants fill up 1–2 weeks ahead.",
            "family":  "👨‍👩‍👧 Family tip: Most major attractions offer family tickets saving 30–40%. "
                       "Always carry snacks and build in a rest afternoon every 3 days.",
            "friends": "👯 Group tip: Use Splitwise to track shared expenses — "
                       "settle up at the end of each day to avoid awkward end-of-trip maths.",
        }
        if self.travel_type in type_insights:
            insights.append(type_insights[self.travel_type])

        # ── Age-aware insights ────────────────────────────────────────────
        if traveler_age:
            if traveler_age >= 65:
                insights.append(
                    "🩺 Senior travel tip: Confirm your travel insurance covers pre-existing conditions. "
                    "Your itinerary prioritises accessible, lower-intensity activities."
                )
            elif traveler_age <= 12:
                insights.append(
                    "🎒 Travelling with kids: Pack entertainment for transit — "
                    "audiobooks and offline maps are essentials. "
                    "Your itinerary front-loads the most engaging activities."
                )
            elif traveler_age < 30:
                insights.append(
                    "🌍 Young traveller tip: Look for hostel or hotel loyalty programmes — "
                    "many offer free night rewards after 5–10 stays."
                )

        # ── Interest-specific insights ────────────────────────────────────
        interest_insights = {
            "food":       "🍽️ Foodie alert: Book popular restaurant reservations at least 3 days ahead.",
            "photography":"📷 Photography tip: Golden hour is 30–60 min after sunrise — the best light of the day.",
            "adventure":  "🧗 Adventure tip: Book guided excursions 48h ahead; they sell out in peak season.",
            "history":    "🏛️ History tip: Free audio guides are available via Google Maps for most historic sites.",
            "shopping":   "🛍️ Shopping tip: Always compare prices at 2–3 shops before buying — especially in markets.",
            "religious":  "🕌 Cultural respect tip: Research dress codes before visiting religious sites — "
                          "modest clothing (covered shoulders/knees) is expected.",
            "nature":     "🌿 Nature tip: Early morning visits to natural sites give you better wildlife sightings "
                          "and far fewer crowds.",
            "luxury":     "💎 Luxury tip: Book hotel concierge services at least 1 week ahead for premium experiences.",
            "nightlife":  "🌃 Nightlife tip: Ride-sharing apps are safer and cheaper than unmetered taxis after midnight.",
            "art":        "🎨 Art tip: Museum audio guides (usually €3–5) are worth it — they triple your understanding.",
        }
        for interest in self.interests[:2]:
            if interest in interest_insights:
                insights.append(interest_insights[interest])

        # ── Group-size insights ───────────────────────────────────────────
        if self.travelers >= 4:
            group_save = round(self.budget * 0.08)
            insights.append(
                f"👥 Group of {self.travelers}: Book a private minibus for airport transfers — "
                f"costs ~${40 * self.travelers} vs ${10 * self.travelers} each for taxis, "
                "but saves time and luggage hassle."
            )

        # ── Long trip pacing ──────────────────────────────────────────────
        if self.days > 10:
            insights.append(
                "📅 Long trip ahead. Schedule one 'rest day' every 4–5 days — "
                "no fixed plans, just exploring at your own pace. "
                "It prevents fatigue and often leads to the best unplanned discoveries."
            )

        return insights[:6]  # cap at 6 to keep UI clean
