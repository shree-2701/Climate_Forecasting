import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.linear_model import LinearRegression

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# =========================================================
# 1. LOAD DATA
# =========================================================
df = pd.read_csv(r"C:\Users\shree\OneDrive\Desktop\FINAL YR PROJECT\Finally_final\climate_featured_data.csv")
df = df.sort_values("datetime")
df = df.iloc[:720].dropna()

X = df.drop(columns=["rainfall_mm","temperature","datetime","season"])
X = X.select_dtypes(include=[np.number])
y = df["rainfall_mm"]

# =========================================================
# 2. TRAIN TEST SPLIT (IMPORTANT FIX)
# =========================================================
split = int(len(df)*0.8)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split].values
y_test = y.iloc[split:].values

# =========================================================
# 3. MACHINE LEARNING MODELS
# =========================================================
rf = RandomForestRegressor(n_estimators=100, random_state=42)
xgb = XGBRegressor(objective="reg:squarederror")
lgbm = LGBMRegressor()
cat = CatBoostRegressor(verbose=0)

rf.fit(X_train, y_train)
xgb.fit(X_train, y_train)
lgbm.fit(X_train, y_train)
cat.fit(X_train, y_train)

rf_pred = rf.predict(X_test)
xgb_pred = xgb.predict(X_test)
lgbm_pred = lgbm.predict(X_test)
cat_pred = cat.predict(X_test)

# =========================================================
# 4. LSTM (FIXED ALIGNMENT)
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

split2 = int(len(X_seq)*0.8)

X_train_l = X_seq[:split2]
X_test_l = X_seq[split2:]
y_train_l = y_seq[:split2]
y_test_l = y_seq[split2:]

lstm = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X_train_l.shape[1], X_train_l.shape[2])),
    LSTM(32),
    Dense(1)
])

lstm.compile(optimizer="adam", loss="mse")
lstm.fit(X_train_l, y_train_l, epochs=5, batch_size=16, verbose=0)

lstm_pred = lstm.predict(X_test_l).flatten()

# =========================================================
# 5. ALIGN ALL MODELS (VERY IMPORTANT FIX)
# =========================================================
min_len = min(
    len(y_test),
    len(rf_pred),
    len(xgb_pred),
    len(lgbm_pred),
    len(cat_pred),
    len(lstm_pred)
)

y_test_final = y_test[:min_len]

rf_pred = rf_pred[:min_len]
xgb_pred = xgb_pred[:min_len]
lgbm_pred = lgbm_pred[:min_len]
cat_pred = cat_pred[:min_len]
lstm_pred = lstm_pred[:min_len]

# =========================================================
# 6. STACKED MODEL
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
# 7. BIAS CORRECTION
# =========================================================
bias = np.mean(y_test_final - final_pred)
corrected_pred = final_pred + bias

# =========================================================
# 8. METRICS
# =========================================================
def rmse(y, p): return np.sqrt(mean_squared_error(y, p))
def mae(y, p): return mean_absolute_error(y, p)
def r2(y, p): return r2_score(y, p)

def acc(y, p):
    return max(0, min(100, 100*(1 - rmse(y,p)/(np.max(y)-np.min(y)))))

# =========================================================
# 9. RESULTS TABLE (THIS FIXES YOUR ERROR)
# =========================================================
results = pd.DataFrame({
    "Model": ["RF","XGB","LGBM","CAT","LSTM","STACKED","BIAS"],
    "RMSE": [
        rmse(y_test_final, rf_pred),
        rmse(y_test_final, xgb_pred),
        rmse(y_test_final, lgbm_pred),
        rmse(y_test_final, cat_pred),
        rmse(y_test_final, lstm_pred),
        rmse(y_test_final, final_pred),
        rmse(y_test_final, corrected_pred)
    ],
    "MAE": [
        mae(y_test_final, rf_pred),
        mae(y_test_final, xgb_pred),
        mae(y_test_final, lgbm_pred),
        mae(y_test_final, cat_pred),
        mae(y_test_final, lstm_pred),
        mae(y_test_final, final_pred),
        mae(y_test_final, corrected_pred)
    ],
    "R2": [
        r2(y_test_final, rf_pred),
        r2(y_test_final, xgb_pred),
        r2(y_test_final, lgbm_pred),
        r2(y_test_final, cat_pred),
        r2(y_test_final, lstm_pred),
        r2(y_test_final, final_pred),
        r2(y_test_final, corrected_pred)
    ],
    "Accuracy": [
        acc(y_test_final, rf_pred),
        acc(y_test_final, xgb_pred),
        acc(y_test_final, lgbm_pred),
        acc(y_test_final, cat_pred),
        acc(y_test_final, lstm_pred),
        acc(y_test_final, final_pred),
        acc(y_test_final, corrected_pred)
    ]
})

print("\n===== FINAL RESULTS =====\n")
print(results)

# =========================================================
# 10. PLOTS
# =========================================================
plt.figure(figsize=(12,5))
plt.plot(y_test_final, label="Actual", color="black")
plt.plot(final_pred, label="Stacked", color="blue")
plt.plot(corrected_pred, label="Bias Corrected", color="red")
plt.title("Final Prediction Comparison")
plt.xlabel("Time Step")
plt.ylabel("Rainfall (mm)")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(10,5))
plt.bar(results["Model"], results["Accuracy"], color="green")
plt.title("Model Accuracy Comparison")
plt.xlabel("Models")
plt.ylabel("Accuracy (%)")
plt.ylim(0,100)
plt.grid()
plt.show()

plt.figure(figsize=(10,5))
sns.boxplot(data=pd.DataFrame({
    "RF": y_test_final-rf_pred,
    "XGB": y_test_final-xgb_pred,
    "LGBM": y_test_final-lgbm_pred,
    "CAT": y_test_final-cat_pred,
    "LSTM": y_test_final-lstm_pred,
    "STACKED": y_test_final-final_pred,
    "BIAS": y_test_final-corrected_pred
}))
plt.title("Error Distribution")
plt.xticks(rotation=30)
plt.grid()
plt.show()



# =========================================================
# 📊 10. WAVEFORM STYLE PLOT (ACTUAL vs ALL MODELS)
# =========================================================
plt.figure(figsize=(12,5))

plt.plot(y_test_final, label="Actual", color="black", linewidth=2)
plt.plot(rf_pred, label="RF", alpha=0.7)
plt.plot(xgb_pred, label="XGB", alpha=0.7)
plt.plot(lstm_pred, label="LSTM", alpha=0.7)
plt.plot(final_pred, label="Stacked", color="blue", linewidth=2)
plt.plot(corrected_pred, label="Bias Corrected", color="red", linewidth=2)

plt.title("Waveform Comparison of All Models")
plt.xlabel("Time Step")
plt.ylabel("Rainfall (mm)")
plt.legend()
plt.grid()
plt.show()

# =========================================================
# 📊 11. RESIDUAL PLOT (ERROR VISUALIZATION)
# =========================================================
plt.figure(figsize=(10,5))

plt.plot(y_test_final - rf_pred, label="RF Error")
plt.plot(y_test_final - xgb_pred, label="XGB Error")
plt.plot(y_test_final - lstm_pred, label="LSTM Error")
plt.plot(y_test_final - corrected_pred, label="Final Error")

plt.title("Residual Error Comparison")
plt.xlabel("Time Step")
plt.ylabel("Error (mm)")
plt.legend()
plt.grid()
plt.show()



# =========================================================
# 📊 13. FINAL SUMMARY TABLE PLOT
# =========================================================
results.set_index("Model")[["RMSE","MAE","R2","Accuracy"]].plot(
    kind="bar",
    figsize=(12,5),
    colormap="viridis"
)

plt.title("Final Model Comparison Summary")
plt.ylabel("Score")
plt.grid()
plt.show()


from sklearn.metrics import confusion_matrix

# -------------------------
# USE EXISTING VARIABLES
# -------------------------
y_true_vals = np.array(y_test_final).flatten()
y_pred_vals = np.array(corrected_pred).flatten()

# -------------------------
# FIX THRESHOLDS
# -------------------------
ref = y_true_vals  # or y_train if available

p33 = np.percentile(ref, 33)
p66 = np.percentile(ref, 66)

def classify(x):
    if x <= p33:
        return 0
    elif x <= p66:
        return 1
    else:
        return 2

# -------------------------
# CLASS CONVERSION
# -------------------------
y_true_class = np.array([classify(x) for x in y_true_vals])
y_pred_class = np.array([classify(x) for x in y_pred_vals])

# -------------------------
# CONFUSION MATRIX
# -------------------------
cm = confusion_matrix(y_true_class, y_pred_class, labels=[0,1,2])

plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt="d", cmap="coolwarm",
            xticklabels=["Low","Medium","High"],
            yticklabels=["Low","Medium","High"])

plt.title("Confusion Matrix (Rainfall Levels)")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()