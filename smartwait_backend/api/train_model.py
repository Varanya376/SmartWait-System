import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from api.models import Prediction


def train():
    # ✅ Load REAL data from DB
    data = Prediction.objects.all().values()
    df = pd.DataFrame(data)

    if len(df) < 10:
        print("❌ Not enough real data to train")
        return

    # ✅ Features (MUST match utils.py)
    X = df[["occupied_tables", "queue_length", "total_tables"]]
    y = df["wait_time"]

    # 🔥 Train model
    model = RandomForestRegressor()
    model.fit(X, y)

    # 💾 Save model
    joblib.dump(model, "wait_time_model.pkl")

    print("✅ Model trained on REAL data")


if __name__ == "__main__":
    train()