import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# LOAD CLEANED DATA
# -----------------------------
df = pd.read_csv("climate_data_cleaned.csv")

# Ensure datetime format
df["datetime"] = pd.to_datetime(df["datetime"])

df = df.sort_values("datetime")

print("\nDATA LOADED")
print(df.head())

# -----------------------------
# BASIC INFO
# -----------------------------
print("\nSHAPE:", df.shape)
print("\nINFO:")
print(df.info())

print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDUPLICATES:", df.duplicated().sum())

# -----------------------------
# SUMMARY STATISTICS
# -----------------------------
print("\nSTATISTICS:")
print(df[["temperature", "rainfall_mm"]].describe())

# -----------------------------
# TIME FEATURES (for analysis only)
# -----------------------------
df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.month

# -----------------------------
# MONTHLY AVERAGE RAINFALL
# -----------------------------
monthly_rain = df.groupby("month")["rainfall_mm"].mean()

plt.figure(figsize=(8,4))
sns.barplot(x=monthly_rain.index, y=monthly_rain.values, color="blue")
plt.title("Monthly Average Rainfall")
plt.xlabel("Month")
plt.ylabel("Rainfall (mm)")
plt.show()

# -----------------------------
# MONTHLY AVERAGE TEMPERATURE
# -----------------------------
monthly_temp = df.groupby("month")["temperature"].mean()

plt.figure(figsize=(8,4))
sns.barplot(x=monthly_temp.index, y=monthly_temp.values, color="red")
plt.title("Monthly Average Temperature")
plt.xlabel("Month")
plt.ylabel("Temperature (°C)")
plt.show()

# -----------------------------
# RAINFALL OVER TIME
# -----------------------------
plt.figure(figsize=(12,5))
plt.plot(df["datetime"], df["rainfall_mm"], color="blue")
plt.title("Rainfall Over Time")
plt.xlabel("Time")
plt.ylabel("Rainfall (mm)")
plt.tight_layout()
plt.show()

# -----------------------------
# TEMPERATURE OVER TIME
# -----------------------------
plt.figure(figsize=(12,5))
plt.plot(df["datetime"], df["temperature"], color="red")
plt.title("Temperature Over Time")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.tight_layout()
plt.show()

# -----------------------------
# DISTRIBUTION PLOTS
# -----------------------------
plt.figure(figsize=(8,4))
sns.histplot(df["rainfall_mm"], bins=50, kde=True)
plt.title("Rainfall Distribution")
plt.show()

plt.figure(figsize=(8,4))
sns.histplot(df["temperature"], bins=50, kde=True, color="orange")
plt.title("Temperature Distribution")
plt.show()

# -----------------------------
# CORRELATION HEATMAP
# -----------------------------
plt.figure(figsize=(5,4))
sns.heatmap(df[["rainfall_mm", "temperature"]].corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Matrix")
plt.show()

# -----------------------------
# BOX PLOT (OUTLIERS CHECK)
# -----------------------------
plt.figure(figsize=(8,4))
sns.boxplot(data=df[["rainfall_mm", "temperature"]])
plt.title("Outlier Check")
plt.show()

# -----------------------------
# INSIGHTS
# -----------------------------
print("\nEDA COMPLETED")
print("Next step: Feature Engineering (lags + rolling + seasonality)")