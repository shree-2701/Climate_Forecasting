import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, confusion_matrix

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(r"C:\Users\shree\OneDrive\Desktop\FINAL YR PROJECT\Finally_final\climate_featured_data.csv")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime")

# Data subset (kept implicit)
df = df.iloc[:720]

# -----------------------------
# FEATURES & TARGETS
# -----------------------------
X = df.drop(columns=["rainfall_mm", "temperature", "datetime", "season"])
y_rain = df["rainfall_mm"]
y_temp = df["temperature"]

# -----------------------------
# TRAIN-TEST SPLIT
# -----------------------------
split = int(len(df) * 0.8)

X_train, X_test = X[:split], X[split:]
y_rain_train, y_rain_test = y_rain[:split], y_rain[split:]
y_temp_train, y_temp_test = y_temp[:split], y_temp[split:]

# -----------------------------
# MODEL
# -----------------------------
rf = RandomForestRegressor(n_estimators=100, random_state=42)

rf.fit(X_train, y_rain_train)
rain_pred = rf.predict(X_test)

rf.fit(X_train, y_temp_train)
temp_pred = rf.predict(X_test)

# -----------------------------
# METRICS
# -----------------------------
def metrics(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2

print("\nRANDOM FOREST RESULTS")
print("Rainfall:", metrics(y_rain_test, rain_pred))
print("Temperature:", metrics(y_temp_test, temp_pred))

# -----------------------------
# WAVEFORM - RAINFALL
# -----------------------------
plt.figure(figsize=(10,4))
plt.plot(y_rain_test.values, label="Actual", color="blue")
plt.plot(rain_pred, label="Predicted", color="red")
plt.title("Random Forest - Rainfall Prediction")
plt.xlabel("Time Step")
plt.ylabel("Rainfall")
plt.legend()
plt.show()

# -----------------------------
# WAVEFORM - TEMPERATURE
# -----------------------------
plt.figure(figsize=(10,4))
plt.plot(y_temp_test.values, label="Actual", color="green")
plt.plot(temp_pred, label="Predicted", color="orange")
plt.title("Random Forest - Temperature Prediction")
plt.xlabel("Time Step")
plt.ylabel("Temperature")
plt.legend()
plt.show()

# -----------------------------
# ERROR DISTRIBUTION
# -----------------------------
rain_error = y_rain_test.values - rain_pred

plt.figure(figsize=(6,4))
sns.histplot(rain_error, kde=True, color="purple")
plt.title("Rainfall Error Distribution")
plt.xlabel("Error")
plt.show()

# -----------------------------
# CONFUSION MATRIX (RAIN LEVELS)
# -----------------------------
def classify(x, ref):
    if x < np.percentile(ref, 33):
        return 0
    elif x < np.percentile(ref, 66):
        return 1
    else:
        return 2

y_true_class = y_rain_test.apply(lambda x: classify(x, y_rain_test))
y_pred_class = pd.Series(rain_pred).apply(lambda x: classify(x, y_rain_test))

cm = confusion_matrix(y_true_class, y_pred_class)

plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, cmap="coolwarm", fmt="d")
plt.title("Random Forest - Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()