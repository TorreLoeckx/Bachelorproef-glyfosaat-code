import pandas as pd
import matplotlib.pyplot as plt
import os

# --- STAP 1: PADEN ---
base_path = r"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024"

jaren_merged = [2023, 2024]
provincies = ['A', 'L', 'OV', 'VB', 'WV']

# --- STAP 2: DATA INLADEN ---
print("Data inladen...")
all_records = []

for year in range(2018, 2027):
    print(f"Verwerken: {year}...")

    if year in jaren_merged:
        path = rf"{base_path}\Indices_Vlaanderen_{year}.csv"
        df = pd.read_csv(path, usecols=['OIDN'])
    else:
        dfs = []
        for prov in provincies:
            path = rf"{base_path}\Indices_{prov}_{year}.csv"
            if os.path.exists(path):
                dfs.append(pd.read_csv(path, usecols=['OIDN']))
        df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=['OIDN'])

    df['year'] = year
    all_records.append(df)

full_df = pd.concat(all_records, ignore_index=True)

# --- STAP 3: AANTAL JAREN PER PERCEEL ---
jaren_per_perceel = full_df.groupby('OIDN')['year'].nunique()
totaal = len(jaren_per_perceel)

# --- STAP 4: HISTOGRAM ---
plt.figure(figsize=(10, 6), dpi=150)
bars = plt.bar(range(1, 10), 
               [len(jaren_per_perceel[jaren_per_perceel == i]) for i in range(1, 10)],
               color='steelblue', edgecolor='white', width=0.6)

for bar in bars:
    val = int(bar.get_height())
    if val > 0:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
                 f'{val:,}'.replace(',', '.'),
                 ha='center', va='bottom', fontsize=9)

plt.title(f'Aantal jaren dat een perceel in de analyse werd opgenomen (2018–2026)\n'
          f'Totaal aantal unieke percelen: {totaal:,}'.replace(',', '.'),
          fontsize=13, fontweight='bold')
plt.xlabel('Aantal jaren', fontsize=12)
plt.ylabel('Aantal percelen', fontsize=12)
plt.xticks(range(1, 10))
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', '.')))
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('jaren_per_perceel.png', dpi=150, bbox_inches='tight')
plt.show()

print("Klaar.")