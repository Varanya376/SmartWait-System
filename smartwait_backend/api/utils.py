import joblib
import os
from django.conf import settings
from .models import Queue
import pandas as pd


# ✅ Load model safely (absolute path)
MODEL_PATH = os.path.join(settings.BASE_DIR, "wait_time_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print("✅ ML model loaded")
except:
    model = None
    print("⚠️ ML model not found, using fallback")


def calculate_wait_time(restaurant):
    queue_count = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # -------------------------------
    # 🤖 ML PREDICTION
    # -------------------------------
    if model:
        try:
            data = pd.DataFrame([{
            "occupied_tables": restaurant.occupied_tables,
            "queue_length": queue_count,
            "total_tables": restaurant.total_tables
            }])

            prediction = model.predict(data)[0]

            print("ML Prediction:", prediction)  

            # ✅ safety bounds
            prediction = max(1, min(int(prediction), 120))

            return prediction

        except Exception as e:
            print("ML error:", e)

    # -------------------------------
    # 🔁 FALLBACK LOGIC (IMPROVED)
    # -------------------------------
    if restaurant.total_tables == 0:
        return 0

    # how full restaurant is
    occupancy_ratio = restaurant.occupied_tables / restaurant.total_tables

    # base wait from queue
    base_wait = queue_count * (
        restaurant.avg_dining_time / max(1, restaurant.total_tables)
    )

    # adjust by occupancy
    wait_time = base_wait * (1 + occupancy_ratio)

    return max(1, int(wait_time))