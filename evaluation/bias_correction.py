"""
evaluation/bias_correction.py
Seasonal bias correction for temperature and precipitation forecasts.
"""
import numpy as np
import pandas as pd

def additive_bias_correction(y_true, y_pred, season):
    bias = (y_true - y_pred).groupby(season).mean()
    corrected = y_pred.copy()
    for s in bias.index:
        corrected[season == s] += bias[s]
    return corrected

def distribution_correction(y_true, y_pred, season):
    corrected = y_pred.copy()
    for s in np.unique(season):
        mask = (season == s)
        true = y_true[mask]
        pred = y_pred[mask]
        # Match mean and std
        pred_mean, pred_std = pred.mean(), pred.std()
        true_mean, true_std = true.mean(), true.std()
        if pred_std > 0:
            corrected[mask] = (pred - pred_mean) / pred_std * true_std + true_mean
        else:
            corrected[mask] = true_mean
    return corrected

def run(eval_results, features, targets):
    df = features.copy()
    
    # Handle both old and new format of eval_results
    if isinstance(eval_results, tuple):
        eval_dict = eval_results[0]
        eval_df = eval_results[1]
    else:
        eval_dict = eval_results
        eval_df = features.copy()
    
    # Add original prediction columns 
    for var in ['temperature', 'precipitation']:
        pred_col = f'{var}_pred'
        
        # Get predictions from eval_df if available
        if pred_col in eval_df.columns:
            df[pred_col] = eval_df[pred_col]
        elif f'{var}_pred' in features.columns:
            df[pred_col] = features[f'{var}_pred']
        else:
            continue
            
        y_true = targets[var]
        y_pred = df[pred_col]
        season = features['season']
        
        if var == 'temperature':
            corrected = additive_bias_correction(y_true, y_pred, season)
        else:
            corrected = distribution_correction(y_true, y_pred, season)
        df[f'{var}_corrected'] = corrected
    
    return df
