import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# 1. LOAD DATA
# Ensure your 'analysis_node1.csv' file is in the same folder as this script
df = pd.read_csv('analysis_node1.csv')

# 2. MANUAL CLASSIFICATION LOGIC
def classify_parcel(row):
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

df['predicted_type'] = df.apply(classify_parcel, axis=1)

# 3. METRICS
accuracy = accuracy_score(df['parcel_type'], df['predicted_type'])
report = classification_report(df['parcel_type'], df['predicted_type'])
print(f"Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(report)

# 4. CONFUSION MATRIX VISUALIZATION (Interne logica Engels, Labels Nederlands)
# Dit zijn de labels die in je data (df) staan
english_classes = ['bare', 'green', 'glyphosate', 'mechanical']
# Dit zijn de vertalingen voor de figuur
dutch_labels = ['kaal', 'groen', 'glyfosaat', 'mechanisch']

cm = confusion_matrix(df['parcel_type'], df['predicted_type'], labels=english_classes)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=dutch_labels, yticklabels=dutch_labels) # Hier de NL labels
plt.xlabel('Voorspeld')
plt.ylabel('Werkelijk')
plt.savefig('Manual_Confusion_Matrix.png')
plt.show()


# 5. VISUALIZE MANUAL DECISION TREE (BALANCED VERSION)
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_axis_off()

# Palette to match previous analysis
color_map = {'bare': '#8B4513', 'green': '#228B22', 'glyphosate': '#FF0000', 'mechanical': '#FFA500'}

def draw_node(text, x, y, color='white', text_color='black'):
    bbox = dict(boxstyle="round,pad=0.6", fc=color, ec="black", lw=1.5)
    ax.text(x, y, text, ha='center', va='center', bbox=bbox, fontsize=10, color=text_color, fontweight='bold')

def draw_edge(start, end, label):
    ax.annotate('', xy=end, xycoords='data', xytext=start, textcoords='data',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3", lw=1.2))
    mid_x, mid_y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    ax.text(mid_x, mid_y + 0.02, label, ha='center', fontsize=9, fontweight='bold')

# --- Drawing the Balanced Tree ---
# Root - Centered at 0.5
draw_node("NDVI Max < 0.575?", 0.5, 0.9)

# Level 1: Split from Root
draw_edge((0.48, 0.86), (0.25, 0.74), "JUIST")
draw_node("KAAL", 0.25, 0.7, color=color_map['bare'], text_color='white')

draw_edge((0.52, 0.86), (0.75, 0.74), "FOUT")
draw_node("NDVI Totale Helling > -0.00315?", 0.75, 0.7)

# Level 2: Split from NDVI Slope
draw_edge((0.72, 0.66), (0.60, 0.54), "JUIST")
draw_node("GROEN", 0.60, 0.5, color=color_map['green'], text_color='white')

draw_edge((0.78, 0.66), (0.90, 0.54), "FOUT")
draw_node("PSRI Max Helling < 0.0472?", 0.90, 0.5)

# Level 3: Final Split
draw_edge((0.88, 0.46), (0.80, 0.34), "JUIST")
draw_node("GLYFOSAAT", 0.80, 0.3, color=color_map['glyphosate'], text_color='white')

draw_edge((0.92, 0.46), (1.00, 0.34), "FOUT")
draw_node("MECHANISCH", 1.00, 0.3, color=color_map['mechanical'], text_color='black')

plt.savefig('Manual_Decision_Tree.png', bbox_inches='tight', dpi=300)
plt.show()

# 6. EXPORT DATA
df.to_csv('analysis_with_predictions.csv', index=False)

# --- NEW: GROUPED CONFUSION MATRIX ---

# 1. Create a mapping for the grouping
group_map = {
    'bare': 'onbewerkt',
    'green': 'onbewerkt',
    'glyphosate': 'glyfosaat',
    'mechanical': 'mechanisch'
}

# 2. Apply mapping to both actual and predicted columns
df['parcel_type_grouped'] = df['parcel_type'].map(group_map)
df['predicted_type_grouped'] = df['predicted_type'].map(group_map)

# 3. Define new classes and calculate the matrix
grouped_classes = ['onbewerkt', 'glyfosaat', 'mechanisch']
cm_grouped = confusion_matrix(df['parcel_type_grouped'], 
                              df['predicted_type_grouped'], 
                              labels=grouped_classes)

# 4. Visualize Grouped Matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm_grouped, annot=True, fmt='d', cmap='Blues', 
            xticklabels=grouped_classes, yticklabels=grouped_classes)
plt.xlabel('Voorspeld')
plt.ylabel('Werkelijk')
plt.savefig('Grouped_Confusion_Matrix.png')
plt.show()

# Optional: Print metrics for the grouped version
print("\nGrouped Classification Report:")
print(classification_report(df['parcel_type_grouped'], df['predicted_type_grouped']))