from .models import Restaurant

def seed_restaurants():
    if Restaurant.objects.exists():
        print("⚠️ Restaurants already exist. Skipping seeding.")
        return

    restaurants = [
    {"name": "Soho Bites", "category": "american", "capacity": 50, "total_tables": 10, "lat": 51.5136, "lng": -0.1365},
    {"name": "Notting Hill Café", "category": "american", "capacity": 40, "total_tables": 8, "lat": 51.5090, "lng": -0.1960},
    {"name": "Camden BBQ", "category": "american", "capacity": 60, "total_tables": 12, "lat": 51.5416, "lng": -0.1420},
    {"name": "Hammersmith Dine", "category": "mexican", "capacity": 45, "total_tables": 9, "lat": 51.4927, "lng": -0.2230},
    {"name": "Shoreditch Sushi", "category": "asian", "capacity": 35, "total_tables": 7, "lat": 51.5255, "lng": -0.0754},
    {"name": "Mayfair Italiano", "category": "italian", "capacity": 70, "total_tables": 14, "lat": 51.5116, "lng": -0.1440},
    {"name": "Kensington Spice", "category": "indian", "capacity": 55, "total_tables": 11, "lat": 51.5009, "lng": -0.1926},
    {"name": "Covent Garden Eats", "category": "british", "capacity": 50, "total_tables": 10, "lat": 51.5117, "lng": -0.1230},
    {"name": "Canary Wharf Grill", "category": "american", "capacity": 65, "total_tables": 13, "lat": 51.5054, "lng": -0.0235},
    {"name": "Greenwich Bistro", "category": "french", "capacity": 30, "total_tables": 6, "lat": 51.4826, "lng": 0.0077},
]

    for r in restaurants:
        Restaurant.objects.create(
            name=r["name"],
            category=r["category"],
            capacity=r["capacity"],
            total_tables=r["total_tables"],
            occupied_tables=0,
            lat=r["lat"],
            lng=r["lng"]
        )

    print("✅ 10 London restaurants seeded successfully!")