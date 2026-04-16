import joblib
import os
from .models import Queue, Table
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

model = None

try:
    model = joblib.load(MODEL_PATH)
    print("✅ ML model loaded successfully")
except:
    print("⚠️ ML model not found, falling back to rule-based")


# -------------------------------
# FEATURE BUILDER (SINGLE SOURCE)
# -------------------------------
def build_features(restaurant):
    total_tables = Table.objects.filter(
        restaurant=restaurant
    ).count()

    occupied_tables = Table.objects.filter(
        restaurant=restaurant,
        status__in=["OCCUPIED", "RESERVED"]
    ).count()

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    avg_dining_time = restaurant.avg_dining_time

    return {
        "occupied_tables": occupied_tables,
        "queue_length": queue_length,
        "total_tables": total_tables,
        "avg_dining_time": avg_dining_time
    }


# -------------------------------
# MAIN WAIT TIME FUNCTION (ML + RULE HYBRID)
# -------------------------------
def calculate_wait_time(restaurant):
    features = build_features(restaurant)

    occupied_tables = features["occupied_tables"]
    queue_count = features["queue_length"]
    total_tables = features["total_tables"]
    avg_time = features["avg_dining_time"]

    if restaurant.total_tables == 0:
        return 0

    print("DEBUG → occupied:", occupied_tables, "total:", total_tables)

    # -------------------------------
    # 🤖 ML PREDICTION
    # -------------------------------
    if model:
        try:
            # IMPORTANT: match training features EXACTLY
            data = pd.DataFrame([{
                "occupied_tables": occupied_tables,
                "queue_length": queue_count,
                "total_tables": total_tables,
                "occupancy_rate": occupied_tables / max(1, total_tables),
                "queue_pressure": queue_count / max(1, total_tables)
        }])

            ml_pred = model.predict(data)[0]
            # Only boost if prediction is too small
            ml_pred = max(5, ml_pred)

            print("🤖 ML Prediction:", ml_pred)

            ml_pred = max(1, min(int(ml_pred), 120))

            # -------------------------------
            # 🔥 HYBRID LOGIC
            # -------------------------------
            # FULL RESTAURANT
            if occupied_tables >= total_tables:
                print("🔥 FULL RESTAURANT")
                return max(ml_pred, avg_time)

            # HIGH LOAD
            if occupied_tables >= total_tables * 0.8:
                print("⚠️ HIGH LOAD")
                return max(ml_pred, int(avg_time / 2))

           # 🔥 RULE-BASED BASELINE
            free_tables = total_tables - occupied_tables

            if free_tables > 0:
                rule_based = queue_count * (avg_time / total_tables)
            else:
                rule_based = avg_time + (queue_count * (avg_time / total_tables))

            # 🤖 HYBRID MODEL (AI + LOGIC)
            final_prediction = (0.6 * ml_pred) + (0.4 * rule_based)

            if queue_count > 0:
                return max(5, int(final_prediction))  # 🔥 never drop below 5
            else:
                return 0

        except Exception as e:
            print("❌ ML ERROR:", e)

    # -------------------------------
    # 🔁 FALLBACK (RULE-BASED)
    # -------------------------------
    # -------------------------------
# 🔁 FALLBACK (RULE-BASED)
# -------------------------------
    if total_tables == 0:
        return 0

    free_tables = total_tables - occupied_tables

    if free_tables > 0:
        rule_based = (queue_count / max(1, free_tables)) * avg_time
    else:
        rule_based = avg_time + (queue_count * (avg_time / total_tables))

    if queue_count > 0:
        return max(5, int(rule_based))
    else:
        return 0