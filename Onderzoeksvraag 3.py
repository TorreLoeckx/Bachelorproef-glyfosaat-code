import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os

# --- STAP 1: PADEN ---
csv_files = [
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2018.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2019.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2020.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2021.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2022.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2023.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2024.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2025.csv",
    r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Classified_Parcels_Vlaanderen_2026.csv"
]

path_percelen = r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Shapefile\Lbgbrprc24.shp"
path_provincies = r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Shapefile\Provinciegrenzen.shp"

# --- STAP 2: GEODATA & JOIN ---
print("Laden van shapefiles...")
percelen = gpd.read_file(path_percelen)
provincies = gpd.read_file(path_provincies)

if percelen.crs is None: percelen.set_crs("EPSG:4326", inplace=True)
if provincies.crs is None: provincies.set_crs("EPSG:4326", inplace=True)

percelen = percelen.to_crs("EPSG:31370")
provincies = provincies.to_crs("EPSG:31370")

print("Middelpunten berekenen en join uitvoeren...")
percelen_pts = percelen.copy()
percelen_pts['geometry'] = percelen_pts.geometry.centroid
joined = gpd.sjoin(percelen_pts, provincies, how='left', predicate='within')

oidn_col = 'OIDN_left' if 'OIDN_left' in joined.columns else 'OIDN'
lookup = joined[[oidn_col, 'NAAM']].drop_duplicates(oidn_col)
lookup.columns = ['OIDN', 'Provincie']

# --- STAP 3: FREQUENTIE ANALYSE ---
frequentie_dict = {}
print("CSV bestanden analyseren...")
for file in csv_files:
    if os.path.exists(file):
        df = pd.read_csv(file, usecols=['OIDN', 'classification'])
        glyph_ids = df[df['classification'] == 'glyphosate']['OIDN'].unique()
        for oidn in glyph_ids:
            frequentie_dict[oidn] = frequentie_dict.get(oidn, 0) + 1

if not frequentie_dict:
    print("FOUT: Geen glyfosaat-data gevonden.")
else:
    freq_df = pd.DataFrame(list(frequentie_dict.items()), columns=['OIDN', 'Jaren_Glyfosaat'])
    final_df = freq_df.merge(lookup, on='OIDN', how='inner')

    if not final_df.empty:
        # --- STAP 4: DESIGN A (Gegroepeerd met Rode Color Ramp) ---
        pivot_prov = final_df.groupby(['Provincie', 'Jaren_Glyfosaat']).size().unstack(fill_value=0).apply(pd.to_numeric)

        n_years = len(pivot_prov.columns)
        cmap = cm.get_cmap('Reds')
        colors_ramp = [cmap(i) for i in np.linspace(0.3, 0.9, n_years)]

        ax1 = pivot_prov.plot(kind='bar', figsize=(15, 8), width=0.8, color=colors_ramp)
        
        for container in ax1.containers:
            ax1.bar_label(container, padding=3, fontsize=8)

        plt.title('Glyfosaat-frequentie gegroepeerd per Provincie', fontsize=14, fontweight='bold')
        plt.ylabel('Aantal percelen')
        plt.xlabel('Provincie')
        plt.xticks(rotation=0)
        
        legend_labels = [f'{int(col)} Jaar' for col in pivot_prov.columns]
        plt.legend(title="Detectie-frequentie", labels=legend_labels, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        # --- STAP 5: DESIGN B (Gestapeld met Totalen) ---
        pivot_year = final_df.groupby(['Jaren_Glyfosaat', 'Provincie']).size().unstack(fill_value=0).apply(pd.to_numeric)
        pivot_year.index = [f'{int(i)} Jaar' for i in pivot_year.index]

        colors_prov = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        ax2 = pivot_year.plot(kind='bar', stacked=True, figsize=(12, 8), width=0.6, color=colors_prov)
        
        totals = pivot_year.sum(axis=1)
        for i, total in enumerate(totals):
            ax2.text(i, total + (total * 0.01), f'{int(total)}', ha='center', va='bottom', fontweight='bold')

        plt.title('Provinciale bijdrage gestapeld per Frequentie-categorie', fontsize=14, fontweight='bold')
        plt.ylabel('Totaal aantal unieke percelen')
        plt.xlabel('Aantal jaren glyfosaat gedetecteerd')
        plt.xticks(rotation=0)
        plt.legend(title="Provincies", bbox_to_anchor=(0.828, 1), loc='upper left')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        print("Beide grafieken succesvol gegenereerd!")
        plt.show()
        
        # CSV opslaan
        final_df.to_csv('frequentie_data_beide_designs.csv', index=False)
