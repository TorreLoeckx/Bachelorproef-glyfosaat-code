import pandas as pd

# 1. Load the statistics data
# Using decimal='.' here ensures it reads your fixed-format CSV perfectly
df = pd.read_csv('Statistics_Vlaanderen_2024.csv', sep=',', decimal='.')

# 2. Data Cleaning (Safe Version)
# Only use string replacement if the data was loaded as text (Object)
for col in ['max_ndvi', 'total_slope_ndvi', 'max_slope_psri']:
    if df[col].dtype == 'object':
        df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
    else:
        # If already numeric, just ensure it's a float
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. Rename columns to match your decision tree logic
df = df.rename(columns={
    'max_ndvi': 'mean_ndvi_max',
    'total_slope_ndvi': 'mean_ndvi_total_slope',
    'max_slope_psri': 'mean_psri_max_slope'
})

# 4. Define your Decision Tree Logic
def classify_parcel(row):
    # Check for NaN to avoid errors
    if pd.isna(row['mean_ndvi_max']):
        return 'unknown'
        
    if row['mean_ndvi_max'] < 0.575:
        return 'bare'
    else:
        if row['mean_ndvi_total_slope'] > -0.00315:
            return 'green'
        else:
            if row['mean_psri_max_slope'] < 0.0472:
                return 'glyphosate'
            else:
                return 'mechanical'

# 5. Apply classification and save
df['classification'] = df.apply(classify_parcel, axis=1)

# Added float_format here as well to keep your classified file clean
df.to_csv('Classified_Parcels_Vlaanderen_2024.csv', index=False, float_format='%.8f')

# Display Summary
print(df['classification'].value_counts())
percentages = df['classification'].value_counts(normalize=True) * 100
print(percentages)
