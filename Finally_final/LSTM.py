import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

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
# SELECT FEATURES
# -----------------------------
features = df.drop(columns=["rainfall_mm", "temperature", "datetime", "season"])

features = features.select_dtypes(include=[np.number])

target_rain = df["rainfall_mm"].values
target_temp = df["temperature"].values

# -----------------------------
# SCALE DATA (IMPORTANT FOR LSTM)
# -----------------------------
scaler_X = MinMaxScaler()
scaler_y_rain = MinMaxScaler()
scaler_y_temp = MinMaxScaler()

X_scaled = scaler_X.fit_transform(features)
y_rain_scaled = scaler_y_rain.fit_transform(target_rain.reshape(-1,1))
y_temp_scaled = scaler_y_temp.fit_transform(target_temp.reshape(-1,1))

# -----------------------------
# CREATE SEQUENCES
# -----------------------------
def create_sequences(X, y, step=10):
    Xs, ys = [], []
    for i in range(len(X)-step):
        Xs.append(X[i:i+step])
        ys.append(y[i+step])
    return np.array(Xs), np.array(ys)

time_step = 10

X_seq, y_rain_seq = create_sequences(X_scaled, y_rain_scaled, time_step)
_, y_temp_seq = create_sequences(X_scaled, y_temp_scaled, time_step)

# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------
split = int(len(X_seq)*0.8)

X_train, X_test = X_seq[:split], X_seq[split:]
y_rain_train, y_rain_test = y_rain_seq[:split], y_rain_seq[split:]
y_temp_train, y_temp_test = y_temp_seq[:split], y_temp_seq[split:]

# -----------------------------
# BUILD LSTM MODEL
# -----------------------------
def build_lstm():
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(32))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")
    return model

# -----------------------------
# TRAIN FOR RAINFALL
# -----------------------------
model_rain = build_lstm()
model_rain.fit(X_train, y_rain_train, epochs=10, batch_size=16, verbose=1)

rain_pred = model_rain.predict(X_test)

# inverse scale
rain_pred = scaler_y_rain.inverse_transform(rain_pred)
y_rain_true = scaler_y_rain.inverse_transform(y_rain_test)

# -----------------------------
# TRAIN FOR TEMPERATURE
# -----------------------------
model_temp = build_lstm()
model_temp.fit(X_train, y_temp_train, epochs=10, batch_size=16, verbose=1)

temp_pred = model_temp.predict(X_test)

temp_pred = scaler_y_temp.inverse_transform(temp_pred)
y_temp_true = scaler_y_temp.inverse_transform(y_temp_test)

# -----------------------------
# METRICS
# -----------------------------
def metrics(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2

print("\nLSTM RESULTS")
print("Rain:", metrics(y_rain_true, rain_pred))
print("Temp:", metrics(y_temp_true, temp_pred))

# -----------------------------
# PLOTS (LABELED)
# -----------------------------
def plot_lstm(y_true, y_pred, title, ylabel):
    plt.figure(figsize=(10,4))
    plt.plot(y_true, label="Actual", color="blue")
    plt.plot(y_pred, label="Predicted", color="red")

    plt.title(title)
    plt.xlabel("Time Step")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.show()

plot_lstm(y_rain_true, rain_pred, "LSTM Rainfall Prediction", "Rainfall (mm)")
plot_lstm(y_temp_true, temp_pred, "LSTM Temperature Prediction", "Temperature (°C)")