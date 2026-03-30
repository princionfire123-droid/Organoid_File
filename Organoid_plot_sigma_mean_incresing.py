#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script Organoid_plot_sigma_mean_incresing.ipynb')


# In[8]:


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -------- PATHS --------
input_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads")
output_root = Path("/NAS2/Nikita/all_beads_organoid_nikita")
output_root.mkdir(parents=True, exist_ok=True)

# -------- FULL SELECTION --------
selection = {
    "00_01_05": [9],
    "00_01_06": [25],
    "00_02_04": [22],
    "00_02_05": [30],
    "00_02_06": [99, 75, 77, 125],
    "00_02_07": [2, 52, 50, 53],
    "00_02_08": [39, 78, 46, 76],
    "00_03_03": [7, 10],
    "00_03_04": [4, 85, 80, 37],
    "00_03_05": [6, 73, 66, 48, 29],
    "00_03_06": [10, 26, 22, 41],
    "00_03_08": [15, 5],
    "00_03_10": [7],
    "00_04_02": [28, 25, 20],
    "00_04_03": [1, 13, 115],
    "00_04_04": [21, 24, 79, 51],
    "00_04_05": [21],
    "00_04_06": [103],
    "00_04_07": [40, 38, 37, 42, 35],
    "00_04_08": [3, 10],
    "00_04_09": [111, 166, 29],
    "00_04_10": [51, 15, 24, 30, 39],
    "00_05_02": [40, 26, 50, 24, 38],
    "00_05_03": [9, 10, 20],
    "00_05_04": [2, 52],
    "00_05_05": [79, 40, 69, 45, 88],
    "00_05_06": [4, 33],
    "00_05_07": [15, 28],
    "00_05_09": [97, 112, 123, 119, 71, 105],
    "00_05_11": [100, 19],
    "00_06_02": [30],
    "00_06_03": [25, 24],
    "00_06_04": [25, 12, 52, 29],
    "00_06_05": [40],
    "00_06_06": [56, 97, 87, 99],
    "00_06_07": [105, 180],
    "00_06_08": [8],
    "00_06_09": [42, 24, 88, 97, 62],
    "00_06_10": [99, 78, 66, 55, 85, 41, 81, 50, 80],
    "00_06_11": [49],
    "00_07_03": [32],
    "00_07_04": [13, 39],
    "00_07_05": [11, 29, 20, 67],
    "00_07_06": [32, 27, 34],
    "00_07_07": [90, 5, 97],
    "00_07_08": [55],
    "00_07_09": [21, 37, 39, 48],
    "00_07_10": [66, 89, 44, 83, 38],
    "00_07_11": [2, 25],
    "00_08_02": [6, 50],
    "00_08_03": [27, 16, 15, 106],
    "00_08_04": [1, 12],
    "00_08_05": [41, 95, 2, 46, 81],
    "00_08_07": [93, 22, 91, 5, 9],
    "00_08_08": [29, 19],
    "00_08_09": [65, 57, 64],
    "00_08_10": [107, 140, 49, 53, 85, 56],
    "00_09_03": [24, 23],
    "00_09_04": [24, 53, 50, 49]
}

# -------- HELPERS --------
def extract_fov(folder_name):
    parts = folder_name.split("_")
    return "_".join(parts[:3])

def extract_organoid(folder_name):
    try:
        num = folder_name.lower().replace("organoid_", "")
        return int(float(num))
    except:
        return None

# -------- COLLECT --------
organoid_data = []

for csv_file in input_root.rglob("*.csv"):
    try:
        fov_folder = csv_file.parents[1].name
        organoid_folder = csv_file.parent.name

        fov_key = extract_fov(fov_folder)
        organoid_id = extract_organoid(organoid_folder)

        if fov_key not in selection:
            continue
        if organoid_id not in selection[fov_key]:
            continue

        print(f"Matched: {fov_key} | Organoid {organoid_id}")

        df = pd.read_csv(csv_file)

        if not all(col in df.columns for col in
                   ["particle_id", "mean_delta_d_um", "sigma_delta_d_um"]):
            continue

        organoid_mean = df["mean_delta_d_um"].mean()

        organoid_data.append({
            "df": df,
            "mean": organoid_mean
        })

    except Exception as e:
        print(f"Error: {csv_file} -> {e}")

print(f"\nTotal organoids loaded: {len(organoid_data)}")

# -------- PLOT --------
if len(organoid_data) == 0:
    print("No data found - check paths")
    exit()

# sort by mean
organoid_data = sorted(organoid_data, key=lambda x: x["mean"])

plt.figure(figsize=(28, 10))

current_x = 0

for org in organoid_data:
    df = org["df"]
    n = len(df)

    x = list(range(current_x, current_x + n))

    plt.errorbar(
        x,
        df["mean_delta_d_um"],
        yerr=df["sigma_delta_d_um"],
        fmt='o',
        markersize=3,
        capsize=2
    )

    plt.axvline(x=current_x - 0.5, linestyle='--', linewidth=0.5)

    current_x += n + 1

plt.axvline(x=current_x - 0.5, linestyle='--', linewidth=0.5)

plt.xlabel("Beads")
plt.ylabel("Δd (μm)")
plt.title("Mean Δd ± σ of Beads Across Organoids")

# ✅ ONLY CHANGE YOU ASKED
plt.xticks([])

plt.tight_layout()

output_file = output_root / "final_sorted_plot.png"
plt.savefig(output_file, dpi=300)
plt.close()

print(f"\nPlot saved at: {output_file}")

