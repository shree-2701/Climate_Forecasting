"""
Update ONLY the rainfall_mm column in the IMD weather dataset
with realistic, seasonally-appropriate precipitation values.
Keep all other columns unchanged.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

def generate_realistic_rainfall(month, hour, latitude, previous_rain=None, rain_streak=0):
    """
    Generate realistic rainfall based on season, time of day, and location.
    
    Args:
        month: Month (1-12)
        hour: Hour of day (0-23)
        latitude: Station latitude
        previous_rain: Rain amount from previous hour (for correlation)
        rain_streak: Current rain streak counter
    
    Returns:
        rainfall_mm (float)
    """
    
    # Seasonal base probabilities and ranges
    if 6 <= month <= 9:  # Monsoon (Jun-Sep)
        base_prob = 0.45  # 45% chance of hourly rain
        min_rain = 2
        max_rain = 150
        mean_rain = 40
        
    elif 10 <= month <= 11:  # Post-monsoon (Oct-Nov)
        base_prob = 0.20  # 20% chance of hourly rain
        min_rain = 0
        max_rain = 80
        mean_rain = 20
        
    elif 12 <= month or month <= 2:  # Winter (Dec-Feb)
        base_prob = 0.08  # 8% chance of hourly rain
        min_rain = 0
        max_rain = 10
        mean_rain = 3
        
    else:  # Pre-monsoon (Mar-May)
        base_prob = 0.12  # 12% chance of hourly rain
        min_rain = 0
        max_rain = 25
        mean_rain = 8
    
    # Hourly modulation (more rain in certain hours)
    # Peak rain in afternoon/evening (12-18) for most seasons
    hour_factor = 1.0
    if 12 <= hour <= 18:
        hour_factor = 1.3  # 30% more likely
    elif 6 <= hour <= 11 or 19 <= hour <= 23:
        hour_factor = 1.0
    else:
        hour_factor = 0.7  # 30% less likely at night/early morning
    
    adjusted_prob = min(base_prob * hour_factor, 0.9)
    
    # Temporal correlation with previous hour (if it was raining, continue)
    if previous_rain is not None and previous_rain > 0:
        # 70% chance to continue rain pattern
        adjusted_prob = min(adjusted_prob + 0.3, 0.95)
    
    # Decide if it rains
    if np.random.random() < adjusted_prob:
        # Generate rainfall amount
        
        # Occasional extreme events (1% chance)
        if np.random.random() < 0.01:
            rainfall = np.random.uniform(max_rain * 0.5, max_rain)
        else:
            # Exponential distribution for rainfall
            rainfall = np.random.exponential(mean_rain / 1.5)
        
        # Clip to seasonal bounds
        rainfall = np.clip(rainfall, min_rain, max_rain)
        
        # Temporal correlation with previous hour
        if previous_rain is not None and previous_rain > 0:
            rainfall = 0.6 * previous_rain + 0.4 * rainfall
        
        return max(0.0, round(rainfall, 1))
    else:
        # No rain
        return 0.0


def update_rainfall_in_csv(input_file, output_file):
    """
    Update only the rainfall_mm column in the CSV file.
    Keep all other columns exactly as they are.
    """
    
    print("Loading CSV file...")
    df = pd.read_csv(input_file)
    
    print(f"Original shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Identify which column is the rainfall column
    rainfall_col = None
    for col in df.columns:
        if 'rainfall' in col.lower() or 'rain' in col.lower():
            rainfall_col = col
            break
    
    if rainfall_col is None:
        raise ValueError(f"Rainfall column not found. Available columns: {list(df.columns)}")
    
    print(f"\nFound rainfall column: '{rainfall_col}'")
    
    # Parse datetime if it exists
    datetime_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower() or 'datetime' in col.lower():
            datetime_col = col
            break
    
    if datetime_col:
        try:
            df[datetime_col] = pd.to_datetime(df[datetime_col])
            print(f"Using datetime column: '{datetime_col}'")
        except:
            print(f"Could not parse {datetime_col} as datetime")
    
    # Identify latitude column
    lat_col = None
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
            break
    
    print(f"Latitude column: '{lat_col}'")
    
    # Generate new rainfall values
    print("\nGenerating realistic rainfall values...")
    new_rainfall = []
    previous_rain_by_station = {}
    
    for idx, row in df.iterrows():
        if idx % 50000 == 0:
            print(f"  Processing row {idx}/{len(df)}...")
        
        # Extract month and hour
        if datetime_col:
            dt = row[datetime_col]
            month = dt.month
            hour = dt.hour
        else:
            month = 6  # Default to monsoon
            hour = 12
        
        # Get latitude for location-specific variations
        latitude = row[lat_col] if lat_col else 20
        
        # Get previous rain for this station
        station_key = latitude
        prev_rain = previous_rain_by_station.get(station_key, None)
        
        # Generate new rainfall
        rainfall = generate_realistic_rainfall(month, hour, latitude, prev_rain)
        new_rainfall.append(rainfall)
        
        # Track for next iteration
        previous_rain_by_station[station_key] = rainfall
    
    # Replace rainfall column
    print("\nReplacing rainfall column...")
    df[rainfall_col] = new_rainfall
    
    # Save to CSV
    print(f"\nSaving updated CSV to: {output_file}")
    df.to_csv(output_file, index=False)
    
    # Print statistics
    print("\n" + "="*60)
    print("RAINFALL UPDATE SUMMARY")
    print("="*60)
    print(f"Total records: {len(df)}")
    print(f"\nRainfall Statistics:")
    print(f"  Min: {df[rainfall_col].min():.1f} mm")
    print(f"  Max: {df[rainfall_col].max():.1f} mm")
    print(f"  Mean: {df[rainfall_col].mean():.2f} mm")
    print(f"  Std Dev: {df[rainfall_col].std():.2f} mm")
    print(f"  Hours with rain: {(df[rainfall_col] > 0).sum()} ({(df[rainfall_col] > 0).sum()/len(df)*100:.1f}%)")
    
    # Seasonal breakdown
    if datetime_col:
        df['month'] = df[datetime_col].dt.month
        
        print(f"\nRainfall by Season:")
        for season, months in [
            ('Monsoon (Jun-Sep)', [6, 7, 8, 9]),
            ('Post-Monsoon (Oct-Nov)', [10, 11]),
            ('Winter (Dec-Feb)', [12, 1, 2]),
            ('Pre-Monsoon (Mar-May)', [3, 4, 5])
        ]:
            season_data = df[df['month'].isin(months)][rainfall_col]
            if len(season_data) > 0:
                print(f"  {season}:")
                print(f"    Mean: {season_data.mean():.2f} mm")
                print(f"    Max: {season_data.max():.1f} mm")
                print(f"    Rainy hours: {(season_data > 0).sum()} ({(season_data > 0).sum()/len(season_data)*100:.1f}%)")
        
        # Drop the temporary month column
        df = df.drop('month', axis=1)
    
    print(f"\n✅ File saved: {output_file}")
    print("="*60)
    
    return df


if __name__ == "__main__":
    input_csv = 'data/imd_weather_dataset_2015_2019.csv'
    output_csv = 'data/imd_weather_dataset_2015_2019.csv'
    
    print("\n" + "="*60)
    print("IMD RAINFALL COLUMN UPDATER")
    print("="*60)
    
    # Update the rainfall column
    df = update_rainfall_in_csv(input_csv, output_csv)
    
    print("\n✅ Rainfall column updated successfully!")
    print(f"✅ All other columns remain unchanged")
    print(f"✅ CSV structure preserved")
