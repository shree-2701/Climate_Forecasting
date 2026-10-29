import pandas as pd
import numpy as np

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(r"C:\Users\shree\OneDrive\Desktop\FINAL YR PROJECT\data\imd_weather_dataset_2015_2019.csv")

print("\nORIGINAL SHAPE:", df.shape)

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------
df.columns = df.columns.str.strip().str.lower()

# Ensure correct expected columns exist
print("\nCOLUMNS IN DATASET:", df.columns)

# -----------------------------
# CREATE DATETIME (STRICTLY USE EXISTING COLUMN)
# -----------------------------
df["datetime"] = pd.to_datetime(df["datetime"])

# Sort by time
df = df.sort_values("datetime")

# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
before = df.shape[0]
df = df.drop_duplicates()
after = df.shape[0]

print("\nDUPLICATES REMOVED:", before - after)

# -----------------------------
# MISSING VALUES CHECK
# -----------------------------
print("\nMISSING VALUES BEFORE:")
print(df.isnull().sum())

# Time-series interpolation
df = df.set_index("datetime")

df["rainfall_mm"] = df["rainfall_mm"].interpolate(method="time")
df["temperature"] = df["temperature"].interpolate(method="time")

# Fill remaining missing values
df = df.ffill().bfill()

df = df.reset_index()

print("\nMISSING VALUES AFTER:")
print(df.isnull().sum())

# -----------------------------
# TYPE SAFETY
# -----------------------------
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)
df["rainfall_mm"] = df["rainfall_mm"].astype(float)
df["temperature"] = df["temperature"].astype(float)

# -----------------------------
# FIX INVALID VALUES
# -----------------------------
df["rainfall_mm"] = df["rainfall_mm"].clip(lower=0)

# -----------------------------
# OUTLIER HANDLING - RAINFALL
# -----------------------------
rain_cap = df["rainfall_mm"].quantile(0.99)
df["rainfall_mm"] = np.where(df["rainfall_mm"] > rain_cap, rain_cap, df["rainfall_mm"])

# -----------------------------
# OUTLIER HANDLING - TEMPERATURE
# -----------------------------
Q1 = df["temperature"].quantile(0.25)
Q3 = df["temperature"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df["temperature"] = np.clip(df["temperature"], lower, upper)

# -----------------------------
# FINAL SORT CHECK
# -----------------------------
df = df.sort_values("datetime")

print("\nFINAL SHAPE:", df.shape)

# -----------------------------
# SAVE CLEANED DATASET
# -----------------------------
df.to_csv("climate_data_cleaned.csv", index=False)

print("\nCLEANING COMPLETED SUCCESSFULLY")
print("Saved as climate_data_cleaned.csv")