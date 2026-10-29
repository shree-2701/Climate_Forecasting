import pandas as pd
import numpy as np

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("climate_data_cleaned.csv")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime")

print("\nDATA LOADED:", df.shape)

# -----------------------------
# BASIC TIME FEATURES
# -----------------------------
df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.month
df["hour"] = df["datetime"].dt.hour

# -----------------------------
# SEASON FEATURE
# -----------------------------
def get_season(m):
    if m in [12, 1, 2]:
        return "DJF"
    elif m in [3, 4, 5]:
        return "MAM"
    elif m in [6, 7, 8]:
        return "JJA"
    else:
        return "SON"

df["season"] = df["month"].apply(get_season)

# -----------------------------
# CYCLICAL ENCODING (VERY IMPORTANT)
# -----------------------------
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

# -----------------------------
# SORT FOR TIME FEATURES
# -----------------------------
df = df.sort_values("datetime")

# -----------------------------
# LAG FEATURES (ONLY ESSENTIAL)
# -----------------------------
df["rainfall_lag_1"] = df["rainfall_mm"].shift(1)
df["rainfall_lag_3"] = df["rainfall_mm"].shift(3)

df["temp_lag_1"] = df["temperature"].shift(1)
df["temp_lag_3"] = df["temperature"].shift(3)

# -----------------------------
# ROLLING FEATURES (STABLE SIGNAL)
# -----------------------------
df["rainfall_roll_mean_6"] = df["rainfall_mm"].rolling(6).mean()
df["temp_roll_mean_6"] = df["temperature"].rolling(6).mean()

# -----------------------------
# DROP NA (from lag/rolling)
# -----------------------------
df = df.dropna()

print("\nFINAL FEATURE SET:", df.shape)

# -----------------------------
# SAVE FINAL DATASET
# -----------------------------
df.to_csv("climate_featured_data.csv", index=False)

print("\nFEATURE ENGINEERING COMPLETED (CLEAN VERSION)")