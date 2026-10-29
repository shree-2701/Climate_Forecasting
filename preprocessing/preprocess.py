"""
preprocessing/preprocess.py
Data loading, cleaning, and preprocessing for climate forecasting.
"""
import os
import pandas as pd
import numpy as np
from glob import glob
from netCDF4 import Dataset

def load_csv_files(data_dir):
    files = glob(os.path.join(data_dir, '*.csv'))
    df_list = [pd.read_csv(f, parse_dates=True, infer_datetime_format=True) for f in files]
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        return df
    return pd.DataFrame()

def load_netcdf_files(data_dir):
    files = glob(os.path.join(data_dir, '*.nc'))
    dfs = []
    for f in files:
        ds = Dataset(f)
        # Example: assumes variables 'temperature', 'precipitation', 'time'
        time = pd.to_datetime(ds.variables['time'][:], unit='D', origin='1970-01-01')
        temp = ds.variables['temperature'][:]
        prec = ds.variables['precipitation'][:]
        df = pd.DataFrame({'date': time, 'temperature': temp, 'precipitation': prec})
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def clean_data(df):
    # Parse date
    if 'date' not in df.columns:
        for col in df.columns:
            if 'date' in col.lower():
                df.rename(columns={col: 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    # Remove duplicates
    df = df.drop_duplicates(subset=['date'])
    # Handle missing values
    df = df.set_index('date')
    for col in ['temperature', 'precipitation']:
        if col in df.columns:
            df[col] = df[col].interpolate(method='time').fillna(method='bfill').fillna(method='ffill')
    # Remove outliers (z-score > 4)
    for col in ['temperature', 'precipitation']:
        if col in df.columns:
            z = np.abs((df[col] - df[col].mean()) / df[col].std())
            df.loc[z > 4, col] = np.nan
            df[col] = df[col].interpolate(method='time').fillna(method='bfill').fillna(method='ffill')
    df = df.reset_index()
    return df

def resample_data(df, freq='D'):
    df = df.set_index('date').sort_index()
    df = df.resample(freq).mean().reset_index()
    return df

def run(data_dir='data', freq='D'):
    df_csv = load_csv_files(data_dir)
    df_nc = load_netcdf_files(data_dir)
    df = pd.concat([df_csv, df_nc], ignore_index=True)
    if df.empty:
        raise ValueError('No data found in data directory.')
    df = clean_data(df)
    df = resample_data(df, freq)
    return df
