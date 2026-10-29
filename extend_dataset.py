"""
Script to extend the climate dataset by 1 year following the existing pattern
"""
import pandas as pd
from datetime import datetime, timedelta

# Read existing data
df = pd.read_csv('data/sample_climate.csv')
df['date'] = pd.to_datetime(df['date'])

# Get the last date and values
last_date = df['date'].iloc[-1]
last_temp = df['temperature'].iloc[-1]
last_precip = df['precipitation'].iloc[-1]

# Create extended data for 1 year (365 days)
new_dates = []
new_temps = []
new_precips = []

current_date = last_date + timedelta(days=1)
current_temp = last_temp
current_precip = last_precip

# Generate data following the pattern
for i in range(365):
    new_dates.append(current_date)
    
    # Temperature increases by 0.3°C per day
    current_temp += 0.3
    new_temps.append(round(current_temp, 1))
    
    # Precipitation cycles through [0.0, 0.1, 0.2]
    precip_cycle = [0.0, 0.1, 0.2]
    current_precip = precip_cycle[(i + 1) % 3]
    new_precips.append(current_precip)
    
    current_date += timedelta(days=1)

# Create new dataframe with extended data
new_data = pd.DataFrame({
    'date': new_dates,
    'temperature': new_temps,
    'precipitation': new_precips
})

# Combine original and new data
extended_df = pd.concat([df, new_data], ignore_index=True)

# Save the extended dataset
extended_df.to_csv('data/sample_climate.csv', index=False)

print(f"Dataset extended!")
print(f"Original data: {len(df)} rows")
print(f"New data added: {len(new_data)} rows")
print(f"Total rows: {len(extended_df)} rows")
print(f"Date range: {extended_df['date'].min()} to {extended_df['date'].max()}")
print(f"Temperature range: {extended_df['temperature'].min():.1f}°C to {extended_df['temperature'].max():.1f}°C")
print(f"Precipitation range: {extended_df['precipitation'].min():.1f} to {extended_df['precipitation'].max():.1f}")
