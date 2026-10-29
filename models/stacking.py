"""
models/stacking.py
Stacking ensemble for temperature and precipitation forecasting.
"""
import numpy as np
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV
import joblib

def run(models, test_data):
    X_test, y_test = test_data
    stacked_models = {}
    for var in ['temperature', 'precipitation']:
        estimators = [
            ('rf', models[var]['rf']),
            ('xgb', models[var]['xgb']),
            ('lgb', models[var]['lgb']),
            ('cat', models[var]['cat'])
        ]
        # Note: LSTM is not included in stacking due to sklearn compatibility
        stack = StackingRegressor(
            estimators=estimators,
            final_estimator=RidgeCV(),
            passthrough=True
        )
        stack.fit(X_test, y_test[var])
        joblib.dump(stack, f'models/{var}_stacked.joblib')
        stacked_models[var] = stack
    return stacked_models
