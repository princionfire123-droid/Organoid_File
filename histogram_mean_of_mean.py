#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script histogram_mean_of_mean.ipynb')


# In[4]:


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -------- INPUT PATH --------
input_csv_path = Path("/NAS2/Nikita/histogram_mean_nikk/mean_delta_d_summary.csv")

# -------- OUTPUT PATH --------
output_image_path = Path("/NAS2/Nikita/histogram_mean_nikk/less_now_mean_of_mean_histogram.png")

# -------- LOAD DATA --------
df = pd.read_csv(input_csv_path)

# -------- FOV -> ORGANOID MAPPING --------
fov_organoid_map = {
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

# -------- FILTER DATA --------
filtered_df = df.copy()

# Keep only valid FOVs in mapping
filtered_df = filtered_df[filtered_df["FOV"].isin(fov_organoid_map.keys())]

# Filter organoids per FOV
mask = filtered_df.apply(
    lambda row: row["Organoid"] in fov_organoid_map.get(row["FOV"], []),
    axis=1
)

filtered_df = filtered_df[mask]

# Extract values for histogram
data = filtered_df["Mean_mean_delta_d_um"].dropna()

# -------- DEBUG CHECK (optional) --------
print(f"Number of selected data points: {len(data)}")

# -------- PLOT HISTOGRAM --------
plt.figure(figsize=(8, 6))
plt.hist(data, bins=30)

plt.xlabel(r"Mean (Mean $\Delta d$ of Beads) per Organoid")
plt.ylabel("Frequency")
plt.title(r"Histogram of Mean (Mean $\Delta d$ of Beads) per Organoid")

# -------- SAVE FIGURE --------
output_image_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_image_path, dpi=300, bbox_inches='tight')

plt.show()

print(f"Histogram saved to: {output_image_path}")

