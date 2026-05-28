import pandas as pd
import numpy as np

# 1. Load the data
df = pd.read_csv('Indices_Vlaanderen_2019.csv', sep=',', decimal='.')

# 2. Data Cleaning
for col in ['ndvi', 'psri']:
    if df[col].dtype == 'object':
        df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['date'] = pd.to_datetime(df['date'], dayfirst=True, format='mixed', errors='coerce')

# 3. Filter and Sort
df = df.dropna(subset=['date'])
df = df.groupby('OIDN').filter(lambda x: len(x) > 1)
df = df.sort_values(['OIDN', 'date'])

# --- PROGRESS TRACKING SETUP ---
grouped = df.groupby('OIDN')
total_parcels = len(grouped)
counter = 0

def calculate_parcel_stats(group):
    global counter
    counter += 1
    
    # Update display every 10,000 parcels
    if counter % 1000 == 0 or counter == total_parcels:
        percent = (counter / total_parcels) * 100
        print(f"Progress: {percent:.2f}% | Processed {counter:,} of {total_parcels:,} parcels", end='\r')

    # Calculation 1: Max NDVI
    max_ndvi = group['ndvi'].max()
    
    # Calculation 2: Total Slope NDVI
    time_delta_total = (group['date'].iloc[-1] - group['date'].iloc[0]).days
    if time_delta_total > 0:
        total_slope_ndvi = (group['ndvi'].iloc[-1] - group['ndvi'].iloc[0]) / time_delta_total
    else:
        total_slope_ndvi = 0
        
    # Calculation 3: Max Slope PSRI
    psri_diff = group['psri'].diff()
    days_diff = group['date'].diff().dt.days
    
    psri_slopes = psri_diff / days_diff.replace(0, np.nan)
    max_slope_psri = psri_slopes.max()
    
    return pd.Series({
        'max_ndvi': max_ndvi,
        'total_slope_ndvi': total_slope_ndvi,
        'max_slope_psri': max_slope_psri
    })

# 4. Run calculations
print(f"Starting analysis on {total_parcels:,} parcels...")
final_summary = grouped.apply(calculate_parcel_stats, include_groups=False).reset_index()
print("\nProcessing finished successfully.")

# 5. Save results
final_summary.to_csv('Statistics_Vlaanderen_2019.csv', index=False, float_format='%.8f')