import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(r"C:\Users\shree\OneDrive\Desktop\FINAL YR PROJECT\Finally_final\climate_featured_data.csv")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime")

df = df.iloc[:720]

df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()

# -----------------------------
# FEATURES & TARGETS
# -----------------------------
X = df.drop(columns=["rainfall_mm", "temperature", "datetime", "season"])
y_rain = df["rainfall_mm"]
y_temp = df["temperature"]

X = X.select_dtypes(include=[np.number])

# -----------------------------
# TRAIN-TEST SPLIT
# -----------------------------
split = int(len(df) * 0.8)

X_train, X_test = X[:split], X[split:]
y_rain_train, y_rain_test = y_rain[:split], y_rain[split:]
y_temp_train, y_temp_test = y_temp[:split], y_temp[split:]

# -----------------------------
# METRICS
# -----------------------------
def metrics(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2

# -----------------------------
# PLOT FUNCTION (LABELED)
# -----------------------------
def plot_results(y_true, y_pred, title, ylabel):
    plt.figure(figsize=(10,4))
    plt.plot(y_true.values, label="Actual", color="blue")
    plt.plot(y_pred, label="Predicted", color="red")

    plt.title(title)
    plt.xlabel("Time Step")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.show()

# =========================================================
# 🔥 1. XGBOOST
# =========================================================
xgb = XGBRegressor(objective="reg:squarederror", n_estimators=100)

xgb.fit(X_train, y_rain_train)
xgb_rain = xgb.predict(X_test)

xgb.fit(X_train, y_temp_train)
xgb_temp = xgb.predict(X_test)

print("\nXGBOOST")
print("Rain:", metrics(y_rain_test, xgb_rain))
print("Temp:", metrics(y_temp_test, xgb_temp))

plot_results(y_rain_test, xgb_rain, "XGBoost Rainfall Prediction", "Rainfall (mm)")
plot_results(y_temp_test, xgb_temp, "XGBoost Temperature Prediction", "Temperature (°C)")

# =========================================================
# ⚡ 2. LIGHTGBM
# =========================================================
lgbm = LGBMRegressor(n_estimators=100)

lgbm.fit(X_train, y_rain_train)
lgbm_rain = lgbm.predict(X_test)

lgbm.fit(X_train, y_temp_train)
lgbm_temp = lgbm.predict(X_test)

print("\nLIGHTGBM")
print("Rain:", metrics(y_rain_test, lgbm_rain))
print("Temp:", metrics(y_temp_test, lgbm_temp))

plot_results(y_rain_test, lgbm_rain, "LightGBM Rainfall Prediction", "Rainfall (mm)")
plot_results(y_temp_test, lgbm_temp, "LightGBM Temperature Prediction", "Temperature (°C)")

# =========================================================
# 🐱 3. CATBOOST
# =========================================================
cat = CatBoostRegressor(verbose=0)

cat.fit(X_train, y_rain_train)
cat_rain = cat.predict(X_test)

cat.fit(X_train, y_temp_train)
cat_temp = cat.predict(X_test)

print("\nCATBOOST")
print("Rain:", metrics(y_rain_test, cat_rain))
print("Temp:", metrics(y_temp_test, cat_temp))

plot_results(y_rain_test, cat_rain, "CatBoost Rainfall Prediction", "Rainfall (mm)")
plot_results(y_temp_test, cat_temp, "CatBoost Temperature Prediction", "Temperature (°C)")

# =========================================================
# 🌿 4. GRADIENT BOOSTING
# =========================================================
gb = GradientBoostingRegressor()

gb.fit(X_train, y_rain_train)
gb_rain = gb.predict(X_test)

gb.fit(X_train, y_temp_train)
gb_temp = gb.predict(X_test)

print("\nGRADIENT BOOSTING")
print("Rain:", metrics(y_rain_test, gb_rain))
print("Temp:", metrics(y_temp_test, gb_temp))

plot_results(y_rain_test, gb_rain, "Gradient Boosting Rainfall Prediction", "Rainfall (mm)")
plot_results(y_temp_test, gb_temp, "Gradient Boosting Temperature Prediction", "Temperature (°C)")