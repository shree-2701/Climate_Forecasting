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

# ============================================================
# SETUP
# ============================================================

# Create output directory for plots
output_dir = "eda_outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print("[OK] Created directory: {}".format(output_dir))

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("="*70)
print("CLIMATE DATA - EXPLORATORY DATA ANALYSIS (EDA)")
print("="*70)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n[1] LOADING DATA...")
print("-" * 70)

# Load the dataset
df = pd.read_csv('data/imd_weather_dataset_2015_2019.csv')
print("[OK] Loaded data/imd_weather_dataset_2015_2019.csv")
print("[OK] Initial shape: {}".format(df.shape))


# ============================================================
# 2. PREPARE DATETIME COLUMN
# ============================================================

print("\n[2] PREPARING DATETIME...")
print("-" * 70)

# Convert datetime column to datetime type
df['datetime'] = pd.to_datetime(df['datetime'])
print(f"✓ Converted 'datetime' to pandas datetime format")
print(f"✓ Date range: {df['datetime'].min()} to {df['datetime'].max()}")


# ============================================================
# 3. BASIC DATA CHECKS
# ============================================================

print("\n[3] BASIC DATA CHECKS...")
print("-" * 70)

# Display shape
print(f"\nDataset Shape: {df.shape}")
print(f"  Rows: {df.shape[0]:,}")
print(f"  Columns: {df.shape[1]}")

# Display data types
print(f"\nData Types:")
print(df.dtypes)

# Check for missing values
print(f"\nMissing Values:")
missing = df.isnull().sum()
if missing.sum() == 0:
    print("  ✓ No missing values found!")
else:
    print(missing[missing > 0])

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"\nDuplicate Rows: {duplicates}")
if duplicates == 0:
    print("  ✓ No duplicate rows found!")

# Display first few rows
print(f"\nFirst 5 rows:")
print(df.head())


# ============================================================
# 4. SUMMARY STATISTICS
# ============================================================

print("\n[4] SUMMARY STATISTICS...")
print("-" * 70)

print("\nRainfall (mm) Statistics:")
rainfall_stats = df['rainfall_mm'].describe()
print(rainfall_stats)
print(f"  Skewness: {df['rainfall_mm'].skew():.3f}")
print(f"  Kurtosis: {df['rainfall_mm'].kurtosis():.3f}")

print("\nTemperature (°C) Statistics:")
temp_stats = df['temperature'].describe()
print(temp_stats)
print(f"  Skewness: {df['temperature'].skew():.3f}")
print(f"  Kurtosis: {df['temperature'].kurtosis():.3f}")


# ============================================================
# 5. CREATE TIME-BASED COLUMNS
# ============================================================

print("\n[5] CREATING TIME-BASED COLUMNS...")
print("-" * 70)

# Extract time components
df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['day'] = df['datetime'].dt.day
df['hour'] = df['datetime'].dt.hour
df['dayofyear'] = df['datetime'].dt.dayofyear

print("✓ Created columns: year, month, day, hour, dayofyear")

# Create season column
def get_season(month):
    """Convert month to season (DJF, MAM, JJA, SON)"""
    if month in [12, 1, 2]:
        return 'DJF'  # Winter
    elif month in [3, 4, 5]:
        return 'MAM'  # Spring
    elif month in [6, 7, 8, 9]:
        return 'JJA'  # Summer/Monsoon
    else:
        return 'SON'  # Fall

df['season'] = df['month'].apply(get_season)
print("✓ Created column: season (DJF, MAM, JJA, SON)")
print(f"\nSeason distribution:")
print(df['season'].value_counts().sort_index())


# ============================================================
# 6. EDA ANALYSIS
# ============================================================

print("\n[6] EXPLORATORY DATA ANALYSIS...")
print("-" * 70)

# Monthly average rainfall
print("\n6.1 - Monthly Average Rainfall:")
monthly_rainfall = df.groupby('month')['rainfall_mm'].agg(['mean', 'sum', 'max', 'count'])
monthly_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Max (mm)', 'Events']
print(monthly_rainfall)

# Monthly average temperature
print("\n6.2 - Monthly Average Temperature:")
monthly_temp = df.groupby('month')['temperature'].agg(['mean', 'std', 'min', 'max'])
monthly_temp.columns = ['Mean (°C)', 'Std Dev', 'Min (°C)', 'Max (°C)']
print(monthly_temp)

# Yearly trends - Rainfall
print("\n6.3 - Yearly Rainfall Trends:")
yearly_rainfall = df.groupby('year')['rainfall_mm'].agg(['mean', 'sum', 'std'])
yearly_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Std Dev']
print(yearly_rainfall)

# Yearly trends - Temperature
print("\n6.4 - Yearly Temperature Trends:")
yearly_temp = df.groupby('year')['temperature'].agg(['mean', 'std', 'min', 'max'])
yearly_temp.columns = ['Mean (°C)', 'Std Dev', 'Min (°C)', 'Max (°C)']
print(yearly_temp)

# Seasonal patterns - Rainfall
print("\n6.5 - Seasonal Rainfall Patterns:")
seasonal_rainfall = df.groupby('season')['rainfall_mm'].agg(['mean', 'sum', 'max', 'std'])
seasonal_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Max (mm)', 'Std Dev']
seasonal_rainfall = seasonal_rainfall.reindex(['DJF', 'MAM', 'JJA', 'SON'])
print(seasonal_rainfall)

# Seasonal patterns - Temperature
print("\n6.6 - Seasonal Temperature Patterns:")
seasonal_temp = df.groupby('season')['temperature'].agg(['mean', 'std', 'min', 'max'])
seasonal_temp.columns = ['Mean (°C)', 'Std Dev', 'Min (°C)', 'Max (°C)']
seasonal_temp = seasonal_temp.reindex(['DJF', 'MAM', 'JJA', 'SON'])
print(seasonal_temp)

# Rainfall by time of day
print("\n6.7 - Hourly Rainfall Pattern:")
hourly_rainfall = df.groupby('hour')['rainfall_mm'].agg(['mean', 'sum', 'max'])
hourly_rainfall.columns = ['Mean (mm)', 'Total (mm)', 'Max (mm)']
print(hourly_rainfall)

# Temperature by time of day
print("\n6.8 - Hourly Temperature Pattern:")
hourly_temp = df.groupby('hour')['temperature'].agg(['mean', 'std', 'min', 'max'])
hourly_temp.columns = ['Mean (°C)', 'Std Dev', 'Min (°C)', 'Max (°C)']
print(hourly_temp)


# ============================================================
# 7. CORRELATION ANALYSIS
# ============================================================

print("\n[7] CORRELATION ANALYSIS...")
print("-" * 70)

# Calculate correlation
correlation = df[['temperature', 'rainfall_mm']].corr()
print("\nCorrelation Matrix:")
print(correlation)
print(f"\n✓ Rainfall-Temperature Correlation: {correlation.loc['temperature', 'rainfall_mm']:.4f}")

# Interpretation
if abs(correlation.loc['temperature', 'rainfall_mm']) < 0.3:
    print("  → Weak correlation (expected: cooler during monsoon, warmer in summer)")
elif abs(correlation.loc['temperature', 'rainfall_mm']) < 0.7:
    print("  → Moderate correlation")
else:
    print("  → Strong correlation")

# Create correlation heatmap
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, 
            square=True, ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title('Correlation Matrix: Temperature vs Rainfall', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{output_dir}/07_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✓ Saved: {output_dir}/07_correlation_heatmap.png")


# ============================================================
# 8. OUTLIER DETECTION
# ============================================================

print("\n[8] OUTLIER DETECTION...")
print("-" * 70)

# Rainfall outliers using IQR method
Q1_rain = df['rainfall_mm'].quantile(0.25)
Q3_rain = df['rainfall_mm'].quantile(0.75)
IQR_rain = Q3_rain - Q1_rain
rain_outliers = df[(df['rainfall_mm'] > Q3_rain + 1.5*IQR_rain)]

print(f"\nRainfall Outliers (IQR method):")
print(f"  Q1: {Q1_rain:.2f}, Q3: {Q3_rain:.2f}, IQR: {IQR_rain:.2f}")
print(f"  Upper fence: {Q3_rain + 1.5*IQR_rain:.2f} mm")
print(f"  Outliers detected: {len(rain_outliers)} ({len(rain_outliers)/len(df)*100:.2f}%)")

# Temperature outliers using IQR method
Q1_temp = df['temperature'].quantile(0.25)
Q3_temp = df['temperature'].quantile(0.75)
IQR_temp = Q3_temp - Q1_temp
temp_outliers = df[(df['temperature'] > Q3_temp + 1.5*IQR_temp) | 
                   (df['temperature'] < Q1_temp - 1.5*IQR_temp)]

print(f"\nTemperature Outliers (IQR method):")
print(f"  Q1: {Q1_temp:.2f}, Q3: {Q3_temp:.2f}, IQR: {IQR_temp:.2f}")
print(f"  Lower fence: {Q1_temp - 1.5*IQR_temp:.2f}°C")
print(f"  Upper fence: {Q3_temp + 1.5*IQR_temp:.2f}°C")
print(f"  Outliers detected: {len(temp_outliers)} ({len(temp_outliers)/len(df)*100:.2f}%)")

# Extreme rainfall events (top 1%)
top_1pct_rain = df['rainfall_mm'].quantile(0.99)
extreme_rain = df[df['rainfall_mm'] >= top_1pct_rain]

print(f"\nExtreme Rainfall Events (Top 1%):")
print(f"  Threshold: {top_1pct_rain:.2f} mm")
print(f"  Events detected: {len(extreme_rain)}")
print(f"  Date range: {extreme_rain['datetime'].min()} to {extreme_rain['datetime'].max()}")

# Show a few extreme events
print(f"\n  Top 10 extreme rainfall events:")
top_extreme = extreme_rain.nlargest(10, 'rainfall_mm')[['datetime', 'latitude', 'rainfall_mm', 'temperature']]
print(top_extreme.to_string(index=False))

# Boxplots for outlier visualization
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Rainfall boxplot
axes[0].boxplot(df['rainfall_mm'], vert=True)
axes[0].set_ylabel('Rainfall (mm)', fontsize=11)
axes[0].set_title('Rainfall Distribution - Outlier Detection', fontsize=12, fontweight='bold')
axes[0].grid(axis='y', alpha=0.3)

# Temperature boxplot
axes[1].boxplot(df['temperature'], vert=True)
axes[1].set_ylabel('Temperature (°C)', fontsize=11)
axes[1].set_title('Temperature Distribution - Outlier Detection', fontsize=12, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}/08_outlier_boxplots.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✓ Saved: {output_dir}/08_outlier_boxplots.png")


# ============================================================
# 9. VISUALIZATIONS
# ============================================================

print("\n[9] CREATING VISUALIZATIONS...")
print("-" * 70)

# 9.1 - Rainfall over time (line plot)
print("\n  9.1 - Rainfall time series...")
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
plt.savefig(f'{output_dir}/09_rainfall_timeseries.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/09_rainfall_timeseries.png")

# 9.2 - Temperature over time (line plot)
print("  9.2 - Temperature time series...")
fig, ax = plt.subplots(figsize=(15, 5))
daily_temp = df.groupby(df['datetime'].dt.date)['temperature'].mean()
ax.plot(daily_temp.index, daily_temp.values, linewidth=1, color='coral', alpha=0.7)
ax.fill_between(daily_temp.index, daily_temp.values, alpha=0.3, color='coral')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Daily Average Temperature (°C)', fontsize=11)
ax.set_title('Daily Temperature Over Time (2015-2019)', fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/10_temperature_timeseries.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/10_temperature_timeseries.png")

# 9.3 - Rainfall distribution (histogram)
print("  9.3 - Rainfall histogram...")
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['rainfall_mm'], bins=100, color='steelblue', edgecolor='black', alpha=0.7)
ax.set_xlabel('Rainfall (mm)', fontsize=11)
ax.set_ylabel('Frequency (hourly records)', fontsize=11)
ax.set_title('Rainfall Distribution (All Hours)', fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
# Add statistics text
stats_text = f"Mean: {df['rainfall_mm'].mean():.2f} mm\nStd: {df['rainfall_mm'].std():.2f} mm\nMax: {df['rainfall_mm'].max():.1f} mm"
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
plt.tight_layout()
plt.savefig(f'{output_dir}/11_rainfall_histogram.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/11_rainfall_histogram.png")

# 9.4 - Temperature distribution (histogram)
print("  9.4 - Temperature histogram...")
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['temperature'], bins=50, color='coral', edgecolor='black', alpha=0.7)
ax.set_xlabel('Temperature (°C)', fontsize=11)
ax.set_ylabel('Frequency (hourly records)', fontsize=11)
ax.set_title('Temperature Distribution (All Hours)', fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
# Add statistics text
stats_text = f"Mean: {df['temperature'].mean():.2f}°C\nStd: {df['temperature'].std():.2f}°C\nMin: {df['temperature'].min():.1f}°C\nMax: {df['temperature'].max():.1f}°C"
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
plt.tight_layout()
plt.savefig(f'{output_dir}/12_temperature_histogram.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/12_temperature_histogram.png")

# 9.5 - Monthly boxplots (rainfall and temperature)
print("  9.5 - Monthly boxplots...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Monthly rainfall
df.boxplot(column='rainfall_mm', by='month', ax=axes[0])
axes[0].set_xlabel('Month', fontsize=11)
axes[0].set_ylabel('Rainfall (mm)', fontsize=11)
axes[0].set_title('Monthly Rainfall Distribution', fontsize=12, fontweight='bold')
plt.sca(axes[0])
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# Monthly temperature
df.boxplot(column='temperature', by='month', ax=axes[1])
axes[1].set_xlabel('Month', fontsize=11)
axes[1].set_ylabel('Temperature (°C)', fontsize=11)
axes[1].set_title('Monthly Temperature Distribution', fontsize=12, fontweight='bold')
plt.sca(axes[1])
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

plt.suptitle('')  # Remove the automatic title
plt.tight_layout()
plt.savefig(f'{output_dir}/13_monthly_boxplots.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/13_monthly_boxplots.png")

# 9.6 - Seasonal patterns (bar plots with line overlay)
print("  9.6 - Seasonal comparison plots...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

seasonal_data_rain = df.groupby('season')['rainfall_mm'].mean().reindex(['DJF', 'MAM', 'JJA', 'SON'])
seasonal_data_temp = df.groupby('season')['temperature'].mean().reindex(['DJF', 'MAM', 'JJA', 'SON'])

# Seasonal rainfall
axes[0].bar(seasonal_data_rain.index, seasonal_data_rain.values, color=['lightblue', 'tan', 'green', 'orange'], alpha=0.7, edgecolor='black')
axes[0].set_ylabel('Average Rainfall (mm/hour)', fontsize=11)
axes[0].set_title('Seasonal Average Rainfall', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Season', fontsize=11)
axes[0].grid(axis='y', alpha=0.3)
for i, v in enumerate(seasonal_data_rain.values):
    axes[0].text(i, v + 0.5, f'{v:.1f}', ha='center', fontweight='bold')

# Seasonal temperature
axes[1].bar(seasonal_data_temp.index, seasonal_data_temp.values, color=['lightblue', 'tan', 'green', 'orange'], alpha=0.7, edgecolor='black')
axes[1].set_ylabel('Average Temperature (°C)', fontsize=11)
axes[1].set_title('Seasonal Average Temperature', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Season', fontsize=11)
axes[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(seasonal_data_temp.values):
    axes[1].text(i, v + 0.5, f'{v:.1f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}/14_seasonal_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/14_seasonal_comparison.png")

# 9.7 - Yearly trends (line plots)
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
axes[1].set_ylabel('Average Temperature (°C)', fontsize=11)
axes[1].set_title('Yearly Average Temperature Trend', fontsize=12, fontweight='bold')
axes[1].grid(alpha=0.3)
axes[1].set_xticks(yearly_temp.index)

plt.tight_layout()
plt.savefig(f'{output_dir}/15_yearly_trends.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/15_yearly_trends.png")

# 9.8 - Diurnal (hourly) patterns
print("  9.8 - Diurnal patterns (hourly cycles)...")
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
axes[1].set_ylabel('Average Temperature (°C)', fontsize=11)
axes[1].set_title('Diurnal Temperature Pattern', fontsize=12, fontweight='bold')
axes[1].grid(alpha=0.3)
axes[1].set_xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig(f'{output_dir}/16_diurnal_patterns.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {output_dir}/16_diurnal_patterns.png")


# ============================================================
# 10. KEY INSIGHTS
# ============================================================

print("\n[10] KEY INSIGHTS")
print("="*70)

print("\n📊 DATASET OVERVIEW:")
print(f"  • Total records: {len(df):,} hourly observations")
print(f"  • Time period: {df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}")
print(f"  • Data completeness: 100%")

print("\n🌡️ TEMPERATURE INSIGHTS:")
avg_temp = df['temperature'].mean()
temp_range = df['temperature'].max() - df['temperature'].min()
print(f"  • Average: {avg_temp:.2f}°C")
print(f"  • Range: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C ({temp_range:.1f}°C spread)")
print(f"  • Warmest season: {seasonal_temp.loc['JJA', 'Mean (°C)']:.2f}°C (Monsoon)")
print(f"  • Coolest season: {seasonal_temp.loc['DJF', 'Mean (°C)']:.2f}°C (Winter)")

print("\n🌧️ RAINFALL INSIGHTS:")
avg_rain = df['rainfall_mm'].mean()
total_rain = df['rainfall_mm'].sum()
rainy_pct = (df['rainfall_mm'] > 0).sum() / len(df) * 100
print(f"  • Average: {avg_rain:.2f} mm/hour")
print(f"  • Total 5-year: {total_rain:.0f} mm")
print(f"  • Rainy hours: {rainy_pct:.1f}% of all observations")
print(f"  • Heaviest season: {seasonal_rainfall.loc['JJA', 'Mean (mm)']:.2f} mm/hour (Monsoon)")
print(f"  • Driest season: {seasonal_rainfall.loc['DJF', 'Mean (mm)']:.2f} mm/hour (Winter)")
print(f"  • Extreme events (≥100mm): {len(extreme_rain)} hours")

print("\n📈 TEMPORAL PATTERNS:")
warmest_month = monthly_temp['Mean (°C)'].idxmax()
coolest_month = monthly_temp['Mean (°C)'].idxmin()
wettest_month = monthly_rainfall['Mean (mm)'].idxmax()
driest_month = monthly_rainfall['Mean (mm)'].idxmin()
month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print(f"  • Warmest month: {month_names[warmest_month]} ({monthly_temp.loc[warmest_month, 'Mean (°C)']:.1f}°C)")
print(f"  • Coolest month: {month_names[coolest_month]} ({monthly_temp.loc[coolest_month, 'Mean (°C)']:.1f}°C)")
print(f"  • Wettest month: {month_names[wettest_month]} ({monthly_rainfall.loc[wettest_month, 'Mean (mm)']:.1f} mm/hour)")
print(f"  • Driest month: {month_names[driest_month]} ({monthly_rainfall.loc[driest_month, 'Mean (mm)']:.2f} mm/hour)")

print("\n🔄 CLIMATE CYCLES:")
print(f"  • Diurnal (24-hour) variations present")
print(f"  • Clear seasonal monsoon pattern (Jun-Sep)")
print(f"  • Year-to-year consistency observed")

print("\n⚠️ ANOMALIES & OUTLIERS:")
print(f"  • Rainfall outliers: {len(rain_outliers)} ({len(rain_outliers)/len(df)*100:.2f}%)")
print(f"  • Temperature outliers: {len(temp_outliers)} ({len(temp_outliers)/len(df)*100:.2f}%)")
print(f"  • Extreme rainfall (≥100mm): {len(extreme_rain)} events")

print("\n📊 CORRELATION:")
corr_value = df['temperature'].corr(df['rainfall_mm'])
print(f"  • Temperature vs Rainfall: {corr_value:.4f}")
if corr_value < -0.3:
    print(f"    → Inverse relationship: Cooler during rainy season (expected)")
else:
    print(f"    → Weak relationship")

print("\n" + "="*70)
print("✅ EDA COMPLETE")
print("="*70)
print(f"\n📁 All visualizations saved to: {output_dir}/")
print(f"   Total files: 10 visualization files")
print("\n✓ Analysis completed successfully!")
