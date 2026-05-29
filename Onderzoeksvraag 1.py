import pandas as pd
import matplotlib.pyplot as plt
import os

# --- STAP 1: BESTANDSPADEN ---
files = [
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

# --- STAP 2: DATA VERWERKEN ---
yearly_data = []

for file_path in files:
    if os.path.exists(file_path):
        try:
            filename = os.path.basename(file_path)
            year = int(filename.split('_')[-1].replace('.csv', ''))
            df = pd.read_csv(file_path, usecols=['classification'])
            counts = df['classification'].value_counts().reset_index()
            counts.columns = ['classification', 'count']
            counts['year'] = year
            yearly_data.append(counts)
        except Exception as e:
            print(f"Fout bij {file_path}: {e}")

if yearly_data:
    full_df = pd.concat(yearly_data).sort_values('year')
    
    plot_config = [
        {'id': 'green', 'title': 'Groene percelen', 'color': 'green'},
        {'id': 'glyphosate', 'title': 'Percelen verwijderd met glyfosaat', 'color': 'red'},
        {'id': 'bare', 'title': 'Kale bodem', 'color': 'brown'},
        {'id': 'mechanical', 'title': 'Mechanisch-verwijderde percelen', 'color': 'orange'}
    ]

    # --- FIGUUR 1: 4 APARTE SUBPLOTS (INDIVIDUELE SCHAAL) ---
    fig1, axes1 = plt.subplots(2, 2, figsize=(16, 12), dpi=500)
    fig1.suptitle('Evolutie van Perceelclassificaties in Vlaanderen', fontsize=20, fontweight='bold')
    axes_flat = axes1.flatten()

    for i, config in enumerate(plot_config):
        subset = full_df[full_df['classification'] == config['id']]
        if not subset.empty:
            axes_flat[i].plot(subset['year'], subset['count'], marker='o', 
                              color=config['color'], linewidth=2.5, markersize=8)
            axes_flat[i].set_title(config['title'], fontsize=14, fontweight='semibold')
            axes_flat[i].set_ylabel('Aantal percelen')
            axes_flat[i].set_xticks([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
            axes_flat[i].grid(True, linestyle='--', alpha=0.5)
            
            # Formatteer y-as voor leesbaarheid
            axes_flat[i].get_yaxis().set_major_formatter(
                plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)).replace(",", ".")))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # --- FIGUUR 2: GEALINEERDE PLOT (ALLES OP ÉÉN AS) ---
    plt.figure(figsize=(14, 10), dpi=500)
    
    for config in plot_config:
        subset = full_df[full_df['classification'] == config['id']]
        if not subset.empty:
            plt.plot(subset['year'], subset['count'], marker='o', label=config['title'],
                     color=config['color'], linewidth=3, markersize=10)

    plt.title('Evolutie van Perceelclassificaties in Vlaanderen (gelijke schaal)', fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('Jaar', fontsize=14)
    plt.ylabel('Aantal percelen', fontsize=14)
    plt.xticks([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])
    
    # Formatteer y-as met punten
    plt.gca().get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)).replace(",", ".")))
    
    plt.legend(fontsize=12, loc='upper right', bbox_to_anchor=(1.0, 1.015))
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    
    # Toon beide figuren
    plt.show()
else:
    print("Geen data gevonden om te plotten.")
