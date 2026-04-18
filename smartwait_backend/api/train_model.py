import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from api.models import Prediction
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging
logger = logging.getLogger(__name__)
from .models import ModelMetrics


MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def train():
    data = Prediction.objects.all().values()
    df = pd.DataFrame(data)

    if len(df) < 10:
        logger.warning("Not enough data")
        return

    logger.info(f"Training on {len(df)} records")

    # -------------------------------
    # 🧹 CLEAN DATA
    # -------------------------------
    df = df[[
        "occupied_tables",
        "queue_length",
        "total_tables",
        "wait_time",
        "created_at"
    ]].copy()

    # 🧠 TIME FEATURES
    df["hour"] = pd.to_datetime(df["created_at"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["created_at"]).dt.dayofweek

    df.drop(columns=["created_at"], inplace=True)

    # remove bad values
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # remove unrealistic values
    df = df[
        (df["total_tables"] > 0) &
        (df["occupied_tables"] >= 0) &
        (df["wait_time"] >= 0) &
        (df["wait_time"] < 180)
    ]

    if len(df) < 10:
        logger.warning("Data too dirty after cleaning")
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
        "queue_pressure",
        "hour",
        "day_of_week"
    ]]

    y = df["wait_time"]

    # -------------------------------
    # 🧠 TRAIN
    # -------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    r2 = model.score(X_test, y_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    logger.info(f"R2 Score: {round(r2, 3)}")
    logger.info(f"MAE: {round(mae, 2)} minutes")
    logger.info(f"RMSE: {round(rmse, 2)} minutes")

    # SAVE METRICS TO DATABASE
    try:
        ModelMetrics.objects.create(
            mae=mae,
            rmse=rmse,
            r2=r2
        )
    except Exception as e:
        logger.error(f"Error saving model metrics: {e}")

    joblib.dump(model, MODEL_PATH)

    logger.info("Model trained & saved successfully")