"""
features/feature_engineering.py
Feature engineering for climate forecasting.
"""
import pandas as pd
import numpy as np

def add_season_label(df):
    # Define seasons (example: India)
    def season_of_month(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Summer'
        elif month in [6, 7, 8, 9]:
            return 'Monsoon'
        else:
            return 'Post-Monsoon'
    df['month'] = df['date'].dt.month
    df['season'] = df['month'].apply(season_of_month)
    df['year'] = df['date'].dt.year
    return df

def add_lag_features(df, lags=[1, 7, 30]):
    for col in ['temperature', 'precipitation']:
        for lag in lags:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)
    return df

def add_rolling_features(df, windows=[7, 30]):
    for col in ['temperature', 'precipitation']:
        for w in windows:
            df[f'{col}_rollmean{w}'] = df[col].rolling(window=w, min_periods=1).mean()
            df[f'{col}_rollstd{w}'] = df[col].rolling(window=w, min_periods=1).std().fillna(0)
    return df

def run(df):
    df = add_season_label(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    # Drop rows with NA only for numeric columns
    numeric_cols = [col for col in df.columns if col not in ['date', 'season']]
    df = df.dropna(subset=numeric_cols).reset_index(drop=True)
    # Exclude non-numeric columns from features
    features = df.drop(columns=['date', 'season'])
    targets = df[['temperature', 'precipitation']]
    return features, targets, df
