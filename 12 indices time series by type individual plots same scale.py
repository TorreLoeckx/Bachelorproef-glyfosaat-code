import matplotlib
matplotlib.use('Agg') # Essential to prevent MemoryError

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import gc

# 1. Load data
df = pd.read_csv('Indices_all_parcels.csv')
df['date'] = pd.to_datetime(df['date'])

# 2. INPUT SETTINGS
target_category = 'glyphosate'  # Options: 'glyphosate', 'mechanical', 'green', 'bare'
colors = {'glyphosate': 'red', 'mechanical': 'orange', 'green': 'green', 'bare': 'brown'}
chosen_color = colors.get(target_category, 'blue')

# 3. MANUAL SCALE LIMITS
# Adjust these values based on your knowledge of the indices to exclude outliers
custom_limits = {
    'mean_ndvi':  (0.0, 1.0),
    'mean_ireci': (0.0, 2.5),
    'mean_ccci':  (0.4, 0.8),
    'mean_pssr':  (0.0, 25.0),
    'mean_cari':  (0.0, 5.0),
    'mean_cri':   (-0.5, 14.0),
    'mean_mari':  (0.0, 4.0),
    'mean_cri2':  (-0.5, 18.0),
    'mean_psri':  (-0.1, 0.4),
    'mean_ndre':  (0.05, 0.75),
    'mean_ndmi':  (-0.2, 0.6),
    'mean_nbr2':  (0.0, 0.4)
}

indices = list(custom_limits.keys())
base_folder = 'plots_all_parcels_same_scale'
sns.set_style("whitegrid")

# 4. Filter data
df_filtered = df[df['parcel_type'] == target_category].copy()

if df_filtered.empty:
    print(f"No data found for category: {target_category}")
else:
    print(f"Generating plots with manual scales for {target_category}...")

    for index in indices:
        target_dir = os.path.join(base_folder, target_category, index)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        # Get your manual limits
        ymin, ymax = custom_limits[index]
        
        unique_parcels = df_filtered['plantation_id'].unique()
        
        for count, p_id in enumerate(unique_parcels):
            p_data = df_filtered[df_filtered['plantation_id'] == p_id].sort_values('date')
            p_data_clean = p_data.dropna(subset=[index])
            
            if p_data_clean.empty:
                continue

            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(111)
            
            # Plot
            ax.plot(p_data_clean['date'], p_data_clean[index], 
                    color=chosen_color, marker='o', linestyle='-', linewidth=1.5)
            
            # --- APPLY YOUR MANUAL LIMITS ---
            ax.set_ylim(ymin, ymax)
            
            # Date Formatting
            ax.set_xticks(p_data_clean['date'])
            ax.set_xticklabels(p_data_clean['date'].dt.strftime('%Y-%m-%d'), 
                               rotation=45, ha='right')
            
            clean_name = index.replace("mean_", "").upper()
            ax.set_title(f'Parcel: {p_id} | {target_category.capitalize()} | {clean_name}')
            ax.set_ylabel(f'{clean_name} Value')
            
            plt.tight_layout()
            
            # Save
            file_path = os.path.join(target_dir, f"{p_id}.png")
            fig.savefig(file_path, dpi=100)
            
            # Memory Management
            fig.clf()
            plt.close(fig)
            del fig, ax
            if count % 50 == 0:
                gc.collect()

        print(f"  - Completed: {index}")

    print(f"All {target_category} plots saved in: {base_folder}")

