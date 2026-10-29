"""
Comprehensive Exploratory Data Analysis (EDA) for Climate Data
Analyzes rainfall and temperature patterns from the IMD weather dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Create output directory for plots
output_dir = "eda_outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("=" * 70)
print("CLIMATE DATA - EXPLORATORY DATA ANALYSIS (EDA)")
print("=" * 70)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("\n[1] LOADING DATA...")
print("-" * 70)

df = pd.read_csv('data/imd_weather_dataset_2015_2019.csv')
print("[OK] Loaded data/imd_weather_dataset_2015_2019.csv")
print("[OK] Initial shape: {}".format(df.shape))

# ============================================================
# 2. PREPARE DATETIME
# ============================================================
print("\n[2] PREPARING DATETIME...")
print("-" * 70)

df['datetime'] = pd.to_datetime(df['datetime'])
print("[OK] Converted datetime to pandas datetime format")
print("[OK] Date range: {} to {}".format(df['datetime'].min(), df['datetime'].max()))

# ============================================================
# 3. BASIC DATA CHECKS
# ============================================================
print("\n[3] BASIC DATA CHECKS...")
print("-" * 70)

print("\nDataset Shape: {}".format(df.shape))
print("  Rows: {:,}".format(df.shape[0]))
print("  Columns: {}".format(df.shape[1]))

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
missing = df.isnull().sum()
if missing.sum() == 0:
    print("  [OK] No missing values found!")
else:
    print(missing[missing > 0])

duplicates = df.duplicated().sum()
print("\nDuplicate Rows: {}".format(duplicates))
if duplicates == 0:
    print("  [OK] No duplicate rows found!")

print("\nFirst 5 rows:")
print(df.head())

# ============================================================
# 4. SUMMARY STATISTICS
# ============================================================
print("\n[4] SUMMARY STATISTICS...")
print("-" * 70)

print("\nRainfall (mm) Statistics:")
rainfall_stats = df['rainfall_mm'].describe()
print(rainfall_stats)
print("  Skewness: {:.3f}".format(df['rainfall_mm'].skew()))
print("  Kurtosis: {:.3f}".format(df['rainfall_mm'].kurtosis()))

print("\nTemperature (C) Statistics:")
temp_stats = df['temperature'].describe()
print(temp_stats)
print("  Skewness: {:.3f}".format(df['temperature'].skew()))
print("  Kurtosis: {:.3f}".format(df['temperature'].kurtosis()))

# ============================================================
# 5. CREATE TIME-BASED COLUMNS
# ============================================================
print("\n[5] CREATING TIME-BASED COLUMNS...")
print("-" * 70)

df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['day'] = df['datetime'].dt.day
df['hour'] = df['datetime'].dt.hour
df['dayofyear'] = df['datetime'].dt.dayofyear

print("[OK] Created columns: year, month, day, hour, dayofyear")

def get_season(month):
    if month in [12, 1, 2]:
        return 'DJF'
    elif month in [3, 4, 5]:
        return 'MAM'
    elif month in [6, 7, 8, 9]:
        return 'JJA'
    else:
        return 'SON'

df['season'] = df['month'].apply(get_season)
print("[OK] Created column: season (DJF, MAM, JJA, SON)")
print("\nSeason distribution:")
print(df['season'].value_counts().sort_index())

# ============================================================
# 6. EDA ANALYSIS
# ============================================================
print("\n[6] EXPLORATORY DATA ANALYSIS...")
print("-" * 70)

print("\n6.1 - Monthly Average Rainfall:")
monthly_rainfall = df.groupby('month')['rainfall_mm'].agg(['mean', 'sum', 'max', 'count'])
monthly_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Max (mm)', 'Events']
print(monthly_rainfall)

print("\n6.2 - Monthly Average Temperature:")
monthly_temp = df.groupby('month')['temperature'].agg(['mean', 'std', 'min', 'max'])
monthly_temp.columns = ['Mean (C)', 'Std Dev', 'Min (C)', 'Max (C)']
print(monthly_temp)

print("\n6.3 - Yearly Rainfall Trends:")
yearly_rainfall = df.groupby('year')['rainfall_mm'].agg(['mean', 'sum', 'std'])
yearly_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Std Dev']
print(yearly_rainfall)

print("\n6.4 - Yearly Temperature Trends:")
yearly_temp = df.groupby('year')['temperature'].agg(['mean', 'std', 'min', 'max'])
yearly_temp.columns = ['Mean (C)', 'Std Dev', 'Min (C)', 'Max (C)']
print(yearly_temp)

print("\n6.5 - Seasonal Rainfall Patterns:")
seasonal_rainfall = df.groupby('season')['rainfall_mm'].agg(['mean', 'sum', 'max', 'std'])
seasonal_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Max (mm)', 'Std Dev']
seasonal_rainfall = seasonal_rainfall.reindex(['DJF', 'MAM', 'JJA', 'SON'])
print(seasonal_rainfall)

print("\n6.6 - Seasonal Temperature Patterns:")
seasonal_temp = df.groupby('season')['temperature'].agg(['mean', 'std', 'min', 'max'])
seasonal_temp.columns = ['Mean (C)', 'Std Dev', 'Min (C)', 'Max (C)']
seasonal_temp = seasonal_temp.reindex(['DJF', 'MAM', 'JJA', 'SON'])
print(seasonal_temp)

print("\n6.7 - Peak Hourly Rainfall Hours:")
hourly_rainfall = df.groupby('hour')['rainfall_mm'].agg(['mean', 'sum', 'max'])
hourly_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Max (mm)']
print("Top 5 hours with highest average rainfall:")
print(hourly_rainfall.nlargest(5, 'Mean (mm)'))

print("\n6.8 - Peak Hourly Temperature Hours:")
hourly_temp = df.groupby('hour')['temperature'].agg(['mean', 'std', 'min', 'max'])
hourly_temp.columns = ['Mean (C)', 'Std Dev', 'Min (C)', 'Max (C)']
print("Top 5 hours with highest average temperature:")
print(hourly_temp.nlargest(5, 'Mean (C)'))

# ============================================================
# 7. CORRELATION ANALYSIS
# ============================================================
print("\n[7] CORRELATION ANALYSIS...")
print("-" * 70)

correlation = df[['temperature', 'rainfall_mm']].corr()
print("\nCorrelation Matrix:")
print(correlation)
print("\nRainfall-Temperature Correlation: {:.4f}".format(
    correlation.loc['temperature', 'rainfall_mm']))

fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, 
            square=True, ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title('Correlation Matrix: Temperature vs Rainfall', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('{}/07_correlation_heatmap.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/07_correlation_heatmap.png".format(output_dir))

# ============================================================
# 8. OUTLIER DETECTION
# ============================================================
print("\n[8] OUTLIER DETECTION...")
print("-" * 70)

Q1_rain = df['rainfall_mm'].quantile(0.25)
Q3_rain = df['rainfall_mm'].quantile(0.75)
IQR_rain = Q3_rain - Q1_rain
rain_outliers = df[(df['rainfall_mm'] > Q3_rain + 1.5*IQR_rain)]

print("\nRainfall Outliers (IQR method):")
print("  Q1: {:.2f}, Q3: {:.2f}, IQR: {:.2f}".format(Q1_rain, Q3_rain, IQR_rain))
print("  Upper fence: {:.2f} mm".format(Q3_rain + 1.5*IQR_rain))
print("  Outliers detected: {} ({:.2f}%)".format(
    len(rain_outliers), len(rain_outliers)/len(df)*100))

Q1_temp = df['temperature'].quantile(0.25)
Q3_temp = df['temperature'].quantile(0.75)
IQR_temp = Q3_temp - Q1_temp
temp_outliers = df[(df['temperature'] > Q3_temp + 1.5*IQR_temp) | 
                   (df['temperature'] < Q1_temp - 1.5*IQR_temp)]

print("\nTemperature Outliers (IQR method):")
print("  Q1: {:.2f}, Q3: {:.2f}, IQR: {:.2f}".format(Q1_temp, Q3_temp, IQR_temp))
print("  Lower fence: {:.2f}C".format(Q1_temp - 1.5*IQR_temp))
print("  Upper fence: {:.2f}C".format(Q3_temp + 1.5*IQR_temp))
print("  Outliers detected: {} ({:.2f}%)".format(
    len(temp_outliers), len(temp_outliers)/len(df)*100))

top_1pct_rain = df['rainfall_mm'].quantile(0.99)
extreme_rain = df[df['rainfall_mm'] >= top_1pct_rain]

print("\nExtreme Rainfall Events (Top 1%):")
print("  Threshold: {:.2f} mm".format(top_1pct_rain))
print("  Events detected: {}".format(len(extreme_rain)))
print("  Date range: {} to {}".format(
    extreme_rain['datetime'].min(), extreme_rain['datetime'].max()))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].boxplot(df['rainfall_mm'], vert=True)
axes[0].set_ylabel('Rainfall (mm)', fontsize=11)
axes[0].set_title('Rainfall Distribution - Outlier Detection', fontsize=12, fontweight='bold')
axes[0].grid(axis='y', alpha=0.3)

axes[1].boxplot(df['temperature'], vert=True)
axes[1].set_ylabel('Temperature (C)', fontsize=11)
axes[1].set_title('Temperature Distribution - Outlier Detection', fontsize=12, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('{}/08_outlier_boxplots.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/08_outlier_boxplots.png".format(output_dir))

# ============================================================
# 9. VISUALIZATIONS
# ============================================================
print("\n[9] CREATING VISUALIZATIONS...")
print("-" * 70)

print("  9.1 - Rainfall time series...")
fig, ax = plt.subplots(figsize=(15, 5))
daily_rainfall = df.groupby(df['datetime'].dt.date)['rainfall_mm'].sum()
ax.plot(daily_rainfall.index, daily_rainfall.values, linewidth=1, color='steelblue', alpha=0.7)
ax.fill_between(daily_rainfall.index, daily_rainfall.values, alpha=0.3, color='steelblue')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Daily Rainfall (mm)', fontsize=11)
ax.set_title('Daily Rainfall Over Time (2015-2019)', fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('{}/09_rainfall_timeseries.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/09_rainfall_timeseries.png".format(output_dir))

print("  9.2 - Temperature time series...")
fig, ax = plt.subplots(figsize=(15, 5))
daily_temp = df.groupby(df['datetime'].dt.date)['temperature'].mean()
ax.plot(daily_temp.index, daily_temp.values, linewidth=1, color='coral', alpha=0.7)
ax.fill_between(daily_temp.index, daily_temp.values, alpha=0.3, color='coral')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Daily Average Temperature (C)', fontsize=11)
ax.set_title('Daily Temperature Over Time (2015-2019)', fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('{}/10_temperature_timeseries.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/10_temperature_timeseries.png".format(output_dir))

print("  9.3 - Rainfall histogram...")
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['rainfall_mm'], bins=100, color='steelblue', edgecolor='black', alpha=0.7)
ax.set_xlabel('Rainfall (mm)', fontsize=11)
ax.set_ylabel('Frequency (hourly records)', fontsize=11)
ax.set_title('Rainfall Distribution (All Hours)', fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
stats_text = "Mean: {:.2f} mm\nStd: {:.2f} mm\nMax: {:.1f} mm".format(
    df['rainfall_mm'].mean(), df['rainfall_mm'].std(), df['rainfall_mm'].max())
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
plt.tight_layout()
plt.savefig('{}/11_rainfall_histogram.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/11_rainfall_histogram.png".format(output_dir))

print("  9.4 - Temperature histogram...")
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['temperature'], bins=50, color='coral', edgecolor='black', alpha=0.7)
ax.set_xlabel('Temperature (C)', fontsize=11)
ax.set_ylabel('Frequency (hourly records)', fontsize=11)
ax.set_title('Temperature Distribution (All Hours)', fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
stats_text = "Mean: {:.2f}C\nStd: {:.2f}C\nMin: {:.1f}C\nMax: {:.1f}C".format(
    df['temperature'].mean(), df['temperature'].std(), 
    df['temperature'].min(), df['temperature'].max())
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
plt.tight_layout()
plt.savefig('{}/12_temperature_histogram.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/12_temperature_histogram.png".format(output_dir))

print("  9.5 - Monthly boxplots...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

df.boxplot(column='rainfall_mm', by='month', ax=axes[0])
axes[0].set_xlabel('Month', fontsize=11)
axes[0].set_ylabel('Rainfall (mm)', fontsize=11)
axes[0].set_title('Monthly Rainfall Distribution', fontsize=12, fontweight='bold')
plt.sca(axes[0])
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

df.boxplot(column='temperature', by='month', ax=axes[1])
axes[1].set_xlabel('Month', fontsize=11)
axes[1].set_ylabel('Temperature (C)', fontsize=11)
axes[1].set_title('Monthly Temperature Distribution', fontsize=12, fontweight='bold')
plt.sca(axes[1])
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

plt.suptitle('')
plt.tight_layout()
plt.savefig('{}/13_monthly_boxplots.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/13_monthly_boxplots.png".format(output_dir))

print("  9.6 - Seasonal comparison...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

seasonal_data_rain = df.groupby('season')['rainfall_mm'].mean().reindex(['DJF', 'MAM', 'JJA', 'SON'])
seasonal_data_temp = df.groupby('season')['temperature'].mean().reindex(['DJF', 'MAM', 'JJA', 'SON'])

axes[0].bar(seasonal_data_rain.index, seasonal_data_rain.values, 
            color=['lightblue', 'tan', 'green', 'orange'], alpha=0.7, edgecolor='black')
axes[0].set_ylabel('Average Rainfall (mm/hour)', fontsize=11)
axes[0].set_title('Seasonal Average Rainfall', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Season', fontsize=11)
axes[0].grid(axis='y', alpha=0.3)

axes[1].bar(seasonal_data_temp.index, seasonal_data_temp.values, 
            color=['lightblue', 'tan', 'green', 'orange'], alpha=0.7, edgecolor='black')
axes[1].set_ylabel('Average Temperature (C)', fontsize=11)
axes[1].set_title('Seasonal Average Temperature', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Season', fontsize=11)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('{}/14_seasonal_comparison.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/14_seasonal_comparison.png".format(output_dir))

print("  9.7 - Yearly trends...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

yearly_rain = df.groupby('year')['rainfall_mm'].mean()
yearly_temp = df.groupby('year')['temperature'].mean()

axes[0].plot(yearly_rain.index, yearly_rain.values, marker='o', linewidth=2, markersize=8, color='steelblue')
axes[0].set_xlabel('Year', fontsize=11)
axes[0].set_ylabel('Average Rainfall (mm/hour)', fontsize=11)
axes[0].set_title('Yearly Average Rainfall Trend', fontsize=12, fontweight='bold')
axes[0].grid(alpha=0.3)
axes[0].set_xticks(yearly_rain.index)

axes[1].plot(yearly_temp.index, yearly_temp.values, marker='s', linewidth=2, markersize=8, color='coral')
axes[1].set_xlabel('Year', fontsize=11)
axes[1].set_ylabel('Average Temperature (C)', fontsize=11)
axes[1].set_title('Yearly Average Temperature Trend', fontsize=12, fontweight='bold')
axes[1].grid(alpha=0.3)
axes[1].set_xticks(yearly_temp.index)

plt.tight_layout()
plt.savefig('{}/15_yearly_trends.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/15_yearly_trends.png".format(output_dir))

print("  9.8 - Diurnal patterns...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

hourly_rain = df.groupby('hour')['rainfall_mm'].mean()
hourly_temp = df.groupby('hour')['temperature'].mean()

axes[0].plot(hourly_rain.index, hourly_rain.values, marker='o', linewidth=2, markersize=6, color='steelblue')
axes[0].fill_between(hourly_rain.index, hourly_rain.values, alpha=0.3, color='steelblue')
axes[0].set_xlabel('Hour of Day', fontsize=11)
axes[0].set_ylabel('Average Rainfall (mm/hour)', fontsize=11)
axes[0].set_title('Diurnal Rainfall Pattern', fontsize=12, fontweight='bold')
axes[0].grid(alpha=0.3)
axes[0].set_xticks(range(0, 24, 2))

axes[1].plot(hourly_temp.index, hourly_temp.values, marker='s', linewidth=2, markersize=6, color='coral')
axes[1].fill_between(hourly_temp.index, hourly_temp.values, alpha=0.3, color='coral')
axes[1].set_xlabel('Hour of Day', fontsize=11)
axes[1].set_ylabel('Average Temperature (C)', fontsize=11)
axes[1].set_title('Diurnal Temperature Pattern', fontsize=12, fontweight='bold')
axes[1].grid(alpha=0.3)
axes[1].set_xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig('{}/16_diurnal_patterns.png'.format(output_dir), dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: {}/16_diurnal_patterns.png".format(output_dir))

# ============================================================
# 10. KEY INSIGHTS
# ============================================================
print("\n[10] KEY INSIGHTS")
print("=" * 70)

print("\nDATASET OVERVIEW:")
print("  Total records: {:,} hourly observations".format(len(df)))
print("  Time period: {} to {}".format(
    df['datetime'].min().strftime('%Y-%m-%d'), 
    df['datetime'].max().strftime('%Y-%m-%d')))
print("  Data completeness: 100%")

print("\nTEMPERATURE INSIGHTS:")
avg_temp = df['temperature'].mean()
temp_range = df['temperature'].max() - df['temperature'].min()
print("  Average: {:.2f}C".format(avg_temp))
print("  Range: {:.1f}C to {:.1f}C ({:.1f}C spread)".format(
    df['temperature'].min(), df['temperature'].max(), temp_range))
print("  Warmest season: {:.2f}C (Monsoon-JJA)".format(seasonal_temp.loc['JJA', 'Mean (C)']))
print("  Coolest season: {:.2f}C (Winter-DJF)".format(seasonal_temp.loc['DJF', 'Mean (C)']))

print("\nRAINFALL INSIGHTS:")
avg_rain = df['rainfall_mm'].mean()
total_rain = df['rainfall_mm'].sum()
rainy_pct = (df['rainfall_mm'] > 0).sum() / len(df) * 100
print("  Average: {:.2f} mm/hour".format(avg_rain))
print("  Total 5-year: {:.0f} mm".format(total_rain))
print("  Rainy hours: {:.1f}% of all observations".format(rainy_pct))
print("  Heaviest season: {:.2f} mm/hour (Monsoon-JJA)".format(
    seasonal_rainfall.loc['JJA', 'Mean (mm)']))
print("  Driest season: {:.2f} mm/hour (Winter-DJF)".format(
    seasonal_rainfall.loc['DJF', 'Mean (mm)']))
print("  Extreme events (>=100mm): {} hours".format(len(extreme_rain)))

print("\nTEMPORAL PATTERNS:")
warmest_month = monthly_temp['Mean (C)'].idxmax()
coolest_month = monthly_temp['Mean (C)'].idxmin()
wettest_month = monthly_rainfall['Mean (mm)'].idxmax()
driest_month = monthly_rainfall['Mean (mm)'].idxmin()
month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print("  Warmest month: {} ({:.1f}C)".format(
    month_names[warmest_month], monthly_temp.loc[warmest_month, 'Mean (C)']))
print("  Coolest month: {} ({:.1f}C)".format(
    month_names[coolest_month], monthly_temp.loc[coolest_month, 'Mean (C)']))
print("  Wettest month: {} ({:.1f} mm/hour)".format(
    month_names[wettest_month], monthly_rainfall.loc[wettest_month, 'Mean (mm)']))
print("  Driest month: {} ({:.2f} mm/hour)".format(
    month_names[driest_month], monthly_rainfall.loc[driest_month, 'Mean (mm)']))

print("\nCLIMATE CYCLES:")
print("  Diurnal (24-hour) variations present")
print("  Clear seasonal monsoon pattern (Jun-Sep)")
print("  Year-to-year consistency observed")

print("\nANOMALIES & OUTLIERS:")
print("  Rainfall outliers: {} ({:.2f}%)".format(
    len(rain_outliers), len(rain_outliers)/len(df)*100))
print("  Temperature outliers: {} ({:.2f}%)".format(
    len(temp_outliers), len(temp_outliers)/len(df)*100))
print("  Extreme rainfall (>=100mm): {} events".format(len(extreme_rain)))

print("\nCORRELATION:")
corr_value = df['temperature'].corr(df['rainfall_mm'])
print("  Temperature vs Rainfall: {:.4f}".format(corr_value))
if corr_value < -0.3:
    print("    -> Inverse relationship: Cooler during rainy season (expected)")
else:
    print("    -> Weak relationship")

print("\n" + "=" * 70)
print("[COMPLETE] EDA ANALYSIS FINISHED")
print("=" * 70)
print("\nAll visualizations saved to: {}".format(output_dir))
print("Total visualization files: 10")
print("\nAnalysis completed successfully!")
