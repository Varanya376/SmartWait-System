import pandas as pd
from xgboost import XGBRegressor
import joblib
import numpy as np

# 🔥 Create dummy training data (for now)
data = pd.DataFrame({
    "crowd_level": np.random.randint(1, 6, 200),
    "hour": np.random.randint(10, 23, 200),
    "day": np.random.randint(0, 7, 200),
    "rating": np.random.uniform(3.0, 5.0, 200),
})

# 🎯 Target: wait time (what we predict)
data["wait_time"] = (
    data["crowd_level"] * 5 +
    (data["hour"] - 12) * 1.5 +
    np.random.randint(0, 5, 200)
)

# Features & target
X = data[["crowd_level", "hour", "day", "rating"]]
y = data["wait_time"]

# 🔥 Train model
model = XGBRegressor()
model.fit(X, y)

# 💾 Save model
joblib.dump(model, "wait_time_model.pkl")

print("✅ Model trained and saved!")