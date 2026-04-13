import joblib
from .models import Queue

# Load model once
try:
    model = joblib.load("wait_time_model.pkl")
except:
    model = None


def calculate_wait_time(restaurant):
    queue_count = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # Features for ML
    features = [[
        restaurant.occupied_tables,
        restaurant.total_tables,
        queue_count,
        restaurant.avg_dining_time
    ]]

    # Try ML prediction
    if model:
        try:
            prediction = model.predict(features)[0]
            return max(0, int(prediction))
        except:
            pass

    # Fallback logic (VERY IMPORTANT)
    if restaurant.total_tables == 0:
        return 0

    return int((queue_count / restaurant.total_tables) * restaurant.avg_dining_time)