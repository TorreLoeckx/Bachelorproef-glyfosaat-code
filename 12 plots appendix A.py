import matplotlib
matplotlib.use('Agg') # Essential to prevent MemoryErrors within loops

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import gc

# 1. Load data
df = pd.read_csv('Indices_all_parcels.csv')
df['date'] = pd.to_datetime(df['date'])

# 2. DEFINITIVE PARCEL CONFIGURATION (2024 Only)
parcels_2024 = {
    'glyphosate': 2211762169,  # Your chosen glyphosate parcel for 2024
    'mechanical': 936452245,
    'green':      437686935,
    'bare':       448441710
}

# Color palette mapped to categories (from your original code)
colors = {
    'glyphosate': 'red', 
    'mechanical': 'orange', 
    'green':      'green', 
    'bare':       'brown'
}

# 3. MANUAL SCALE LIMITS (from your original code)
custom_limits = {
    'mean_ndvi':  (0.0, 1.0),
    'mean_ireci': (0.0, 3.5),
    'mean_ccci':  (0.4, 0.8),
    'mean_pssr':  (0.0, 25.0),
    'mean_cari':  (0.0, 6.0),
    'mean_cri':   (-0.5, 12.0),
    'mean_mari':  (0.0, 4.0),
    'mean_cri2':  (-0.5, 15.0),
    'mean_psri':  (-0.1, 0.5),
    'mean_ndre':  (0.05, 0.75),
    'mean_ndmi':  (-0.2, 0.6),
    'mean_nbr2':  (0.0, 0.4)
}

output_folder = 'AppendixA_plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize Seaborn whitegrid style for a clean scientific appearance
sns.set_style("whitegrid")

print("Generating the 12 combined plots for 2024...")

# Loop over the 12 spectral indices
for index in custom_limits.keys():
    ymin, ymax = custom_limits[index]
    clean_index_name = index.replace("mean_", "").upper()
    
    # Create 1 central plot per index
    fig, ax = plt.subplots(figsize=(12, 6))
    
    plotted_any = False
    
    # Loop through the 4 categories and plot them onto the same graph
    for cat, p_id in parcels_2024.items():
        # Filter data for this specific parcel in 2024
        p_data = df[(df['plantation_id'] == p_id) & (df['date'].dt.year == 2024)].sort_values('date')
        
        # Remove rows where this specific index is NaN (e.g., due to clouds)
        p_data_clean = p_data.dropna(subset=[index])
        
        if p_data_clean.empty:
            continue
            
        # Plot the time-series line for this parcel
        ax.plot(p_data_clean['date'], p_data_clean[index], 
                color=colors[cat], marker='o', linestyle='-', linewidth=1.8, markersize=5,
                label=f"{cat.capitalize()} (ID: {p_id})")
        
        plotted_any = True

    if not plotted_any:
        print(f"  [Warning] No lines could be plotted for index {clean_index_name}")
        plt.close(fig)
        continue

    # Apply manual Y-axis limits
    ax.set_ylim(ymin, ymax)
    
    # Extract all unique 2024 dates from the dataset for a consistent X-axis timeline
    dates_2024 = df[df['date'].dt.year == 2024]['date'].unique()
    unique_dates = sorted(dates_2024)
    
    ax.set_xticks(unique_dates)
    ax.set_xticklabels([pd.to_datetime(d).strftime('%Y-%m-%d') for d in unique_dates], 
                       rotation=45, ha='right', fontsize=9)
    
    # Set titles and axis labels in English
    ax.set_title(f'Time-Series Analysis: Comparison of {clean_index_name} Index by Parcel Category', 
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel(f'{clean_index_name} Value', fontsize=11)
    ax.set_xlabel('Observation Date', fontsize=11)
    
    # Add legend to the optimal empty space
    ax.legend(loc='best', frameon=True, facecolor='white', edgecolor='0.8')
    
    plt.tight_layout()
    
    # Save the combined figure
    file_path = os.path.join(output_folder, f"AppendixA_{clean_index_name}_Comparison.png")
    fig.savefig(file_path, dpi=150)
    
    # Explicit memory cleanup
    fig.clf()
    plt.close(fig)
    del fig, ax
    gc.collect()

    print(f"  - Successfully generated: AppendixA_{clean_index_name}_Comparison.png")

print(f"\nFinished! All 12 charts for 2024 are saved in the directory: '{output_folder}'")