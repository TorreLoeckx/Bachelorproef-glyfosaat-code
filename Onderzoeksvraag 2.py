import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
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

path_percelen = r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Shapefile\Landbouwgebruikspercelen_2024_Vlaanderen_WGS84.shp"
path_provincies = r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Shapefile\Provinciegrenzen.shp"

# --- STAP 2: RUIMTELIJKE JOIN ---
print("Laden van shapefiles...")
percelen = gpd.read_file(path_percelen)
provincies = gpd.read_file(path_provincies)

# CRS handmatig instellen op WGS84 (gezien de bestandsnaam) en omzetten naar Lambert 72
if percelen.crs is None:
    percelen.set_crs("EPSG:4326", inplace=True)
if provincies.crs is None:
    provincies.set_crs("EPSG:4326", inplace=True)

percelen = percelen.to_crs("EPSG:31370")
provincies = provincies.to_crs("EPSG:31370")

print("Middelpunten berekenen en koppelen aan provincies...")
percelen_pts = percelen.copy()
percelen_pts['geometry'] = percelen_pts.geometry.centroid

# Ruimtelijke join om de provincie NAAM aan de percelen toe te voegen
percelen_met_prov = gpd.sjoin(percelen_pts, provincies, how='left', predicate='within')

# Controleer welke ID kolom we moeten gebruiken (voorkom KeyError)
oidn_col = 'OIDN_left' if 'OIDN_left' in percelen_met_prov.columns else 'OIDN'
print(f"Gebruikte ID-kolom uit shapefile: {oidn_col}")

# Maak de opzoektabel OIDN -> Provincie
lookup = percelen_met_prov[[oidn_col, 'NAAM']].drop_duplicates(oidn_col)
lookup.columns = ['OIDN', 'Provincie']

# --- STAP 3: CSV DATA ANALYSEREN ---
stats_list = []

for file in csv_files:
    try:
        year = int(os.path.basename(file).split('_')[-1].replace('.csv', ''))
        print(f"Analyse jaar {year}...")
        
        df_csv = pd.read_csv(file, usecols=['OIDN', 'classification'])
        
        # Merge de provincie-info aan de CSV data
        merged = df_csv.merge(lookup, on='OIDN', how='inner')
        
        # Bereken proportie glyfosaat per provincie
        # We gebruiken een simpele lambda functie voor de berekening
        yearly_stats = merged.groupby('Provincie')['classification'].apply(
            lambda x: (x == 'glyphosate').sum() * 100 / len(x) if len(x) > 0 else 0
        ).reset_index()
        
        yearly_stats.columns = ['Provincie', 'Proportie']
        yearly_stats['Year'] = year
        stats_list.append(yearly_stats)
        
    except Exception as e:
        print(f"Fout bij jaar {file}: {e}")

# Alles samenvoegen voor de grafiek
full_stats = pd.concat(stats_list)

# --- STAP 4: PLOTTEN ---
plt.figure(figsize=(12, 7))

# Elke provincie krijgt een eigen lijn
for prov in full_stats['Provincie'].unique():
    subset = full_stats[full_stats['Provincie'] == prov].sort_values('Year')
    plt.plot(subset['Year'], subset['Proportie'], marker='o', label=prov, linewidth=2)

plt.title('Evolutie Glyfosaatgebruik per Provincie (2018-2025)', fontsize=14, fontweight='bold')
plt.ylabel('Proportie percelen verwijderd met glyfosaat (%)', fontsize=12)
plt.xlabel('Jaar', fontsize=12)
plt.xticks([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title="Provincies", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

print("Klaar! Grafiek wordt getoond.")
plt.show()
