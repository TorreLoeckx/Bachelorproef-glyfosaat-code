import pandas as pd
import numpy as np

# 1. LOAD THE DATA
df = pd.read_csv('Indices_all_parcels.csv')
df['date'] = pd.to_datetime(df['date'])

# 2. EXCLUDE HAND-PICKED PARCELS
parcels_to_exclude = [
    421473484, 418067774, 426232851, 434377013, 434420964,
    439004923, 439045945, 442425686, 442475806, 444549077,
    455329417, 456767845, 460977847, 460992702, 463196824,
    568424747, 576440280, 581181055, 588053002, 754688692,
    812268401, 813394207, 813394308, 814272762, 829782052,
    907335875, 921431288, 932201726, 935389487, 935480225, 
    938022534, 1000377467, 1001363433, 1003129641, 1003983039, 
    1117306321, 1122103171, 1316476623, 1424405590, 1747868864
]
df = df[~df['plantation_id'].isin(parcels_to_exclude)]

# 3. PRE-PROCESS: HANDLE MULTIPLE MEASUREMENTS PER DATE
indices_cols = [col for col in df.columns if col.startswith('mean_')]
df = df.groupby(['plantation_id', 'date', 'parcel_type'], as_index=False)[indices_cols].max()

# 4. FEATURE EXTRACTION
final_data = []

for p_id, p_df in df.groupby('plantation_id'):
    p_df = p_df.sort_values('date')
    parcel_features = {
        'plantation_id': p_id,
        'parcel_type': p_df['parcel_type'].iloc[0]
    }
    
    for idx in indices_cols:
        idx_df = p_df[['date', idx]].dropna()
        if len(idx_df) < 1:
            continue
            
        values = idx_df[idx].values
        dates = idx_df['date']
        
        # Stats
        parcel_features[f'{idx}_max'] = np.nanmax(values)
        parcel_features[f'{idx}_min'] = np.nanmin(values)
        parcel_features[f'{idx}_mean'] = np.nanmean(values)
        parcel_features[f'{idx}_median'] = np.nanmedian(values)
        parcel_features[f'{idx}_cv'] = (np.nanstd(values) / np.nanmean(values)) if np.nanmean(values) != 0 else 0
        
        # Slopes
        if len(idx_df) >= 2:
            delta_days = (dates.diff().dt.total_seconds() / (24*3600)).values[1:]
            slopes = np.diff(values) / delta_days
            parcel_features[f'{idx}_max_slope'] = np.nanmax(slopes)
            parcel_features[f'{idx}_min_slope'] = np.nanmin(slopes)
            
            total_days = (dates.iloc[-1] - dates.iloc[0]).days
            parcel_features[f'{idx}_total_slope'] = (values[-1] - values[0]) / total_days if total_days > 0 else 0
            
            if len(slopes) >= 2:
                moving_avg_slopes = (slopes[:-1] + slopes[1:]) / 2
                parcel_features[f'{idx}_max_abs_rolling_slope'] = np.nanmax(np.abs(moving_avg_slopes))
            else:
                parcel_features[f'{idx}_max_abs_rolling_slope'] = np.abs(slopes[0])
                
    final_data.append(parcel_features)

# 5. EXPORT
classifier_df = pd.DataFrame(final_data)
custom_order = ['bare', 'green', 'glyphosate', 'mechanical']
classifier_df['parcel_type'] = pd.Categorical(classifier_df['parcel_type'], categories=custom_order, ordered=True)
classifier_df = classifier_df.sort_values(by=['parcel_type', 'plantation_id'])

classifier_df.to_csv('analysis_node1.csv', index=False)

