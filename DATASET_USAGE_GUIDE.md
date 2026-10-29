# IMD Dataset - Practical Usage Guide

## Quick Start

### Loading the Dataset

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('data/imd_weather_dataset_2015_2019.csv')

# Convert datetime column
df['datetime'] = pd.to_datetime(df['datetime'])

# Display basic info
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
```

---

## Data Exploration

### 1. Basic Statistics

```python
# Temperature statistics
print("=== TEMPERATURE STATISTICS ===")
print(df['temperature'].describe())

# Rainfall statistics
print("\n=== RAINFALL STATISTICS ===")
print(df['rainfall_mm'].describe())

# By station (latitude)
print("\n=== TEMPERATURE BY STATION ===")
station_stats = df.groupby('latitude')[['temperature', 'rainfall_mm']].agg({
    'temperature': ['mean', 'std', 'min', 'max'],
    'rainfall_mm': ['mean', 'sum']
})
print(station_stats)
```

### 2. Temporal Patterns

```python
# Extract temporal features
df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['day'] = df['datetime'].dt.day
df['hour'] = df['datetime'].dt.hour
df['dayofyear'] = df['datetime'].dt.dayofyear

# Average daily cycle (all data)
hourly_pattern = df.groupby('hour')['temperature'].mean()
print("Average temperature by hour:")
print(hourly_pattern)

# Average monthly cycle
monthly_pattern = df.groupby('month')['temperature'].mean()
print("\nAverage temperature by month:")
print(monthly_pattern)

# Rainfall by month
monthly_rainfall = df.groupby('month')['rainfall_mm'].sum()
print("\nMonthly rainfall totals:")
print(monthly_rainfall)
```

### 3. Seasonal Analysis

```python
# Define seasons
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Summer'
    elif month in [6, 7, 8, 9]:
        return 'Monsoon'
    else:
        return 'Post-monsoon'

df['season'] = df['month'].apply(get_season)

# Seasonal statistics
seasonal_stats = df.groupby('season').agg({
    'temperature': ['mean', 'std', 'min', 'max'],
    'rainfall_mm': ['mean', 'sum', 'max']
})
print("=== SEASONAL STATISTICS ===")
print(seasonal_stats)
```

---

## Data Preprocessing

### 1. Create Derived Features

```python
# Time-based features
df['day_of_year'] = df['datetime'].dt.dayofyear
df['week_of_year'] = df['datetime'].dt.isocalendar().week
df['quarter'] = df['datetime'].dt.quarter

# Cyclical encoding for month
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

# Cyclical encoding for hour
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# Temperature changes
df['temp_change'] = df.groupby('latitude')['temperature'].diff()
df['temp_rolling_mean'] = df.groupby('latitude')['temperature'].rolling(24).mean().reset_index(0, drop=True)

# Rainfall features
df['rain_flag'] = (df['rainfall_mm'] > 0).astype(int)
df['rain_cumsum'] = df.groupby(['latitude', 'month'])['rainfall_mm'].cumsum()

print("New features created successfully!")
```

### 2. Handle Missing/Outliers

```python
# Check for missing values
print(f"Missing values: {df.isnull().sum().sum()}")

# Identify outliers (temperature)
Q1 = df['temperature'].quantile(0.25)
Q3 = df['temperature'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['temperature'] < Q1 - 1.5*IQR) | (df['temperature'] > Q3 + 1.5*IQR)]
print(f"Temperature outliers: {len(outliers)} ({len(outliers)/len(df)*100:.2f}%)")

# Identify outliers (rainfall)
Q1_rain = df['rainfall_mm'].quantile(0.25)
Q3_rain = df['rainfall_mm'].quantile(0.75)
IQR_rain = Q3_rain - Q1_rain
outliers_rain = df[(df['rainfall_mm'] > Q3_rain + 1.5*IQR_rain)]
print(f"Rainfall outliers (heavy rain): {len(outliers_rain)} events")
```

### 3. Normalize/Scale Features

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Standardization (zero mean, unit variance)
scaler = StandardScaler()
df['temperature_scaled'] = scaler.fit_transform(df[['temperature']])

# Min-Max scaling (0-1)
minmax = MinMaxScaler()
df['rainfall_normalized'] = minmax.fit_transform(df[['rainfall_mm']])

print("Scaled features added!")
```

---

## Analysis Examples

### 1. Extreme Weather Events

```python
# Identify extreme temperatures
extreme_hot = df[df['temperature'] >= df['temperature'].quantile(0.95)]
extreme_cold = df[df['temperature'] <= df['temperature'].quantile(0.05)]

print(f"Extreme hot days (top 5%): {len(extreme_hot)}")
print(f"Extreme cold days (bottom 5%): {len(extreme_cold)}")

# Heavy rainfall events
heavy_rain = df[df['rainfall_mm'] >= 100]
print(f"\nHeavy rainfall events (≥100mm): {len(heavy_rain)}")
print(heavy_rain[['datetime', 'latitude', 'longitude', 'temperature', 'rainfall_mm']].head(10))

# Heatwave detection (3+ consecutive days > 40°C)
df['is_hot'] = df['temperature'] > 40
df['hot_streak'] = (df['is_hot'] != df['is_hot'].shift()).cumsum()
heatwaves = df[df['is_hot']].groupby(['latitude', 'hot_streak']).size()
print(f"\nHeatwave events: {len(heatwaves)}")
```

### 2. Monsoon Analysis

```python
# Monsoon period (June-September)
monsoon_data = df[(df['month'] >= 6) & (df['month'] <= 9)]

print("=== MONSOON STATISTICS (Jun-Sep) ===")
print(f"Total rainfall: {monsoon_data['rainfall_mm'].sum():.0f} mm")
print(f"Average daily rainfall: {monsoon_data.groupby('dayofyear')['rainfall_mm'].sum().mean():.1f} mm")
print(f"Max hourly rainfall: {monsoon_data['rainfall_mm'].max():.1f} mm")

# Monsoon intensity by station
monsoon_by_station = monsoon_data.groupby('latitude').agg({
    'rainfall_mm': ['sum', 'mean', 'max'],
    'temperature': ['mean', 'min', 'max']
})
print("\nMonsoon characteristics by station:")
print(monsoon_by_station)

# Rain days (days with any rainfall)
monsoon_data['rain_day'] = monsoon_data.groupby(['latitude', 'dayofyear'])['rainfall_mm'].transform('sum') > 0
rain_days = monsoon_data.groupby('latitude')['rain_day'].sum() / monsoon_data.groupby('dayofyear').size()
print("\nRain days during monsoon:")
print(rain_days)
```

### 3. Geographic Variations

```python
# Station names and coordinates
stations = {
    13.0827: 'Chennai',
    19.0760: 'Mumbai',
    28.7041: 'Delhi',
    31.5497: 'Amritsar',
    23.1815: 'Indore',
    25.3176: 'Varanasi',
    34.0837: 'Srinagar',
    19.0176: 'Colaba',
    22.5726: 'Kolkata',
    17.3850: 'Hyderabad'
}

# Add station names
df['station'] = df['latitude'].map(stations)

# Compare stations
station_comparison = df.groupby('station').agg({
    'temperature': ['mean', 'std', 'min', 'max'],
    'rainfall_mm': ['mean', 'sum', 'count']
})

print("=== STATION COMPARISON ===")
print(station_comparison)

# Latitude-temperature relationship
correlation = df[['latitude', 'temperature']].corr()
print(f"\nLatitude-Temperature correlation: {correlation.iloc[0, 1]:.3f}")
```

---

## Time-Series Preprocessing

### 1. Lag Features (for ML models)

```python
# Create lag features for forecasting
def create_lag_features(df, lags=[1, 6, 24, 168]):
    """Create lagged features for time-series forecasting"""
    for lag in lags:
        df[f'temp_lag_{lag}'] = df.groupby('latitude')['temperature'].shift(lag)
        df[f'rain_lag_{lag}'] = df.groupby('latitude')['rainfall_mm'].shift(lag)
    return df

df = create_lag_features(df, lags=[1, 6, 24])

# Rolling statistics
df['temp_rolling_mean_24'] = df.groupby('latitude')['temperature'].transform(
    lambda x: x.rolling(24).mean()
)
df['temp_rolling_std_24'] = df.groupby('latitude')['temperature'].transform(
    lambda x: x.rolling(24).std()
)

df['rain_rolling_sum_24'] = df.groupby('latitude')['rainfall_mm'].transform(
    lambda x: x.rolling(24).sum()
)

print("Lag features created!")
```

### 2. Differencing (for stationarity)

```python
# First difference
df['temp_diff_1'] = df.groupby('latitude')['temperature'].diff()

# Seasonal difference (24-hour for hourly data)
df['temp_diff_seasonal'] = df.groupby('latitude')['temperature'].diff(24)

# Check stationarity
from scipy import stats

# Augmented Dickey-Fuller test
print("=== STATIONARITY TEST (ADF) ===")
adf_result = stats.adfuller(df['temperature'].dropna())
print(f"ADF Statistic: {adf_result[0]:.4f}")
print(f"p-value: {adf_result[1]:.4f}")
print(f"Stationary: {'Yes' if adf_result[1] < 0.05 else 'No'}")
```

### 3. Train-Test Split (Time-Series Aware)

```python
# Time-based split (important for time-series!)
train_size = int(len(df) * 0.8)
train_df = df.iloc[:train_size]
test_df = df.iloc[train_size:]

print(f"Training set: {len(train_df)} records ({train_df['datetime'].min()} to {train_df['datetime'].max()})")
print(f"Test set: {len(test_df)} records ({test_df['datetime'].min()} to {test_df['datetime'].max()})")

# Per-station splits
for station in df['latitude'].unique():
    station_data = df[df['latitude'] == station]
    n = len(station_data)
    train_n = int(n * 0.8)
    
    station_train = station_data.iloc[:train_n]
    station_test = station_data.iloc[train_n:]
    
    print(f"{df[df['latitude']==station]['station'].iloc[0]}: "
          f"Train {len(station_train)}, Test {len(station_test)}")
```

---

## Visualization Examples

### 1. Temperature Patterns

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Daily cycle
hourly_avg = df.groupby('hour')['temperature'].mean()
axes[0, 0].plot(hourly_avg)
axes[0, 0].set_title('Average Daily Temperature Cycle')
axes[0, 0].set_xlabel('Hour of Day')
axes[0, 0].set_ylabel('Temperature (°C)')

# Monthly pattern
monthly_avg = df.groupby('month')['temperature'].mean()
axes[0, 1].plot(monthly_avg, marker='o')
axes[0, 1].set_title('Average Monthly Temperature')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Temperature (°C)')

# Station comparison
station_temps = df.groupby('station')['temperature'].mean().sort_values()
axes[1, 0].barh(range(len(station_temps)), station_temps.values)
axes[1, 0].set_yticks(range(len(station_temps)))
axes[1, 0].set_yticklabels(station_temps.index)
axes[1, 0].set_title('Average Temperature by Station')
axes[1, 0].set_xlabel('Temperature (°C)')

# Year-to-year
yearly_avg = df.groupby('year')['temperature'].mean()
axes[1, 1].plot(yearly_avg, marker='o', linewidth=2)
axes[1, 1].set_title('Year-to-Year Temperature Trend')
axes[1, 1].set_xlabel('Year')
axes[1, 1].set_ylabel('Temperature (°C)')

plt.tight_layout()
plt.savefig('temperature_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
```

### 2. Rainfall Patterns

```python
# Monsoon vs non-monsoon
df['is_monsoon'] = df['month'].isin([6, 7, 8, 9])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Monthly rainfall
monthly_rain = df.groupby('month')['rainfall_mm'].sum()
colors = ['green' if m in [6,7,8,9] else 'orange' for m in range(1, 13)]
axes[0].bar(range(1, 13), monthly_rain.values, color=colors)
axes[0].set_title('Monthly Rainfall Distribution')
axes[0].set_xlabel('Month')
axes[0].set_ylabel('Total Rainfall (mm)')

# Station comparison
station_rain = df.groupby('station')['rainfall_mm'].sum().sort_values()
axes[1].barh(range(len(station_rain)), station_rain.values)
axes[1].set_yticks(range(len(station_rain)))
axes[1].set_yticklabels(station_rain.index)
axes[1].set_title('Total Annual Rainfall by Station')
axes[1].set_xlabel('Rainfall (mm)')

plt.tight_layout()
plt.savefig('rainfall_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
```

---

## Machine Learning Examples

### 1. Temperature Forecasting

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Prepare data
ml_df = df.copy()
ml_df = create_lag_features(ml_df, lags=[1, 24, 168])

# Drop NaN values
ml_df = ml_df.dropna()

# Features and target
feature_cols = [col for col in ml_df.columns if col.startswith(('temp_lag', 'rain_lag', 'hour_', 'month_', 'temp_rolling'))]
X = ml_df[feature_cols]
y = ml_df['temperature']

# Split
split_idx = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# Train model
model = RandomForestRegressor(n_estimators=50, max_depth=20, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"Temperature Forecasting Results:")
print(f"RMSE: {rmse:.2f}°C")
print(f"R² Score: {r2:.3f}")
```

### 2. Seasonal Classification

```python
from sklearn.ensemble import RandomForestClassifier

# Prepare data
X_season = df[['temperature', 'rainfall_mm', 'latitude', 'hour', 'dayofyear']]
y_season = df['season']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X_season, y_season, test_size=0.2, random_state=42
)

# Train
clf = RandomForestClassifier(n_estimators=50, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
accuracy = clf.score(X_test, y_test)
print(f"Seasonal Classification Accuracy: {accuracy:.3f}")

# Feature importance
feature_importance = pd.Series(clf.feature_importances_, index=X_train.columns)
print("\nFeature Importance:")
print(feature_importance.sort_values(ascending=False))
```

---

## Export and Sharing

### 1. Save Processed Data

```python
# Save specific station
delhi_data = df[df['station'] == 'Delhi']
delhi_data.to_csv('delhi_weather_2015_2019.csv', index=False)

# Save seasonal subset
monsoon_data = df[df['season'] == 'Monsoon']
monsoon_data.to_csv('monsoon_data_2015_2019.csv', index=False)

# Export to Excel with formatting
with pd.ExcelWriter('weather_analysis.xlsx') as writer:
    station_comparison.to_excel(writer, sheet_name='Station Stats')
    seasonal_stats.to_excel(writer, sheet_name='Seasonal Stats')
    df.head(1000).to_excel(writer, sheet_name='Sample Data', index=False)
```

### 2. Generate Summary Reports

```python
# Create summary statistics
summary = {
    'Total Records': len(df),
    'Date Range': f"{df['datetime'].min()} to {df['datetime'].max()}",
    'Number of Stations': df['latitude'].nunique(),
    'Temperature - Mean': f"{df['temperature'].mean():.2f}°C",
    'Temperature - Range': f"{df['temperature'].min():.1f} to {df['temperature'].max():.1f}°C",
    'Rainfall - Total': f"{df['rainfall_mm'].sum():.0f} mm",
    'Rainfall - Rainy Hours': f"{(df['rainfall_mm'] > 0).sum()} ({(df['rainfall_mm'] > 0).sum()/len(df)*100:.1f}%)",
}

for key, value in summary.items():
    print(f"{key}: {value}")
```

---

## Common Issues & Solutions

### Issue 1: Memory Error with Large Subset
```python
# Solution: Process in chunks
chunk_size = 100000
for chunk in pd.read_csv('data/imd_weather_dataset_2015_2019.csv', chunksize=chunk_size):
    # Process chunk
    processed_chunk = process_data(chunk)
```

### Issue 2: Slow Groupby Operations
```python
# Solution: Use .transform() instead of .apply()
# Slow:
df['monthly_avg'] = df.groupby('month')['temperature'].apply(lambda x: x.mean())

# Fast:
df['monthly_avg'] = df.groupby('month')['temperature'].transform('mean')
```

### Issue 3: Time-Series Leakage in ML
```python
# Always use time-based split, not random split
train_cutoff = pd.Timestamp('2018-12-31')
train = df[df['datetime'] <= train_cutoff]
test = df[df['datetime'] > train_cutoff]
```

---

## Links & Resources

- **Official IMD**: https://www.imdpune.gov.in/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Scikit-learn**: https://scikit-learn.org/
- **Time-Series Forecasting Guide**: https://machinelearningmastery.com/time-series-forecasting/

---

This guide provides practical foundations for working with meteorological time-series data. Adapt examples to your specific use case!
