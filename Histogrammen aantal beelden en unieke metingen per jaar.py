import pandas as pd
import matplotlib.pyplot as plt

files = {
    year: rf"C:\Users\Administrator\OneDrive - Vrije Universiteit Brussel\3de bachelor\Bachelorproef\Nieuwe data\Landbouwgebruikspercelen (Vlaanderen)\Landbouwgebruikspercelen_2024\Indices_Vlaanderen_{year}.csv"
    for year in range(2018, 2026)
}

for year, path in files.items():
    print(f"Verwerken: {year}...")
    df = pd.read_csv(path, usecols=['OIDN', 'date'])
    meetpunten_per_perceel = df.groupby('OIDN')['date'].count()

    plt.figure(figsize=(10, 6), dpi=150)
    plt.hist(meetpunten_per_perceel, bins=range(1, meetpunten_per_perceel.max() + 2),
             color='steelblue', edgecolor='white', align='left')
    plt.title(f'Aantal meetpunten per perceel — {year}', fontsize=14, fontweight='bold')
    plt.xlabel('Aantal meetpunten', fontsize=12)
    plt.ylabel('Aantal percelen', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', '.')))
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(f'meetpunten_{year}.png', dpi=150, bbox_inches='tight')
    plt.show()

print("Klaar.")