import joblib
import os
from .models import Queue, Table
import pandas as pd
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

model = None

import logging
logger = logging.getLogger(__name__)

try:
    model = joblib.load(MODEL_PATH)
    logger.info("ML model loaded successfully")
except Exception as e:
    model = None
    logger.warning(f"ML model not found: {e}")


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

    used_ml = False  

    occupied_tables = features["occupied_tables"]
    queue_count = features["queue_length"]
    total_tables = features["total_tables"]
    avg_time = features["avg_dining_time"]

    factors = {
        "queue_length": queue_count,
        "occupied_tables": occupied_tables,
        "total_tables": total_tables
    }

    explanation = []

    if queue_count > 10:
         explanation.append("High queue volume")

    if occupied_tables >= total_tables:
            explanation.append("Restaurant is full")

    elif occupied_tables >= total_tables * 0.8:
            explanation.append("Restaurant nearly full")

    if queue_count == 0:
            explanation = ["No waiting queue"]

    if total_tables == 0:
        return {
            "wait_time": 0,
            "used_ml": False,
            "factors": factors,
            "explanation": explanation
        }

    # -------------------------------
    # 🤖 ML PREDICTION
    # -------------------------------
    if model:
        try:
            used_ml = True

            # ⏱ TIME FEATURES
            now = datetime.now()

            data = pd.DataFrame([{
                "occupied_tables": occupied_tables,
                "queue_length": queue_count,
                "total_tables": total_tables,
                "occupancy_rate": occupied_tables / max(1, total_tables),
                "queue_pressure": queue_count / max(1, total_tables),
                "hour": now.hour,
                "day_of_week": now.weekday()
            }])

            ml_pred = model.predict(data)[0]
            ml_pred = max(5, ml_pred)
            ml_pred = max(1, min(int(ml_pred), 120))

            # FULL RESTAURANT
            if occupied_tables >= total_tables:
                return {
                    "wait_time": max(ml_pred, avg_time),
                    "used_ml": used_ml,
                    "factors": factors,
                    "explanation": explanation
                }

            # HIGH LOAD
            if occupied_tables >= total_tables * 0.8:
                return {
                    "wait_time": max(ml_pred, int(avg_time / 2)),
                    "used_ml": used_ml,
                    "factors": factors,
                    "explanation": explanation
                }

            # RULE BASE
            free_tables = total_tables - occupied_tables

            if free_tables > 0:
                rule_based = queue_count * (avg_time / total_tables)
            else:
                rule_based = avg_time + (queue_count * (avg_time / total_tables))

            final_prediction = (0.6 * ml_pred) + (0.4 * rule_based)

            return {
                "wait_time": int(final_prediction) if queue_count > 0 else 0,
                "used_ml": used_ml,
                "factors": factors,
                "explanation": explanation
            }
        except Exception as e:
            logger.error(f"ML ERROR: {e}")
        

    # -------------------------------
    # 🔁 FALLBACK
    # -------------------------------
    free_tables = total_tables - occupied_tables

    if free_tables > 0:
        rule_based = (queue_count / max(1, free_tables)) * avg_time
    else:
        rule_based = avg_time + (queue_count * (avg_time / total_tables))

    return {
        "wait_time": int(rule_based) if queue_count > 0 else 0,
        "used_ml": False,
        "factors": factors,
        "explanation": explanation
    }