import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

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
# FEATURES
# -----------------------------
X = df.drop(columns=["rainfall_mm", "temperature", "datetime", "season"])
X = X.select_dtypes(include=[np.number])
y = df["rainfall_mm"]

# -----------------------------
# TRAIN TEST SPLIT (ML MODELS)
# -----------------------------
split = int(len(df)*0.8)

X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# =========================================================
# 🔥 1. RANDOM FOREST
# =========================================================
rf = RandomForestRegressor(n_estimators=100)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)

# =========================================================
# ⚡ 2. BOOSTING MODELS
# =========================================================
xgb = XGBRegressor(objective="reg:squarederror")
lgbm = LGBMRegressor()
cat = CatBoostRegressor(verbose=0)

xgb.fit(X_train, y_train)
lgbm.fit(X_train, y_train)
cat.fit(X_train, y_train)

xgb_pred = xgb.predict(X_test)
lgbm_pred = lgbm.predict(X_test)
cat_pred = cat.predict(X_test)

# =========================================================
# 🧠 3. LSTM (SEQUENTIAL PREP)
# =========================================================
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

def create_seq(X, y, step=10):
    Xs, ys = [], []
    for i in range(len(X)-step):
        Xs.append(X[i:i+step])
        ys.append(y[i+step])
    return np.array(Xs), np.array(ys)

X_seq, y_seq = create_seq(X_scaled, y.values, 10)

split_l = int(len(X_seq)*0.8)

X_train_l, X_test_l = X_seq[:split_l], X_seq[split_l:]
y_train_l, y_test_l = y_seq[:split_l], y_seq[split_l:]

model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X_train_l.shape[1], X_train_l.shape[2])))
model.add(LSTM(32))
model.add(Dense(1))

model.compile(optimizer="adam", loss="mse")
model.fit(X_train_l, y_train_l, epochs=5, batch_size=16, verbose=0)

lstm_pred = model.predict(X_test_l).flatten()

# =========================================================
# 🧠 ALIGN DATA FOR STACKING
# =========================================================

min_len = min(len(rf_pred), len(lstm_pred))

rf_pred = rf_pred[:min_len]
xgb_pred = xgb_pred[:min_len]
lgbm_pred = lgbm_pred[:min_len]
cat_pred = cat_pred[:min_len]
lstm_pred = lstm_pred[:min_len]
y_test_final = y_test.values[:min_len]

# =========================================================
# 🧠 STACKED ENSEMBLE (NOW INCLUDES LSTM)
# =========================================================
stack = pd.DataFrame({
    "rf": rf_pred,
    "xgb": xgb_pred,
    "lgbm": lgbm_pred,
    "cat": cat_pred,
    "lstm": lstm_pred
})

meta = LinearRegression()
meta.fit(stack, y_test_final)

final_pred = meta.predict(stack)

# =========================================================
# 📊 METRICS FUNCTION
# =========================================================
def metrics(y_true, y_pred):
    return (
        np.sqrt(mean_squared_error(y_true, y_pred)),
        mean_absolute_error(y_true, y_pred),
        r2_score(y_true, y_pred)
    )

# =========================================================
# 📊 RESULTS TABLE (ALL MODELS INCLUDED)
# =========================================================
results = pd.DataFrame({
    "Model": ["RF","XGB","LGBM","CAT","LSTM","STACK"],
    "RMSE": [
        metrics(y_test_final, rf_pred)[0],
        metrics(y_test_final, xgb_pred)[0],
        metrics(y_test_final, lgbm_pred)[0],
        metrics(y_test_final, cat_pred)[0],
        metrics(y_test_final, lstm_pred)[0],
        metrics(y_test_final, final_pred)[0]
    ],
    "MAE": [
        metrics(y_test_final, rf_pred)[1],
        metrics(y_test_final, xgb_pred)[1],
        metrics(y_test_final, lgbm_pred)[1],
        metrics(y_test_final, cat_pred)[1],
        metrics(y_test_final, lstm_pred)[1],
        metrics(y_test_final, final_pred)[1]
    ],
    "R2": [
        metrics(y_test_final, rf_pred)[2],
        metrics(y_test_final, xgb_pred)[2],
        metrics(y_test_final, lgbm_pred)[2],
        metrics(y_test_final, cat_pred)[2],
        metrics(y_test_final, lstm_pred)[2],
        metrics(y_test_final, final_pred)[2]
    ]
})

print("\nFINAL MODEL COMPARISON TABLE")
print(results)

# =========================================================
# 📈 LINE PLOT
# =========================================================
plt.figure(figsize=(10,4))
plt.plot(y_test_final, label="Actual")
plt.plot(final_pred, label="Stacked + LSTM Prediction")

plt.title("Final Forecast (All Models Combined)")
plt.xlabel("Time Step")
plt.ylabel("Rainfall (mm)")
plt.legend()
plt.grid()
plt.show()

# =========================================================
# 📊 BOX PLOT (ERRORS)
# =========================================================
errors = pd.DataFrame({
    "RF": y_test_final - rf_pred,
    "XGB": y_test_final - xgb_pred,
    "LGBM": y_test_final - lgbm_pred,
    "CAT": y_test_final - cat_pred,
    "LSTM": y_test_final - lstm_pred,
    "STACK": y_test_final - final_pred
})

plt.figure(figsize=(10,5))
sns.boxplot(data=errors)
plt.title("Model Error Distribution")
plt.ylabel("Error (mm)")
plt.grid()
plt.show()

# =========================================================
# 📊 BAR PLOT
# =========================================================
results.set_index("Model")[["RMSE","MAE"]].plot(kind="bar", figsize=(10,4))
plt.title("Model Performance Comparison")
plt.ylabel("Error")
plt.grid()
plt.show()

from sklearn.metrics import confusion_matrix

# -----------------------------
# CLASSIFICATION FUNCTION
# -----------------------------
def classify_rain(x, ref):
    if x < np.percentile(ref, 33):
        return 0   # Low
    elif x < np.percentile(ref, 66):
        return 1   # Medium
    else:
        return 2   # High

# -----------------------------
# ACTUAL vs PREDICTED (STACKED MODEL)
# -----------------------------
y_true_class = pd.Series(y_test_final).apply(lambda x: classify_rain(x, y_test_final))
y_pred_class = pd.Series(final_pred).apply(lambda x: classify_rain(x, y_test_final))

# -----------------------------
# CONFUSION MATRIX
# -----------------------------
cm = confusion_matrix(y_true_class, y_pred_class)

# -----------------------------
# PLOT
# -----------------------------
plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt="d", cmap="coolwarm")

plt.title("Final Stacked + LSTM Model Confusion Matrix")
plt.xlabel("Predicted (Low / Medium / High)")
plt.ylabel("Actual (Low / Medium / High)")
plt.show()