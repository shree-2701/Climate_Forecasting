"""
evaluation/evaluate.py
Evaluation metrics for climate forecasting models.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
import joblib
from tensorflow.keras.models import load_model
import os

def compute_metrics(y_true, y_pred):
    return {
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'MAE': mean_absolute_error(y_true, y_pred),
        'R2': r2_score(y_true, y_pred)
    }

def compute_accuracy_from_regression(y_true, y_pred, tolerance=0.1):
    """Convert regression predictions to accuracy using tolerance """
    errors = np.abs(y_true - y_pred)
    max_val = np.max(np.abs(y_true))
    tolerance_val = max_val * tolerance
    accurate = errors <= tolerance_val
    return np.mean(accurate) * 100

def season_wise_metrics(df, y_col, y_pred_col, season_col='season'):
    results = {}
    for season in df[season_col].unique():
        mask = df[season_col] == season
        metrics = compute_metrics(df.loc[mask, y_col], df.loc[mask, y_pred_col])
        results[season] = metrics
    return results

def get_individual_model_predictions(features, targets):
    """Get predictions from individual models"""
    feature_cols = [col for col in features.columns if col not in ['date', 'season']]
    model_predictions = {}
    
    for var in ['temperature', 'precipitation']:
        model_predictions[var] = {}
        
        # Random Forest
        if os.path.exists(f'models/{var}_rf.joblib'):
            rf = joblib.load(f'models/{var}_rf.joblib')
            model_predictions[var]['rf'] = rf.predict(features[feature_cols])
        
        # XGBoost
        if os.path.exists(f'models/{var}_xgb.joblib'):
            xgb = joblib.load(f'models/{var}_xgb.joblib')
            model_predictions[var]['xgb'] = xgb.predict(features[feature_cols])
        
        # LightGBM
        if os.path.exists(f'models/{var}_lgb.joblib'):
            lgb = joblib.load(f'models/{var}_lgb.joblib')
            model_predictions[var]['lgb'] = lgb.predict(features[feature_cols])
        
        # CatBoost
        if os.path.exists(f'models/{var}_cat.joblib'):
            cat = joblib.load(f'models/{var}_cat.joblib')
            model_predictions[var]['cat'] = cat.predict(features[feature_cols])
        
        # LSTM
        if os.path.exists(f'models/{var}_lstm.keras'):
            try:
                lstm = load_model(f'models/{var}_lstm.keras')
                # Reshape for LSTM
                n_samples = features.shape[0]
                n_features = features.shape[1]
                lookback = 10
                X_seq = []
                for i in range(lookback, n_samples):
                    X_seq.append(features.iloc[i-lookback:i].values)
                X_seq = np.array(X_seq)
                lstm_preds = lstm.predict(X_seq, verbose=0)
                # Pad predictions to match length
                model_predictions[var]['lstm'] = np.concatenate([
                    np.full(lookback, np.nan),
                    lstm_preds.flatten()
                ])
            except:
                pass
    
    return model_predictions

def run(models, features, targets, full_df=None):
    results = {}
    df = features.copy()
    feature_cols = [col for col in features.columns if col not in ['date', 'season']]
    
    # Get individual model predictions
    model_predictions = get_individual_model_predictions(features, targets)
    
    for var in ['temperature', 'precipitation']:
        model = models[var]
        y_true = targets[var]
        y_pred = model.predict(features[feature_cols])
        df[f'{var}_pred'] = y_pred
        df[f'{var}_true'] = y_true
        
        # Store individual model predictions
        for model_name, preds in model_predictions.get(var, {}).items():
            df[f'{var}_{model_name}_pred'] = preds
        
        # Compute metrics for stacked model
        # Prefer full_df for season information
        if full_df is not None and 'season' in full_df.columns:
            temp_df = full_df.copy()
            temp_df[f'{var}_pred'] = y_pred
            season_wise = season_wise_metrics(temp_df, var, f'{var}_pred')
        else:
            season_wise = {}
        
        results[var] = {
            'overall': compute_metrics(y_true, y_pred),
            'season_wise': season_wise,
            'individual_models': {}
        }
        
        # Compute metrics for individual models
        for model_name, preds in model_predictions.get(var, {}).items():
            valid_mask = ~np.isnan(preds)
            if np.sum(valid_mask) > 0:
                valid_y_true = y_true[valid_mask]
                valid_preds = preds[valid_mask]
                results[var]['individual_models'][model_name.upper()] = compute_metrics(valid_y_true, valid_preds)
        
        # Add stacked model to individual models
        results[var]['individual_models']['STACKED'] = compute_metrics(y_true, y_pred)
    
    # Create output dataframe with season info if available
    if full_df is not None and 'season' in full_df.columns:
        df = full_df.copy()
        for var in ['temperature', 'precipitation']:
            # Add predictions to the full dataframe
            if f'{var}_pred' in features.columns or True:
                y_true = targets[var]
                model = models[var]
                feature_cols = [col for col in features.columns if col not in ['date', 'season']]
                y_pred = model.predict(features[feature_cols])
                df[f'{var}_pred'] = y_pred
                # Add individual model predictions
                for model_name, preds in model_predictions.get(var, {}).items():
                    df[f'{var}_{model_name}_pred'] = preds
    
    return results, df

