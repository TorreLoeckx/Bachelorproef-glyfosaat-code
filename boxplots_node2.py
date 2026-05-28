import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as ticker  # Added for tick control

# 1. LOAD THE DATA (Now using the filtered node2 data)
df = pd.read_csv('analysis_node2.csv')

# 2. SETUP OUTPUT
output_folder = 'boxplots_node2'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. SETTINGS
# Removed 'bare' from order and palette
custom_order = ['green', 'glyphosate', 'mechanical']
color_palette = {'green': 'green', 'mechanical': 'orange', 'glyphosate': 'red'}

stats = ['max', 'min', 'mean', 'median', 'cv', 'max_slope', 'min_slope', 'total_slope', 'max_abs_rolling_slope']
indices = ['mean_ndvi', 'mean_ireci', 'mean_ccci', 'mean_pssr', 'mean_cari', 
           'mean_cri', 'mean_mari', 'mean_cri2', 'mean_psri', 'mean_ndre', 
           'mean_ndmi', 'mean_nbr2']

# 4. GENERATE DETAILED BOXPLOTS
for idx in indices:
    for stat in stats:
        col_name = f"{idx}_{stat}"
        if col_name not in df.columns:
            continue
        
        # --- FEATURE CLEANING (1.5 * IQR) ---
        cleaned_data_list = []
        for p_type in custom_order:
            category_group = df[df['parcel_type'] == p_type][col_name].dropna()
            if not category_group.empty:
                q1, q3 = category_group.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                filtered = category_group[(category_group >= lower) & (category_group <= upper)]
                cleaned_data_list.append(pd.DataFrame({'parcel_type': p_type, col_name: filtered}))
        
        if not cleaned_data_list: 
            continue
            
        plot_df = pd.concat(cleaned_data_list)
        
        # --- DETAILED PLOTTING ---
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.boxplot(
            data=plot_df, x='parcel_type', y=col_name, 
            order=custom_order, palette=color_palette, showfliers=False, ax=ax
        )
        
        # DETAIL ADJUSTMENT: Add 9 minor lines between major ticks
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(10))
        
        # Customize the Grid
        ax.grid(which='major', axis='y', linestyle='--', linewidth=0.8, color='gray', alpha=0.7)
        ax.grid(which='minor', axis='y', linestyle=':', linewidth=0.8, color='lightgray', alpha=0.5)
        
        plt.title(f"{idx.replace('mean_', '').upper()} - {stat.upper()}", fontsize=14)
        plt.ylabel('Value', fontsize=12)
        plt.xlabel('Parcel Category', fontsize=12)
        
        # Save plot
        plt.savefig(os.path.join(output_folder, f"{col_name}.png"), dpi=200)
        plt.close()