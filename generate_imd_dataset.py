"""
Generate realistic Indian Meteorological Department (IMD)-style weather dataset
for years 2015-2019 with hourly observations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

def generate_imd_weather_dataset():
    """
    Generate realistic Indian weather dataset (2015-2019) with hourly frequency.
    
    Returns:
        DataFrame with columns: datetime, latitude, longitude, temperature, rainfall_mm
    """
    
    # Define Indian meteorological stations across different regions
    # (latitude, longitude, station_name, altitude_factor)
    stations = [
        (13.0827, 80.2707, "Chennai", 0.95),           # South
        (19.0760, 72.8777, "Mumbai", 0.98),            # West
        (28.7041, 77.1025, "Delhi", 1.02),             # North
        (31.5497, 74.3436, "Amritsar", 1.05),          # Northwest
        (23.1815, 79.9864, "Indore", 1.01),            # Central
        (25.3176, 82.9739, "Varanasi", 1.03),          # East
        (34.0837, 74.7973, "Srinagar", 1.08),          # North (Kashmir)
        (19.0176, 72.8479, "Colaba (Mumbai)", 0.97),   # Central West
        (22.5726, 88.3639, "Kolkata", 0.96),           # East
        (17.3850, 78.4867, "Hyderabad", 0.99),         # South-Central
    ]
    
    # Generate hourly datetime range for 2015-2019
    start_date = pd.Timestamp('2015-01-01 00:00:00')
    end_date = pd.Timestamp('2019-12-31 23:59:59')
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    
    print(f"Generating dataset from {start_date} to {end_date}")
    print(f"Total hourly records: {len(date_range)}")
    print(f"Number of stations: {len(stations)}")
    print(f"Total records: {len(date_range) * len(stations)}")
    
    # Create list to store all records
    records = []
    
    for lat, lon, station_name, altitude_factor in stations:
        print(f"\nGenerating data for {station_name} ({lat}, {lon})...")
        
        for timestamp in date_range:
            # Extract temporal features
            month = timestamp.month
            day_of_year = timestamp.dayofyear
            hour = timestamp.hour
            
            # Calculate day within month (for daily cycle)
            day_of_month = timestamp.day
            
            # ===== TEMPERATURE GENERATION =====
            # Base temperature varies by latitude (realistic for India)
            base_temp = 35 - (abs(lat - 20) * 0.8)  # Cooler at extremes
            
            # Seasonal variation (sinusoidal pattern)
            # Peak in May-June, minimum in January
            seasonal_variation = 10 * np.sin((month - 3) * np.pi / 6) * altitude_factor
            
            # Daily cycle: warmest in afternoon (14-16), coolest before dawn (4-6)
            daily_variation = 8 * np.sin((hour - 6) * np.pi / 12)
            
            # Random noise and variability
            noise = np.random.normal(0, 0.5)
            
            # Combine all components
            temperature = base_temp + seasonal_variation + daily_variation + noise
            
            # Ensure realistic bounds for Indian climate
            temperature = np.clip(temperature, 10, 48)
            
            # ===== RAINFALL GENERATION =====
            # Indian monsoon pattern (June-September strong, March-May weak, Oct-Feb weak)
            
            if 6 <= month <= 9:
                # Monsoon season: June-September (strong rainfall)
                base_rainfall_prob = 0.4  # 40% chance of rain
                max_daily_rain = 150  # mm
                mean_rain = 40  # mm
            elif 3 <= month <= 5:
                # Pre-monsoon: March-May (weak rainfall, occasional thunderstorms)
                base_rainfall_prob = 0.15
                max_daily_rain = 80
                mean_rain = 15
            else:
                # Dry season: October-February and rest of year
                base_rainfall_prob = 0.08
                max_daily_rain = 40
                mean_rain = 5
            
            # Hourly rainfall varies with daily pattern
            # More rain during certain hours (typically afternoon/evening)
            hour_factor = np.sin((hour - 12) * np.pi / 12) * 1.5
            hour_factor = np.clip(hour_factor, 0.3, 1.5)
            
            # Decide if it rains this hour
            if np.random.random() < base_rainfall_prob / 24:  # Convert daily to hourly probability
                # Generate rainfall amount
                rainfall = np.random.exponential(mean_rain / 2) * hour_factor
                
                # Occasional extreme rainfall events (1-2% chance)
                if np.random.random() < 0.01:
                    rainfall = np.random.uniform(max_daily_rain * 0.5, max_daily_rain)
                
                rainfall = min(rainfall, max_daily_rain)
            else:
                rainfall = 0.0
            
            # Add slight spatial correlation: nearby hours similar rainfall
            if len(records) > 0 and records[-1]['datetime'] == timestamp - timedelta(hours=1):
                previous_rain = records[-1]['rainfall_mm']
                # 60% correlation with previous hour
                rainfall = 0.6 * previous_rain + 0.4 * rainfall
            
            # Ensure non-negative rainfall
            rainfall = max(0.0, rainfall)
            
            # Round to 1 decimal place for realism
            temperature = round(temperature, 1)
            rainfall = round(rainfall, 1)
            
            # Create record
            record = {
                'datetime': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'latitude': round(lat, 4),
                'longitude': round(lon, 4),
                'temperature': temperature,
                'rainfall_mm': rainfall
            }
            
            records.append(record)
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Verify data quality
    print("\n" + "="*60)
    print("DATA QUALITY CHECKS")
    print("="*60)
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Duplicate records: {df.duplicated().sum()}")
    print(f"\nTemperature stats:")
    print(f"  Min: {df['temperature'].min()}°C")
    print(f"  Max: {df['temperature'].max()}°C")
    print(f"  Mean: {df['temperature'].mean():.2f}°C")
    print(f"  Std Dev: {df['temperature'].std():.2f}°C")
    print(f"\nRainfall stats:")
    print(f"  Min: {df['rainfall_mm'].min()} mm")
    print(f"  Max: {df['rainfall_mm'].max():.1f} mm")
    print(f"  Mean: {df['rainfall_mm'].mean():.2f} mm")
    print(f"  Days with rain: {(df['rainfall_mm'] > 0).sum()} ({(df['rainfall_mm'] > 0).sum()/len(df)*100:.1f}%)")
    print(f"\nLatitudes: {df['latitude'].unique()}")
    print(f"Longitudes: {df['longitude'].unique()}")
    
    return df


def main():
    """Main function to generate and save the dataset."""
    
    print("\n" + "="*60)
    print("INDIAN METEOROLOGICAL DEPARTMENT (IMD) DATASET GENERATOR")
    print("="*60)
    print("Generating realistic weather data for 2015-2019")
    print("="*60 + "\n")
    
    # Generate dataset
    df = generate_imd_weather_dataset()
    
    # Save to CSV
    output_file = 'data/imd_weather_dataset_2015_2019.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n✓ Dataset saved to: {output_file}")
    print(f"✓ File size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Display sample
    print("\n" + "="*60)
    print("SAMPLE DATA")
    print("="*60)
    print("\nFirst 10 rows:")
    print(df.head(10).to_string(index=False))
    print("\nSample from mid-dataset:")
    print(df.iloc[len(df)//2:(len(df)//2)+10].to_string(index=False))
    print("\nSample monsoon season (July 2017):")
    july_2017 = df[(df['datetime'] >= '2017-07-01') & 
                   (df['datetime'] < '2017-07-02') &
                   (df['latitude'] == df['latitude'].iloc[0])].head(10)
    print(july_2017.to_string(index=False))
    
    print("\n" + "="*60)
    print("✓ Dataset generation complete!")
    print("="*60 + "\n")
    
    return df


if __name__ == "__main__":
    df = main()
