import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from api.models import Prediction

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def train():
    data = Prediction.objects.all().values()
    df = pd.DataFrame(data)

    if len(df) < 10:
        print("❌ Not enough data")
        return

    print(f"📊 Training on {len(df)} records")

    # -------------------------------
    # 🧹 CLEAN DATA (CRITICAL FIX)
    # -------------------------------
    df = df[["occupied_tables", "queue_length", "total_tables", "wait_time"]]

    # remove bad values
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # remove unrealistic values
    df = df[
        (df["total_tables"] > 0) &
        (df["occupied_tables"] >= 0) &
        (df["wait_time"] > 0) &
        (df["wait_time"] < 180)
    ]

    if len(df) < 10:
        print("❌ Data too dirty after cleaning")
        return

    # -------------------------------
    # 🎯 FEATURES
    # -------------------------------
    df["occupancy_rate"] = df["occupied_tables"] / df["total_tables"]
    df["queue_pressure"] = df["queue_length"] / (df["total_tables"] + 1)

    X = df[[
    "occupied_tables",
    "queue_length",
    "total_tables",
    "occupancy_rate",
    "queue_pressure"
]]
    y = df["wait_time"]

    # -------------------------------
    # 🧠 TRAIN / TEST SPLIT
    # -------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # -------------------------------
    # 🌳 MODEL
    # -------------------------------
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42
    )

    model.fit(X_train, y_train)

    # -------------------------------
    # 📈 EVALUATION
    # -------------------------------
    score = model.score(X_test, y_test)
    print(f"📈 Model R² Score: {round(score, 3)}")

    # -------------------------------
    # 💾 SAVE MODEL
    # -------------------------------
    joblib.dump(model, MODEL_PATH)

    print("✅ Model trained & saved successfully")