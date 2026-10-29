"""
models/train_models.py
Train Random Forest and boosting models for temperature and precipitation.
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.model_selection import TimeSeriesSplit
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import Input

def train_single_model(model, X_train, y_train):
    model.fit(X_train, y_train)
    return model

def train_lstm_model(X_train, y_train, lookback=10, epochs=30, batch_size=8):
    # Reshape for LSTM: [samples, timesteps, features]
    n_samples = X_train.shape[0]
    n_features = X_train.shape[1]
    if n_samples < lookback:
        return None
    X_seq = []
    y_seq = []
    for i in range(lookback, n_samples):
        X_seq.append(X_train.iloc[i-lookback:i].values)
        y_seq.append(y_train.iloc[i])
    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)
    model = Sequential([
        Input(shape=(lookback, n_features)),
        LSTM(32, activation='tanh'),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
    es = EarlyStopping(patience=5, restore_best_weights=True)
    model.fit(X_seq, y_seq, epochs=epochs, batch_size=batch_size, verbose=0, callbacks=[es])
    return model

def run(features, targets):
    # TimeSeries split
    tscv = TimeSeriesSplit(n_splits=5)
    train_idx, test_idx = list(tscv.split(features))[0]
    X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
    y_train, y_test = targets.iloc[train_idx], targets.iloc[test_idx]

    models = {}
    for var in ['temperature', 'precipitation']:
        y = y_train[var]
        # Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf = train_single_model(rf, X_train, y)
        # XGBoost
        xgb = XGBRegressor(n_estimators=100, random_state=42)
        xgb = train_single_model(xgb, X_train, y)
        # LightGBM
        lgb = LGBMRegressor(n_estimators=100, random_state=42)
        lgb = train_single_model(lgb, X_train, y)
        # CatBoost
        cat = CatBoostRegressor(n_estimators=100, random_state=42, verbose=0)
        cat = train_single_model(cat, X_train, y)
        # LSTM
        lstm = train_lstm_model(X_train, y, lookback=10, epochs=30, batch_size=8)
        models[var] = {
            'rf': rf,
            'xgb': xgb,
            'lgb': lgb,
            'cat': cat,
            'lstm': lstm
        }
        # Save models
        for name, m in models[var].items():
            if name == 'lstm' and m is not None:
                m.save(f'models/{var}_lstm.keras')
            elif name != 'lstm':
                joblib.dump(m, f'models/{var}_{name}.joblib')
    return models, (X_test, y_test)
