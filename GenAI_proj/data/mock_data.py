from __future__ import annotations

import pandas as pd

APP_NAME = "ReLoop AI"
CITY = "Bengaluru"
MAP_CENTER = (12.9716, 77.5946)

USER = {
    "name": "Aarav Mehta",
    "first_name": "Aarav",
    "initials": "AM",
    "email": "aarav.mehta@example.com",
    "tier": "Green Guardian",
    "next_tier": "Circular Champion",
    "next_tier_points": 3000,
    "points": 2480,
    "streak_days": 12,
    "devices_recycled": 46,
    "member_since": "Mar 2025",
    "city": CITY,
}

MONTHLY_IMPACT = pd.DataFrame(
    [
        {"month": "Dec", "waste_kg": 62, "devices": 18, "co2_kg": 149},
        {"month": "Jan", "waste_kg": 71, "devices": 22, "co2_kg": 170},
        {"month": "Feb", "waste_kg": 68, "devices": 21, "co2_kg": 163},
        {"month": "Mar", "waste_kg": 84, "devices": 27, "co2_kg": 202},
        {"month": "Apr", "waste_kg": 91, "devices": 30, "co2_kg": 218},
        {"month": "May", "waste_kg": 88, "devices": 29, "co2_kg": 211},
        {"month": "Jun", "waste_kg": 104, "devices": 35, "co2_kg": 250},
        {"month": "Jul", "waste_kg": 112, "devices": 38, "co2_kg": 269},
        {"month": "Aug", "waste_kg": 109, "devices": 36, "co2_kg": 262},
        {"month": "Sep", "waste_kg": 126, "devices": 43, "co2_kg": 302},
        {"month": "Oct", "waste_kg": 134, "devices": 46, "co2_kg": 322},
        {"month": "Nov", "waste_kg": 142, "devices": 49, "co2_kg": 341},
    ]
)

CATEGORY_BREAKDOWN = pd.DataFrame(
    [
        {"category": "Smartphones", "share": 34},
        {"category": "Laptops", "share": 22},
        {"category": "Accessories", "share": 16},
        {"category": "Home appliances", "share": 13},
        {"category": "Tablets", "share": 9},
        {"category": "Other", "share": 6},
    ]
)

MONTHLY_BY_CATEGORY = pd.DataFrame(
    [
        {"month": "Dec", "Smartphones": 6, "Laptops": 4, "Accessories": 3, "Home appliances": 2, "Tablets": 2, "Other": 1},
        {"month": "Jan", "Smartphones": 8, "Laptops": 4, "Accessories": 3, "Home appliances": 3, "Tablets": 2, "Other": 2},
        {"month": "Feb", "Smartphones": 7, "Laptops": 4, "Accessories": 3, "Home appliances": 3, "Tablets": 2, "Other": 2},
        {"month": "Mar", "Smartphones": 9, "Laptops": 5, "Accessories": 4, "Home appliances": 3, "Tablets": 3, "Other": 3},
        {"month": "Apr", "Smartphones": 10, "Laptops": 6, "Accessories": 5, "Home appliances": 4, "Tablets": 3, "Other": 2},
        {"month": "May", "Smartphones": 10, "Laptops": 6, "Accessories": 4, "Home appliances": 4, "Tablets": 3, "Other": 2},
        {"month": "Jun", "Smartphones": 12, "Laptops": 8, "Accessories": 5, "Home appliances": 4, "Tablets": 3, "Other": 3},
        {"month": "Jul", "Smartphones": 13, "Laptops": 8, "Accessories": 6, "Home appliances": 4, "Tablets": 4, "Other": 3},
        {"month": "Aug", "Smartphones": 12, "Laptops": 8, "Accessories": 5, "Home appliances": 5, "Tablets": 3, "Other": 3},
        {"month": "Sep", "Smartphones": 15, "Laptops": 9, "Accessories": 6, "Home appliances": 5, "Tablets": 4, "Other": 4},
        {"month": "Oct", "Smartphones": 16, "Laptops": 10, "Accessories": 7, "Home appliances": 6, "Tablets": 4, "Other": 3},
        {"month": "Nov", "Smartphones": 17, "Laptops": 11, "Accessories": 7, "Home appliances": 6, "Tablets": 4, "Other": 4},
    ]
)

DEVICE_TYPE_VOLUME = pd.DataFrame(
    [
        {"device": "Smartphones", "units": 134},
        {"device": "Laptops", "units": 86},
        {"device": "Accessories", "units": 58},
        {"device": "Home appliances", "units": 42},
        {"device": "Tablets", "units": 38},
        {"device": "Other", "units": 36},
    ]
)

MATERIAL_RECOVERY = pd.DataFrame(
    [
        {"material": "Copper", "kg": 334},
        {"material": "Aluminium", "kg": 262},
        {"material": "Plastics", "kg": 238},
        {"material": "Rare earth", "kg": 107},
        {"material": "Gold", "kg": 71},
        {"material": "Silver", "kg": 48},
        {"material": "Other", "kg": 131},
    ]
)

RECENT_ACTIVITY = [
    {
        "title": "Dropped off 2 smartphones",
        "detail": "GreenLoop Hub · Indiranagar",
        "time": "2h ago",
        "points": "+120",
        "icon": "phone",
        "tone": "green",
    },
    {
        "title": "Booked a home pickup",
        "detail": "Laptop + accessories · Sat, 7 Nov",
        "time": "Yesterday",
        "points": "",
        "icon": "truck",
        "tone": "blue",
    },
    {
        "title": "Completed a 7-day streak",
        "detail": "Recycling streak milestone",
        "time": "2 days ago",
        "points": "+80",
        "icon": "zap",
        "tone": "amber",
    },
    {
        "title": "Redeemed a bamboo organizer",
        "detail": "Rewards marketplace",
        "time": "4 days ago",
        "points": "-450",
        "icon": "gift",
        "tone": "coral",
    },
    {
        "title": "Recycled a 24-inch monitor",
        "detail": "TechTakeback Centre · Electronic City",
        "time": "6 days ago",
        "points": "+200",
        "icon": "monitor",
        "tone": "green",
    },
    {
        "title": "Earned Circular Starter",
        "detail": "First verified drop-off",
        "time": "1 week ago",
        "points": "+50",
        "icon": "award",
        "tone": "purple",
    },
]

NEXT_PICKUP = {
    "day": "07",
    "month": "NOV",
    "title": "Laptop + accessories",
    "when": "Sat · 4:00–6:00 PM",
    "partner": "Ravi K. · EV pickup van",
    "status": "Confirmed",
}

MONTHLY_GOAL = {
    "label": "Monthly diversion goal",
    "current": 142,
    "target": 150,
    "unit": "kg",
}

COLLECTION_POINTS = [
    {
        "name": "GreenLoop Recycling Hub",
        "type": "Recycling Centre",
        "area": "Indiranagar",
        "address": "12th Main Rd, Indiranagar, Bengaluru 560038",
        "lat": 12.9784,
        "lon": 77.6408,
        "hours": "9:00–18:00",
        "open_now": True,
        "accepted": ["Smartphones", "Laptops", "Batteries", "Cables"],
        "capacity": 72,
        "rating": 4.8,
        "distance_km": 2.4,
        "partner": True,
    },
    {
        "name": "EcoByte Collection Point",
        "type": "Drop-off",
        "area": "Koramangala",
        "address": "80 Feet Rd, 4th Block, Koramangala 560034",
        "lat": 12.9352,
        "lon": 77.6245,
        "hours": "10:00–20:00",
        "open_now": True,
        "accepted": ["Smartphones", "Tablets", "Cables"],
        "capacity": 48,
        "rating": 4.6,
        "distance_km": 3.1,
        "partner": True,
    },
    {
        "name": "EarthCare E-Waste Facility",
        "type": "Recycling Centre",
        "area": "Whitefield",
        "address": "Hope Farm Junction, Whitefield 560066",
        "lat": 12.9698,
        "lon": 77.75,
        "hours": "8:30–17:30",
        "open_now": True,
        "accepted": ["Smartphones", "Laptops", "Appliances", "Batteries", "Cables"],
        "capacity": 63,
        "rating": 4.7,
        "distance_km": 12.8,
        "partner": True,
    },
    {
        "name": "ReNew Tech Depot",
        "type": "Refurbisher",
        "area": "Jayanagar",
        "address": "11th Main Rd, 4th Block, Jayanagar 560011",
        "lat": 12.925,
        "lon": 77.5938,
        "hours": "10:00–19:00",
        "open_now": True,
        "accepted": ["Laptops", "Desktops", "Monitors"],
        "capacity": 39,
        "rating": 4.5,
        "distance_km": 4.6,
        "partner": False,
    },
    {
        "name": "Cirqle Collection Kiosk",
        "type": "Kiosk",
        "area": "HSR Layout",
        "address": "27th Main Rd, Sector 1, HSR Layout 560102",
        "lat": 12.9116,
        "lon": 77.6389,
        "hours": "Open 24 hours",
        "open_now": True,
        "accepted": ["Smartphones", "Batteries", "Cables"],
        "capacity": 21,
        "rating": 4.4,
        "distance_km": 5.2,
        "partner": True,
    },
    {
        "name": "BlueGreen Recyclers",
        "type": "Recycling Centre",
        "area": "Hebbal",
        "address": "Bellary Rd, Hebbal Industrial Area 560024",
        "lat": 13.0358,
        "lon": 77.597,
        "hours": "9:00–18:00",
        "open_now": True,
        "accepted": ["Appliances", "Monitors", "Printers"],
        "capacity": 81,
        "rating": 4.3,
        "distance_km": 8.9,
        "partner": True,
    },
    {
        "name": "UrbanMine Drop-off",
        "type": "Drop-off",
        "area": "Malleshwaram",
        "address": "Sampige Rd, Malleshwaram 560003",
        "lat": 13.0035,
        "lon": 77.5648,
        "hours": "9:00–17:00",
        "open_now": False,
        "accepted": ["Smartphones", "Laptops", "Appliances", "Batteries"],
        "capacity": 35,
        "rating": 4.6,
        "distance_km": 6.4,
        "partner": True,
    },
    {
        "name": "TechTakeback Centre",
        "type": "Recycling Centre",
        "area": "Electronic City",
        "address": "Phase 1, Electronic City 560100",
        "lat": 12.8452,
        "lon": 77.6602,
        "hours": "9:00–18:30",
        "open_now": True,
        "accepted": ["Laptops", "Desktops", "Batteries", "Monitors"],
        "capacity": 57,
        "rating": 4.9,
        "distance_km": 14.2,
        "partner": True,
    },
    {
        "name": "LoopWorks Refurb Lab",
        "type": "Refurbisher",
        "area": "Rajajinagar",
        "address": "1st Block, Rajajinagar 560010",
        "lat": 12.991,
        "lon": 77.552,
        "hours": "11:00–19:00",
        "open_now": True,
        "accepted": ["Smartphones", "Laptops", "Tablets"],
        "capacity": 44,
        "rating": 4.7,
        "distance_km": 7.1,
        "partner": False,
    },
    {
        "name": "Sapling E-Waste Bank",
        "type": "Drop-off",
        "area": "Yelahanka",
        "address": "New Town Main Rd, Yelahanka 560064",
        "lat": 13.1007,
        "lon": 77.5963,
        "hours": "8:00–16:00",
        "open_now": False,
        "accepted": ["Appliances", "Cables", "Batteries"],
        "capacity": 28,
        "rating": 4.2,
        "distance_km": 13.5,
        "partner": True,
    },
]

REPAIR_SHOPS = [
    {
        "name": "FixPoint Electronics",
        "type": "Repair Shop",
        "area": "Indiranagar",
        "address": "100 Feet Rd, Indiranagar, Bengaluru 560038",
        "lat": 12.9719,
        "lon": 77.6412,
        "hours": "10:00–19:00",
        "open_now": True,
        "accepted": ["Smartphones", "Laptops", "Tablets", "Cables"],
        "capacity": 55,
        "rating": 4.8,
        "distance_km": 1.8,
        "partner": True,
        "phone": "+91 80 4123 8801",
        "email": "hello@fixpoint.example",
        "speciality": "Screen and charging-port repairs",
    },
    {
        "name": "VoltFix Repairs",
        "type": "Repair Shop",
        "area": "Koramangala",
        "address": "5th Block, Koramangala, Bengaluru 560095",
        "lat": 12.9308,
        "lon": 77.6229,
        "hours": "10:30–20:00",
        "open_now": True,
        "accepted": ["Smartphones", "Laptops", "Tablets", "Cables"],
        "capacity": 61,
        "rating": 4.6,
        "distance_km": 3.4,
        "partner": True,
        "phone": "+91 80 4123 8802",
        "email": "care@voltfix.example",
        "speciality": "Board-level diagnostics and battery replacement",
    },
    {
        "name": "SecondLife Tech Studio",
        "type": "Repair Shop",
        "area": "Jayanagar",
        "address": "9th Main Rd, Jayanagar 2nd Block 560011",
        "lat": 12.9299,
        "lon": 77.5833,
        "hours": "11:00–19:00",
        "open_now": False,
        "accepted": ["Laptops", "Desktops", "Monitors", "Printers"],
        "capacity": 42,
        "rating": 4.5,
        "distance_km": 4.9,
        "partner": True,
        "phone": "+91 80 4123 8803",
        "email": "studio@secondlife.example",
        "speciality": "Laptop refurbishment and data-safe upgrades",
    },
]

COLLECTION_POINTS = COLLECTION_POINTS + REPAIR_SHOPS

for _index, _point in enumerate(COLLECTION_POINTS, start=1):
    _point.setdefault("id", f"partner-{_index:02d}")
    _point.setdefault("fictional", True)
    _point.setdefault("phone", f"+91 80 4000 {1000 + _index}")
    _point.setdefault("email", f"partner{_index}@reloop.example")
    _point.setdefault("speciality", "E-waste drop-off and material recovery")

ACCEPTED_TYPES = [
    "Smartphones",
    "Laptops",
    "Tablets",
    "Desktops",
    "Monitors",
    "Appliances",
    "Printers",
    "Batteries",
    "Cables",
]

DEVICE_CATALOG = {
    "Smartphone": {
        "category": "Mobile",
        "weight_kg": 0.18,
        "base_value": 1250,
        "co2_kg": 22.4,
        "recyclable_pct": 94,
        "materials": {"Copper": 30, "Aluminium": 18, "Plastics": 24, "Gold": 8, "Silver": 5, "Other": 15},
    },
    "Laptop": {
        "category": "Computing",
        "weight_kg": 2.1,
        "base_value": 3400,
        "co2_kg": 145.0,
        "recyclable_pct": 91,
        "materials": {"Copper": 26, "Aluminium": 24, "Plastics": 22, "Gold": 4, "Silver": 3, "Other": 21},
    },
    "Tablet": {
        "category": "Mobile",
        "weight_kg": 0.5,
        "base_value": 900,
        "co2_kg": 48.0,
        "recyclable_pct": 92,
        "materials": {"Copper": 28, "Aluminium": 20, "Plastics": 26, "Gold": 5, "Silver": 4, "Other": 17},
    },
    "Charger & cables": {
        "category": "Accessory",
        "weight_kg": 0.12,
        "base_value": 60,
        "co2_kg": 4.2,
        "recyclable_pct": 88,
        "materials": {"Copper": 46, "Aluminium": 12, "Plastics": 34, "Other": 8},
    },
    "Monitor": {
        "category": "Display",
        "weight_kg": 4.2,
        "base_value": 1100,
        "co2_kg": 210.0,
        "recyclable_pct": 86,
        "materials": {"Aluminium": 28, "Plastics": 26, "Copper": 16, "Rare earth": 6, "Other": 24},
    },
    "Desktop PC": {
        "category": "Computing",
        "weight_kg": 7.4,
        "base_value": 2600,
        "co2_kg": 300.0,
        "recyclable_pct": 89,
        "materials": {"Copper": 24, "Aluminium": 22, "Plastics": 20, "Gold": 5, "Silver": 4, "Other": 25},
    },
    "Printer": {
        "category": "Office",
        "weight_kg": 6.8,
        "base_value": 450,
        "co2_kg": 260.0,
        "recyclable_pct": 78,
        "materials": {"Plastics": 42, "Copper": 16, "Aluminium": 14, "Other": 28},
    },
    "Television": {
        "category": "Display",
        "weight_kg": 9.5,
        "base_value": 1500,
        "co2_kg": 380.0,
        "recyclable_pct": 84,
        "materials": {"Plastics": 32, "Aluminium": 22, "Copper": 14, "Rare earth": 6, "Other": 26},
    },
    "Refrigerator": {
        "category": "Appliance",
        "weight_kg": 45.0,
        "base_value": 2800,
        "co2_kg": 640.0,
        "recyclable_pct": 81,
        "materials": {"Copper": 22, "Aluminium": 20, "Plastics": 30, "Other": 28},
    },
    "Washing machine": {
        "category": "Appliance",
        "weight_kg": 38.0,
        "base_value": 2200,
        "co2_kg": 520.0,
        "recyclable_pct": 83,
        "materials": {"Copper": 24, "Aluminium": 18, "Plastics": 28, "Other": 30},
    },
    "Microwave": {
        "category": "Appliance",
        "weight_kg": 12.0,
        "base_value": 700,
        "co2_kg": 180.0,
        "recyclable_pct": 79,
        "materials": {"Copper": 20, "Aluminium": 22, "Plastics": 30, "Other": 28},
    },
    "Battery": {
        "category": "Hazardous",
        "weight_kg": 0.3,
        "base_value": 40,
        "co2_kg": 12.0,
        "recyclable_pct": 96,
        "materials": {"Copper": 18, "Aluminium": 12, "Plastics": 24, "Rare earth": 14, "Other": 32},
    },
    "Power Bank": {
        "category": "Accessory",
        "weight_kg": 0.25,
        "base_value": 320,
        "co2_kg": 14.0,
        "recyclable_pct": 90,
        "materials": {"Copper": 24, "Aluminium": 22, "Plastics": 30, "Rare earth": 8, "Other": 16},
    },
    "Earbuds": {
        "category": "Accessory",
        "weight_kg": 0.06,
        "base_value": 260,
        "co2_kg": 8.0,
        "recyclable_pct": 85,
        "materials": {"Copper": 22, "Plastics": 40, "Gold": 2, "Other": 36},
    },
    "Cable": {
        "category": "Accessory",
        "weight_kg": 0.05,
        "base_value": 30,
        "co2_kg": 2.1,
        "recyclable_pct": 88,
        "materials": {"Copper": 52, "Plastics": 38, "Other": 10},
    },
    "Small Appliance": {
        "category": "Appliance",
        "weight_kg": 3.5,
        "base_value": 900,
        "co2_kg": 90.0,
        "recyclable_pct": 80,
        "materials": {"Copper": 18, "Aluminium": 20, "Plastics": 34, "Other": 28},
    },
}

IDENTIFY_CATEGORIES = [
    "Phone",
    "Charger",
    "Power Bank",
    "Earbuds",
    "Laptop",
    "Cable",
    "Battery",
    "Small Appliance",
]

CATEGORY_TO_DEVICE = {
    "Phone": "Smartphone",
    "Charger": "Charger & cables",
    "Power Bank": "Power Bank",
    "Earbuds": "Earbuds",
    "Laptop": "Laptop",
    "Cable": "Cable",
    "Battery": "Battery",
    "Small Appliance": "Small Appliance",
}

DEVICE_CATEGORY_GROUP = {
    "Smartphone": "Smartphones",
    "Laptop": "Laptops",
    "Tablet": "Tablets",
    "Charger & cables": "Accessories",
    "Cable": "Accessories",
    "Power Bank": "Accessories",
    "Earbuds": "Accessories",
    "Monitor": "Other",
    "Desktop PC": "Other",
    "Printer": "Other",
    "Television": "Home appliances",
    "Refrigerator": "Home appliances",
    "Washing machine": "Home appliances",
    "Microwave": "Home appliances",
    "Small Appliance": "Home appliances",
    "Battery": "Other",
}

BATTERY_CONDITIONS = ["Normal", "Swollen", "Overheating", "Leaking", "Unknown"]
HAZARDOUS_BATTERY_CONDITIONS = {"Swollen", "Overheating", "Leaking"}
DAMAGE_LEVELS = ["None", "Minor", "Moderate", "Major"]

PATHWAYS = {
    "Repair": {
        "title": "Repair",
        "icon": "fact_check",
        "tone": "green",
        "color": "#22A06B",
        "description": "Keep the device in use with a targeted repair and extend its working life.",
    },
    "Refurbish & Resell": {
        "title": "Refurbish & Resell",
        "icon": "refresh",
        "tone": "blue",
        "color": "#6FA8DC",
        "description": "Professionally refurbish the device so it can be resold or donated.",
    },
    "Harvest Components": {
        "title": "Harvest Components",
        "icon": "cpu",
        "tone": "amber",
        "color": "#E0B45C",
        "description": "Recover useful parts and materials from a device that no longer works.",
    },
    "Recycle": {
        "title": "Recycle",
        "icon": "recycle",
        "tone": "teal",
        "color": "#2FBFA3",
        "description": "Send the device through a verified material recovery route.",
    },
    "Hazardous Handling": {
        "title": "Hazardous Handling",
        "icon": "battery",
        "tone": "coral",
        "color": "#E08A77",
        "description": "Use specialist, battery-safe handling for a potentially hazardous device.",
    },
}

CONDITIONS = {
    "Excellent": {"value_factor": 1.0, "score": 96},
    "Good": {"value_factor": 0.82, "score": 84},
    "Fair": {"value_factor": 0.58, "score": 66},
    "Poor": {"value_factor": 0.34, "score": 46},
    "Non-working": {"value_factor": 0.15, "score": 30},
}

GUIDANCE = {
    "Mobile": [
        "Back up your data and factory reset the device.",
        "Remove the SIM card and any memory cards.",
        "Keep the battery intact and avoid puncturing it.",
    ],
    "Computing": [
        "Back up data and sign out of all accounts.",
        "Remove external drives, dongles and peripherals.",
        "Do not remove an internal battery yourself.",
    ],
    "Accessory": [
        "Bundle cables loosely to avoid damage.",
        "Check for exposed wires before handling.",
        "Keep chargers with their matching cable.",
    ],
    "Display": [
        "Remove the stand and any mounting accessories.",
        "Do not break or pressure the screen panel.",
        "Transport upright with the screen protected.",
    ],
    "Office": [
        "Remove ink and toner cartridges separately.",
        "Delete stored scan and fax logs where possible.",
        "Keep the power cord attached for recycling.",
    ],
    "Appliance": [
        "Empty, clean and dry the appliance first.",
        "Keep the power cord attached to the unit.",
        "Book a pickup for large appliances.",
    ],
    "Hazardous": [
        "Tape the battery terminals before transport.",
        "Store in a cool, non-flammable container.",
        "Never place batteries in household bins.",
    ],
}

REWARDS = [
    {
        "title": "Plant a sapling",
        "description": "Fund a native tree planted with a local community partner.",
        "cost": 200,
        "category": "Impact",
        "stock": 99,
        "icon": "leaf",
    },
    {
        "title": "Bamboo desk organizer",
        "description": "A compact organizer made from reclaimed bamboo.",
        "cost": 450,
        "category": "Home",
        "stock": 12,
        "icon": "package",
    },
    {
        "title": "Recycled fabric tote",
        "description": "Everyday tote woven from recovered textile offcuts.",
        "cost": 500,
        "category": "Lifestyle",
        "stock": 16,
        "icon": "recycle",
    },
    {
        "title": "₹100 green voucher",
        "description": "Use at partner repair cafes and sustainable stores.",
        "cost": 800,
        "category": "Voucher",
        "stock": 25,
        "icon": "gift",
    },
    {
        "title": "Community cleanup sponsor",
        "description": "Sponsor one hour of a neighbourhood e-waste drive.",
        "cost": 1200,
        "category": "Impact",
        "stock": 5,
        "icon": "users",
    },
    {
        "title": "Solar power bank",
        "description": "A rugged 10,000 mAh power bank with solar charging.",
        "cost": 1800,
        "category": "Tech",
        "stock": 3,
        "icon": "zap",
    },
]

BADGES = [
    {
        "name": "Circular Starter",
        "description": "Recycle your first device",
        "icon": "recycle",
        "earned": True,
        "rarity": "Common",
    },
    {
        "name": "Green Guardian",
        "description": "Divert 25 kg of e-waste",
        "icon": "shield",
        "earned": True,
        "rarity": "Rare",
    },
    {
        "name": "Streak Keeper",
        "description": "Maintain a 7-day streak",
        "icon": "zap",
        "earned": True,
        "rarity": "Common",
    },
    {
        "name": "E-Waste Explorer",
        "description": "Visit 5 drop-off points",
        "icon": "map",
        "earned": False,
        "rarity": "Rare",
    },
    {
        "name": "Carbon Cutter",
        "description": "Avoid 500 kg of CO₂",
        "icon": "cloud",
        "earned": False,
        "rarity": "Epic",
    },
    {
        "name": "Community Champion",
        "description": "Refer three friends to ReLoop",
        "icon": "users",
        "earned": False,
        "rarity": "Epic",
    },
    {
        "name": "Rare Earth Hero",
        "description": "Recycle 100 devices",
        "icon": "cpu",
        "earned": False,
        "rarity": "Legendary",
    },
    {
        "name": "Zero Waste Legend",
        "description": "Divert 1,000 kg of e-waste",
        "icon": "trophy",
        "earned": False,
        "rarity": "Legendary",
    },
]

LEADERBOARD = [
    {"rank": 1, "name": "Meera Nair", "points": 3420, "kg": 186},
    {"rank": 2, "name": "Aarav Mehta", "points": 2480, "kg": 142},
    {"rank": 3, "name": "Rohan Iyer", "points": 2310, "kg": 128},
    {"rank": 4, "name": "Sneha Rao", "points": 2050, "kg": 119},
    {"rank": 5, "name": "Kabir Shah", "points": 1890, "kg": 104},
    {"rank": 6, "name": "Ananya Das", "points": 1640, "kg": 96},
    {"rank": 7, "name": "Vikram Singh", "points": 1420, "kg": 88},
]

REDEMPTION_HISTORY = [
    {"title": "Bamboo desk organizer", "date": "01 Nov 2026", "points": 450, "status": "Delivered"},
    {"title": "Plant a sapling", "date": "18 Oct 2026", "points": 200, "status": "Planted"},
    {"title": "₹100 green voucher", "date": "02 Oct 2026", "points": 800, "status": "Used"},
]

RECYCLING_HISTORY = [
    {
        "date": "05 Nov 2026",
        "device": "Smartphone",
        "detail": "Samsung Galaxy S21",
        "partner": "GreenLoop Recycling Hub",
        "status": "Completed",
        "weight_kg": 0.18,
        "co2_kg": 22.4,
        "points": 180,
        "score": 92,
        "icon": "phone",
        "tone": "green",
    },
    {
        "date": "02 Nov 2026",
        "device": "Laptop",
        "detail": "Dell XPS 13",
        "partner": "TechTakeback Centre",
        "status": "Completed",
        "weight_kg": 2.1,
        "co2_kg": 145.0,
        "points": 320,
        "score": 88,
        "icon": "laptop",
        "tone": "green",
    },
    {
        "date": "28 Oct 2026",
        "device": "Monitor",
        "detail": "LG 24-inch display",
        "partner": "BlueGreen Recyclers",
        "status": "Completed",
        "weight_kg": 4.2,
        "co2_kg": 210.0,
        "points": 240,
        "score": 84,
        "icon": "monitor",
        "tone": "green",
    },
    {
        "date": "24 Oct 2026",
        "device": "Charger & cables",
        "detail": "Anker cable bundle",
        "partner": "Cirqle Collection Kiosk",
        "status": "Completed",
        "weight_kg": 0.12,
        "co2_kg": 4.2,
        "points": 60,
        "score": 90,
        "icon": "zap",
        "tone": "green",
    },
    {
        "date": "18 Oct 2026",
        "device": "Tablet",
        "detail": "Apple iPad Air",
        "partner": "EcoByte Collection Point",
        "status": "Completed",
        "weight_kg": 0.5,
        "co2_kg": 48.0,
        "points": 150,
        "score": 86,
        "icon": "phone",
        "tone": "green",
    },
    {
        "date": "11 Oct 2026",
        "device": "Desktop PC",
        "detail": "HP Pavilion tower",
        "partner": "ReNew Tech Depot",
        "status": "Completed",
        "weight_kg": 7.4,
        "co2_kg": 300.0,
        "points": 420,
        "score": 81,
        "icon": "cpu",
        "tone": "green",
    },
    {
        "date": "07 Nov 2026",
        "device": "Washing machine",
        "detail": "Bosch Serie 6",
        "partner": "Home pickup · Ravi K.",
        "status": "Scheduled",
        "weight_kg": 38.0,
        "co2_kg": 520.0,
        "points": 0,
        "score": 79,
        "icon": "package",
        "tone": "blue",
    },
    {
        "date": "09 Nov 2026",
        "device": "Smartphone",
        "detail": "OnePlus 9",
        "partner": "GreenLoop Recycling Hub",
        "status": "Scheduled",
        "weight_kg": 0.18,
        "co2_kg": 22.4,
        "points": 0,
        "score": 84,
        "icon": "phone",
        "tone": "blue",
    },
    {
        "date": "03 Nov 2026",
        "device": "Printer",
        "detail": "Canon PIXMA",
        "partner": "EarthCare E-Waste Facility",
        "status": "Processing",
        "weight_kg": 6.8,
        "co2_kg": 260.0,
        "points": 0,
        "score": 78,
        "icon": "package",
        "tone": "amber",
    },
    {
        "date": "30 Oct 2026",
        "device": "Battery",
        "detail": "6 lithium-ion cells",
        "partner": "Cirqle Collection Kiosk",
        "status": "Completed",
        "weight_kg": 0.3,
        "co2_kg": 12.0,
        "points": 90,
        "score": 96,
        "icon": "battery",
        "tone": "green",
    },
    {
        "date": "21 Oct 2026",
        "device": "Television",
        "detail": 'Sony Bravia 32"',
        "partner": "TechTakeback Centre",
        "status": "Completed",
        "weight_kg": 9.5,
        "co2_kg": 380.0,
        "points": 300,
        "score": 84,
        "icon": "monitor",
        "tone": "green",
    },
    {
        "date": "14 Oct 2026",
        "device": "Refrigerator",
        "detail": "Samsung 260L",
        "partner": "Home pickup · Ravi K.",
        "status": "Completed",
        "weight_kg": 45.0,
        "co2_kg": 640.0,
        "points": 560,
        "score": 81,
        "icon": "package",
        "tone": "green",
    },
]

def _mock_pathway(entry: dict) -> str:
    if entry["status"] != "Completed":
        return "Recycle"
    device = entry["device"]
    if device == "Battery":
        return "Hazardous Handling"
    if device in {"Smartphone", "Laptop", "Tablet"} and entry.get("score", 0) >= 88:
        return "Repair"
    if device in {"Smartphone", "Laptop", "Tablet", "Monitor", "Desktop PC"}:
        return "Refurbish & Resell"
    return "Recycle"


for _entry in RECYCLING_HISTORY:
    _entry.setdefault("category", DEVICE_CATEGORY_GROUP.get(_entry["device"], "Other"))
    _entry.setdefault("pathway", _mock_pathway(_entry))
    _entry.setdefault("image", None)
    _entry.setdefault("battery_condition", "Normal")
    _entry.setdefault("notes", "Mock recovery record from the ReLoop demo network.")

USER_PREFERENCES = {
    "pickup_reminders": True,
    "impact_digest": True,
    "partner_offers": False,
    "default_mode": "Home pickup",
    "preferred_window": "Weekend afternoons",
    "city": CITY,
    "home_area": "Indiranagar",
    "max_distance_km": 12,
    "default_sort": "Nearest first",
    "location_sharing": True,
    "anonymous_analytics": True,
    "photo_retention": False,
    "share_impact": True,
}

PATHWAY_IMPACT = [
    {"pathway": "Repair", "devices": 18, "weight_kg": 12.4, "co2_kg": 212.0},
    {"pathway": "Refurbish & Resell", "devices": 22, "weight_kg": 31.8, "co2_kg": 486.0},
    {"pathway": "Harvest Components", "devices": 11, "weight_kg": 18.6, "co2_kg": 168.0},
    {"pathway": "Recycle", "devices": 14, "weight_kg": 58.2, "co2_kg": 204.0},
    {"pathway": "Hazardous Handling", "devices": 6, "weight_kg": 4.1, "co2_kg": 72.0},
]

IMPACT_EQUIVALENTS = [
    {
        "label": "Tree-years equivalent",
        "value": "139",
        "icon": "leaf",
        "tone": "green",
        "note": "based on CO₂ avoided",
    },
    {
        "label": "Smartphones charged",
        "value": "28,900",
        "icon": "zap",
        "tone": "amber",
        "note": "energy saved from recovery",
    },
    {
        "label": "Landfill space saved",
        "value": "1.8 m³",
        "icon": "package",
        "tone": "blue",
        "note": "volume diverted from landfill",
    },
]

INSIGHTS = [
    {
        "title": "Smartphones lead the mix",
        "body": "They make up 34% of volume but 41% of total recoverable material value.",
        "icon": "phone",
        "tone": "green",
    },
    {
        "title": "Route pickups to Hebbal",
        "body": "BlueGreen Recyclers is at 81% capacity, while Whitefield is at 63%.",
        "icon": "truck",
        "tone": "amber",
    },
    {
        "title": "Weekends win",
        "body": "Saturday drop-offs are 2.3× more popular than weekday visits.",
        "icon": "calendar",
        "tone": "blue",
    },
    {
        "title": "Copper recovery is climbing",
        "body": "Recovered copper is up 18% quarter over quarter across partner hubs.",
        "icon": "recycle",
        "tone": "purple",
    },
]

ROADMAP = [
    {
        "period": "Section 1",
        "title": "Frontend foundation",
        "body": "Responsive Streamlit app, reusable components, mock flows and data.",
        "state": "done",
    },
    {
        "period": "Section 2",
        "title": "AI vision classifier",
        "body": "Device recognition from photos with confidence scoring and material estimates.",
        "state": "next",
    },
    {
        "period": "Section 3",
        "title": "Routing and partners",
        "body": "Pickup scheduling, partner capacity sync and route optimisation.",
        "state": "planned",
    },
    {
        "period": "Section 4",
        "title": "Impact ledger",
        "body": "Verified chain of custody, rewards marketplace and exportable ESG reports.",
        "state": "planned",
    },
]
