#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script all_organoid_SD_mean_delta_d_plot_19_march.ipynb')


# In[1]:


import os
print(os.getcwd())


# In[1]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/sigma_by_mean"
output_root = "/NAS2/Nikita/plot_sigma_by_mean"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR FULL SELECTION ----
selected_data = {
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

# ---- LOAD DATA ----
data_cache = {}
all_x, all_y = [], []
ordered_keys = []

for fov_prefix, organoid_numbers in selected_data.items():
    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:
            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
            if not csv_files:
                continue

            key = (fov, organoid_num)
            ordered_keys.append(key)
            data_cache[key] = []

            for csv_file in csv_files:
                df = pd.read_csv(os.path.join(organoid_path, csv_file))

                x = df["mean_delta_d_um"]
                y = df["sigma_over_mean"]

                valid = np.isfinite(x) & np.isfinite(y)
                x_clean = x[valid]
                y_clean = y[valid]

                if len(x_clean) == 0:
                    continue

                data_cache[key].append((x_clean, y_clean))
                all_x.extend(x_clean)
                all_y.extend(y_clean)

# ---- FIXED SCALE (0 to 2) ----
x_min, x_max = 0, 2
y_min, y_max = 0, 2

# ---- GROUP INTO 10 PER PLOT ----
groups = [ordered_keys[i:i+10] for i in range(0, len(ordered_keys), 10)]

# ---- PLOTTING ----
for idx, group in enumerate(groups):
    plt.figure(figsize=(8, 8))

    cmap = plt.get_cmap('tab20', len(group))

    for i, key in enumerate(group):
        fov, organoid_num = key
        color = cmap(i)

        for x_clean, y_clean in data_cache[key]:

            # ---- FILTER ONLY 0–2 RANGE ----
            mask = (
                (x_clean >= 0) & (x_clean <= 2) &
                (y_clean >= 0) & (y_clean <= 2)
            )

            plt.scatter(
                x_clean[mask],
                y_clean[mask],
                s=5,
                color=color,
                alpha=0.6,
                label=f"{fov} | Org {organoid_num}"
            )

    plt.xlim(0, 2)
    plt.ylim(0, 2)

    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("sigma_over_mean (µm)")
    plt.title(f"Organoids {idx*10+1}–{idx*10+len(group)}")

    handles, labels = plt.gca().get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    plt.legend(unique.values(), unique.keys(), fontsize=6, bbox_to_anchor=(1.05, 1))

    save_path = os.path.join(output_root, f"plot_{idx+1}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {save_path}")

print("All plots generated successfully.")


# In[2]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/final_mean_delta/2x2_SD_mean_delta_d_all_organoid_plot"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR FULL SELECTION ----
selected_data = {
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

# ---- LOAD DATA ----
data_cache = {}
all_x, all_y = [], []

ordered_keys = []

for fov_prefix, organoid_numbers in selected_data.items():
    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:
            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
            if not csv_files:
                continue

            key = (fov, organoid_num)
            ordered_keys.append(key)
            data_cache[key] = []

            for csv_file in csv_files:
                df = pd.read_csv(os.path.join(organoid_path, csv_file))

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]

                valid = np.isfinite(x) & np.isfinite(y)
                x_clean = x[valid]
                y_clean = y[valid]

                if len(x_clean) == 0:
                    continue

                data_cache[key].append((x_clean, y_clean))
                all_x.extend(x_clean)
                all_y.extend(y_clean)

# ---- GLOBAL SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

mask = np.isfinite(all_x) & np.isfinite(all_y)
all_x = all_x[mask]
all_y = all_y[mask]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

x_margin = 0.05 * (x_max - x_min)
y_margin = 0.05 * (y_max - y_min)

# ---- GROUP INTO 10 PER PLOT ----
groups = [ordered_keys[i:i+10] for i in range(0, len(ordered_keys), 10)]

# ---- PLOTTING ----
for idx, group in enumerate(groups):
    plt.figure(figsize=(8, 8))

    cmap = plt.get_cmap('tab20', len(group))  # distinct colors

    for i, key in enumerate(group):
        fov, organoid_num = key
        color = cmap(i)

        for x_clean, y_clean in data_cache[key]:

            mask = (
                (x_clean >= x_min) & (x_clean <= x_max) &
                (y_clean >= y_min) & (y_clean <= y_max)
            )

            plt.scatter(
                x_clean[mask],
                y_clean[mask],
                s=5,
                color=color,
                alpha=0.6,
                label=f"{fov} | Org {organoid_num}"
            )

    plt.xlim(x_min - x_margin, x_max + x_margin)
    plt.ylim(y_min - y_margin, y_max + y_margin)

    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Organoids {idx*10+1}–{idx*10+len(group)}")

    # remove duplicate legend entries
    handles, labels = plt.gca().get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    plt.legend(unique.values(), unique.keys(), fontsize=6, bbox_to_anchor=(1.05, 1))

    save_path = os.path.join(output_root, f"plot_{idx+1}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {save_path}")

print("All plots generated successfully.")


# In[1]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/2x2_SD_mean_all_organoid_plot"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR FULL SELECTION ----
selected_data = {
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

# ---- LOAD DATA ----
data_cache = {}
all_x, all_y = [], []

for fov_prefix, organoid_numbers in selected_data.items():
    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:
            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
            if not csv_files:
                continue

            key = (fov, organoid_num)
            data_cache[key] = []

            for csv_file in csv_files:
                df = pd.read_csv(os.path.join(organoid_path, csv_file))

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]

                valid = np.isfinite(x) & np.isfinite(y)
                x_clean = x[valid]
                y_clean = y[valid]

                if len(x_clean) == 0:
                    continue

                data_cache[key].append((x_clean, y_clean))
                all_x.extend(x_clean)
                all_y.extend(y_clean)

# ---- GLOBAL SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

mask = np.isfinite(all_x) & np.isfinite(all_y)
all_x = all_x[mask]
all_y = all_y[mask]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

x_margin = 0.05 * (x_max - x_min) if x_max != x_min else 0.1
y_margin = 0.05 * (y_max - y_min) if y_max != y_min else 0.1

# ---- GROUP INTO 4 PER FIGURE ----
valid_keys = list(data_cache.keys())
groups = [valid_keys[i:i+4] for i in range(0, len(valid_keys), 4)]

# ---- PLOTTING ----
for idx, group in enumerate(groups):
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes = axes.flatten()

    for ax_i, key in enumerate(group):
        ax = axes[ax_i]
        fov, organoid_num = key

        color = plt.get_cmap('tab10')(ax_i)

        for x_clean, y_clean in data_cache[key]:

            mask = (
                (x_clean >= x_min) & (x_clean <= x_max) &
                (y_clean >= y_min) & (y_clean <= y_max)
            )

            ax.scatter(
                x_clean[mask],
                y_clean[mask],
                s=5,
                color=color,
                alpha=0.6,
                label=f"{fov} | Org {organoid_num}"
            )

        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)

        ax.set_xlabel("Mean Δd (µm)")
        ax.set_ylabel("Std Dev Δd (µm)")
        ax.set_title(f"{fov} | Organoid {organoid_num}", fontsize=9)

        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[:1], labels[:1], fontsize=7)

    for j in range(len(group), 4):
        fig.delaxes(axes[j])

    plt.tight_layout()
    save_path = os.path.join(output_root, f"plot_{idx+1}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"Saved: {save_path}")

print("All plots generated successfully.")


# In[19]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/final_mean_delta/correct_X_mean_Y_SD_beads_plots_selected_split10"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION ----
selected_data = {
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

# ---- STEP 1: LOAD ALL VALID DATA ----
data_cache = {}
all_x, all_y = [], []

for fov_prefix, organoid_numbers in selected_data.items():

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:
            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue  # skip missing

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            if len(csv_files) == 0:
                continue

            key = (fov_prefix, organoid_num)
            data_cache[key] = []

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)
                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]

                valid_mask = np.isfinite(x) & np.isfinite(y)
                x_clean = x[valid_mask]
                y_clean = y[valid_mask]

                if len(x_clean) == 0:
                    continue

                data_cache[key].append((x_clean, y_clean))

                all_x.extend(x_clean.tolist())
                all_y.extend(y_clean.tolist())

# ---- GLOBAL SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

mask = np.isfinite(all_x) & np.isfinite(all_y)
all_x = all_x[mask]
all_y = all_y[mask]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

x_margin = 0.05 * (x_max - x_min) if x_max != x_min else 0.1
y_margin = 0.05 * (y_max - y_min) if y_max != y_min else 0.1

# ---- GROUP INTO 10 ORGANOIDS PER PLOT ----
valid_keys = list(data_cache.keys())
groups = [valid_keys[i:i+10] for i in range(0, len(valid_keys), 10)]

# ---- PLOTTING ----
for idx, group in enumerate(groups):

    plt.figure(figsize=(8, 8))
    cmap = plt.get_cmap('tab10', len(group))

    for i, key in enumerate(group):
        fov_prefix, organoid_num = key
        color = cmap(i)

        for x_clean, y_clean in data_cache[key]:
            plt.scatter(x_clean, y_clean, color=color,
                        label=f"{fov_prefix}-org{organoid_num}" if i == 0 else "")

    # SAME SCALE
    plt.xlim(x_min - x_margin, x_max + x_margin)
    plt.ylim(y_min - y_margin, y_max + y_margin)

    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Beads Plot (Organoids {idx*10+1}–{idx*10+len(group)})")

    plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

    save_path = os.path.join(output_root, f"plot_{idx+1}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {save_path}")

print("All plots generated successfully (robust, no errors).")


# In[24]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/final_mean_delta/right_X_mean_Y_SD_beads_plots_selected_split10"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION (UNCHANGED) ----
selected_data = {
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
    "00_04_09": [111, 29],
    "00_04_10": [15, 24, 30, 39],
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
    "00_06_07": [105],
    "00_06_08": [8],
    "00_06_09": [42, 24, 88, 97, 62],
    "00_06_10": [78, 66, 55, 85, 41, 81, 50, 80],
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
    "00_08_03": [27, 16, 15],
    "00_08_04": [1, 12],
    "00_08_05": [41, 95, 2, 46, 81],
    "00_08_07": [93, 22, 91, 5, 9],
    "00_08_08": [29, 19],
    "00_08_09": [65, 57, 64],
    "00_08_10": [107, 140, 49, 53, 85, 56],
    "00_09_03": [24, 23],
    "00_09_04": [24, 53, 50, 49]
}

# ---- FLATTEN ORDERED LIST ----
organoid_list = []
for fov_prefix, organoids in selected_data.items():
    for org in organoids:
        organoid_list.append((fov_prefix, org))

print(f"Total selected organoids: {len(organoid_list)}")

# ---- FIRST PASS: COLLECT ALL DATA FOR GLOBAL SCALE ----
all_x, all_y = [], []
data_cache = {}

for fov_prefix, organoid_num in organoid_list:

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        organoid_name = f"organoid_{float(organoid_num)}"
        organoid_path = os.path.join(input_root, fov, organoid_name)

        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

        key = (fov_prefix, organoid_num)
        data_cache[key] = []

        for csv_file in csv_files:
            df = pd.read_csv(os.path.join(organoid_path, csv_file))

            x = df["mean_delta_d_um"]
            y = df["sigma_delta_d_um"]

            mask = np.isfinite(x) & np.isfinite(y)

            x_clean = x[mask]
            y_clean = y[mask]
            pid_clean = df["particle_id"][mask]

            data_cache[key].append((x_clean, y_clean, pid_clean))

            all_x.extend(x_clean.tolist())
            all_y.extend(y_clean.tolist())

# ---- GLOBAL SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

x_margin = 0.05 * (x_max - x_min)
y_margin = 0.05 * (y_max - y_min)

x_limits = (x_min - x_margin, x_max + x_margin)
y_limits = (y_min - y_margin, y_max + y_margin)

# ---- SPLIT INTO GROUPS OF 10 ----
group_size = 10
num_groups = math.ceil(len(organoid_list) / group_size)

# ---- PLOT ----
for g in range(num_groups):

    plt.figure(figsize=(10, 10))

    group = organoid_list[g*group_size:(g+1)*group_size]

    cmap = plt.cm.get_cmap('tab10', len(group))

    for i, (fov_prefix, organoid_num) in enumerate(group):

        key = (fov_prefix, organoid_num)
        color = cmap(i)
        first_plot = True

        for x_clean, y_clean, pid_clean in data_cache[key]:

            if first_plot:
                plt.scatter(x_clean, y_clean, color=color,
                            label=f"{fov_prefix}-org{organoid_num}")
                first_plot = False
            else:
                plt.scatter(x_clean, y_clean, color=color)

            # particle labels
            for j in range(len(x_clean)):
                plt.text(x_clean.iloc[j], y_clean.iloc[j],
                         str(pid_clean.iloc[j]), fontsize=5, color=color)

    # ---- SAME SCALE ----
    plt.xlim(x_limits)
    plt.ylim(y_limits)

    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Selected Organoids {g*10+1}–{min((g+1)*10, len(organoid_list))}")

    plt.grid(True)
    plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()

    save_path = os.path.join(output_root, f"plot_{g+1}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {save_path}")

print("All plots generated correctly (10 organoids per plot).")


# In[17]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# ---- INPUT & OUTPUT ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_split_10_final_final"
os.makedirs(output_root, exist_ok=True)

# ---- COLLECT ORGANOIDS ----
organoid_data = []

for fov in sorted(os.listdir(input_root)):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in sorted(os.listdir(fov_path)):
        organoid_path = os.path.join(fov_path, organoid)
        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        organoid_data.append({
            "fov": fov,
            "organoid": organoid,
            "x": df["mean_delta_d_um"].values,
            "y": df["sigma_delta_d_um"].values
        })

print(f"Total organoids: {len(organoid_data)}")

# ---- GLOBAL SCALE ----
all_x = np.concatenate([d["x"] for d in organoid_data])
all_y = np.concatenate([d["y"] for d in organoid_data])

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

# Add small margin so points are not at border
x_margin = 0.05 * (x_max - x_min)
y_margin = 0.05 * (y_max - y_min)

x_limits = (x_min - x_margin, x_max + x_margin)
y_limits = (y_min - y_margin, y_max + y_margin)

# ---- 10 VERY DISTINCT COLORS ----
distinct_colors = [
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "black",
    "cyan",
    "magenta",
    "brown",
    "gold"
]

# ---- SPLIT INTO GROUPS OF 10 ----
group_size = 10
num_groups = math.ceil(len(organoid_data) / group_size)

print(f"Total plots: {num_groups}")

# ---- PLOTTING ----
for g in range(num_groups):

    start = g * group_size
    end = min((g + 1) * group_size, len(organoid_data))
    group = organoid_data[start:end]

    plt.figure(figsize=(8, 8))

    for i, data in enumerate(group):
        label = f"{data['fov']} | {data['organoid']}"

        plt.scatter(
            data["x"],
            data["y"],
            s=8,
            color=distinct_colors[i],
            label=label
        )

    # ---- SAME SCALE ----
    plt.xlim(x_limits)
    plt.ylim(y_limits)

    # ---- LABELS ----
    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Organoids {start+1}–{end}")

    # ---- LEGEND ----
    plt.legend(
        fontsize=6,
        markerscale=2,
        loc='upper left',
        bbox_to_anchor=(1.02, 1)
    )

    plt.tight_layout()

    # ---- SAVE ----
    output_path = os.path.join(output_root, f"plot_{g+1}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

print("All plots generated successfully.")


# In[16]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import random
import math

# ---- INPUT & OUTPUT ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_split_10_clean"
os.makedirs(output_root, exist_ok=True)

# ---- COLLECT ORGANOIDS ----
organoid_data = []

for fov in sorted(os.listdir(input_root)):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in sorted(os.listdir(fov_path)):
        organoid_path = os.path.join(fov_path, organoid)
        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        organoid_data.append({
            "fov": fov,
            "organoid": organoid,
            "x": df["mean_delta_d_um"].values,
            "y": df["sigma_delta_d_um"].values
        })

print(f"Total organoids: {len(organoid_data)}")

# ---- GLOBAL SCALE (SAME FOR ALL PLOTS) ----
all_x = np.concatenate([d["x"] for d in organoid_data])
all_y = np.concatenate([d["y"] for d in organoid_data])

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

# ---- FIXED 0.2 INTERVAL TICKS ----
x_ticks = np.arange(0, round(x_max + 0.2, 1), 0.2)
y_ticks = np.arange(0, round(y_max + 0.2, 1), 0.2)

# ---- COLOR FUNCTION (10 DISTINCT COLORS) ----
def generate_10_colors():
    hues = np.linspace(0, 1, 10, endpoint=False)
    colors = []
    for h in hues:
        rgb = colorsys.hls_to_rgb(h, 0.5, 0.9)
        colors.append(rgb)
    random.shuffle(colors)
    return colors

# ---- SPLIT INTO GROUPS OF 10 ----
group_size = 10
num_groups = math.ceil(len(organoid_data) / group_size)

print(f"Total plots: {num_groups}")

# ---- PLOTTING ----
for g in range(num_groups):

    start = g * group_size
    end = min((g + 1) * group_size, len(organoid_data))
    group = organoid_data[start:end]

    colors = generate_10_colors()

    plt.figure(figsize=(8, 8))

    for i, data in enumerate(group):
        label = f"{data['fov']} | {data['organoid']}"

        plt.scatter(
            data["x"],
            data["y"],
            s=8,
            color=colors[i],
            label=label
        )

    # ---- SAME SCALE ----
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # ---- 0.2 INTERVAL (NO GRID) ----
    plt.xticks(x_ticks)
    plt.yticks(y_ticks)

    # ---- LABELS ----
    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Organoids {start+1}–{end}")

    # ---- LEGEND ----
    plt.legend(
        fontsize=6,
        markerscale=2,
        loc='upper left',
        bbox_to_anchor=(1.02, 1)
    )

    plt.tight_layout()

    # ---- SAVE ----
    output_path = os.path.join(output_root, f"plot_{g+1}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

print("All plots generated successfully.")


# In[15]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import random

# ---- INPUT & OUTPUT ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_legend_50/first_50_organoids_0.2_grid_labeled.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ---- COLLECT ORGANOIDS ----
organoid_data = []

for fov in sorted(os.listdir(input_root)):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in sorted(os.listdir(fov_path)):
        organoid_path = os.path.join(fov_path, organoid)
        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        organoid_data.append({
            "fov": fov,
            "organoid": organoid,
            "x": df["mean_delta_d_um"].values,
            "y": df["sigma_delta_d_um"].values
        })

# ---- TAKE FIRST 50 ----
organoid_data = organoid_data[:50]
print(f"Using {len(organoid_data)} organoids")

# ---- GENERATE DISTINCT COLORS ----
def generate_colors(n):
    hues = np.linspace(0, 1, n, endpoint=False)
    colors = []
    for h in hues:
        rgb = colorsys.hls_to_rgb(h, 0.5, 0.9)
        colors.append(rgb)
    random.shuffle(colors)
    return colors

colors = generate_colors(len(organoid_data))

# ---- GLOBAL SCALE ----
all_x = np.concatenate([d["x"] for d in organoid_data])
all_y = np.concatenate([d["y"] for d in organoid_data])

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

# ---- PLOT ----
plt.figure(figsize=(10, 10))

for i, data in enumerate(organoid_data):
    label = f"{data['fov']} | {data['organoid']}"
    
    plt.scatter(
        data["x"],
        data["y"],
        s=8,
        color=colors[i],
        label=label
    )

# ---- AXIS ----
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)

# ---- 0.2 INTERVAL GRID ----
x_ticks = np.arange(0, round(x_max + 0.2, 1), 0.2)
y_ticks = np.arange(0, round(y_max + 0.2, 1), 0.2)

plt.xticks(x_ticks)
plt.yticks(y_ticks)

plt.grid(True, linestyle='--', linewidth=0.5)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead Distribution (First 50 Organoids)")

# ---- LEGEND ----
plt.legend(
    fontsize=6,
    markerscale=2,
    loc='upper left',
    bbox_to_anchor=(1.02, 1)
)

plt.tight_layout()

# ---- SAVE ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Plot saved at: {output_path}")


# In[14]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import random

# ---- INPUT & OUTPUT ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_50_organoids/first_50_organoids_0.2_grid.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ---- COLLECT ORGANOIDS ----
organoid_data = []

for fov in sorted(os.listdir(input_root)):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in sorted(os.listdir(fov_path)):
        organoid_path = os.path.join(fov_path, organoid)
        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        organoid_data.append({
            "fov": fov,
            "organoid": organoid,
            "x": df["mean_delta_d_um"].values,
            "y": df["sigma_delta_d_um"].values
        })

# ---- TAKE FIRST 50 ----
organoid_data = organoid_data[:50]
print(f"Using {len(organoid_data)} organoids")

# ---- GENERATE DISTINCT COLORS ----
def generate_colors(n):
    hues = np.linspace(0, 1, n, endpoint=False)
    colors = []
    for h in hues:
        rgb = colorsys.hls_to_rgb(h, 0.5, 0.9)
        colors.append(rgb)
    random.shuffle(colors)
    return colors

colors = generate_colors(len(organoid_data))

# ---- GLOBAL SCALE ----
all_x = np.concatenate([d["x"] for d in organoid_data])
all_y = np.concatenate([d["y"] for d in organoid_data])

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

# ---- PLOT ----
plt.figure(figsize=(10, 10))

for i, data in enumerate(organoid_data):
    plt.scatter(
        data["x"],
        data["y"],
        s=8,
        color=colors[i]
    )

# ---- SET AXIS ----
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)

# ---- SET 0.2 INTERVAL GRID ----
x_ticks = np.arange(0, round(x_max + 0.2, 1), 0.2)
y_ticks = np.arange(0, round(y_max + 0.2, 1), 0.2)

plt.xticks(x_ticks)
plt.yticks(y_ticks)

plt.grid(True, linestyle='--', linewidth=0.5)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead Distribution (First 50 Organoids)")

plt.tight_layout()

# ---- SAVE ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Plot saved at: {output_path}")


# In[13]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import random
import math

# ---- INPUT & OUTPUT ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_split_20"
os.makedirs(output_root, exist_ok=True)

# ---- COLLECT ALL ORGANOIDS ----
organoid_data = []

for fov in os.listdir(input_root):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in os.listdir(fov_path):
        organoid_path = os.path.join(fov_path, organoid)
        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        # Clean data
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        x = df["mean_delta_d_um"].values
        y = df["sigma_delta_d_um"].values

        organoid_data.append({
            "fov": fov,
            "organoid": organoid,
            "x": x,
            "y": y
        })

print(f"Total organoids loaded: {len(organoid_data)}")

# ---- GLOBAL AXIS SCALE (IMPORTANT) ----
all_x = np.concatenate([d["x"] for d in organoid_data])
all_y = np.concatenate([d["y"] for d in organoid_data])

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

x_margin = 0.05 * (all_x.max() - all_x.min())
y_margin = 0.05 * (all_y.max() - all_y.min())

x_limits = (all_x.min() - x_margin, all_x.max() + x_margin)
y_limits = (all_y.min() - y_margin, all_y.max() + y_margin)

# ---- FUNCTION: 20 DISTINCT COLORS ----
def generate_20_colors():
    hues = np.linspace(0, 1, 20, endpoint=False)
    colors = []
    for h in hues:
        rgb = colorsys.hls_to_rgb(h, 0.5, 0.9)
        colors.append(rgb)
    random.shuffle(colors)
    return colors

# ---- SPLIT INTO GROUPS OF 20 ----
group_size = 20
num_groups = math.ceil(len(organoid_data) / group_size)

print(f"Total plots to generate: {num_groups}")

# ---- PLOTTING ----
for g in range(num_groups):

    start = g * group_size
    end = min((g + 1) * group_size, len(organoid_data))
    group = organoid_data[start:end]

    colors = generate_20_colors()

    plt.figure(figsize=(10, 10))

    for i, data in enumerate(group):
        label = f"{data['fov']} | {data['organoid']}"

        plt.scatter(
            data["x"],
            data["y"],
            s=8,
            color=colors[i],
            label=label
        )

    # ---- FIXED SAME SCALE ----
    plt.xlim(x_limits)
    plt.ylim(y_limits)

    # ---- LABELS ----
    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Bead Distribution (Organoids {start+1}–{end})")

    plt.grid(True)

    # ---- LEGEND ----
    plt.legend(fontsize=6, markerscale=2, loc='upper right', bbox_to_anchor=(1.35, 1))

    plt.tight_layout()

    # ---- SAVE ----
    output_path = os.path.join(output_root, f"plot_group_{g+1}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

print("All plots generated successfully.")


# In[12]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import random

# ---- INPUT & OUTPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_upgrade/all_organoids_distinct_improved.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ---- COLLECT ALL ORGANOIDS ----
organoid_paths = []

for fov in os.listdir(input_root):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in os.listdir(fov_path):
        organoid_path = os.path.join(fov_path, organoid)
        if os.path.isdir(organoid_path):
            organoid_paths.append((fov, organoid, organoid_path))

print(f"Total organoids found: {len(organoid_paths)}")

# ---- GENERATE HIGH-CONTRAST DISTINCT COLORS ----
def generate_high_contrast_colors(n):
    hues = np.linspace(0, 1, n, endpoint=False)
    
    colors = []
    for h in hues:
        # Alternate lightness for better separation
        lightness = 0.45 + 0.1 * (random.random())
        saturation = 0.85 + 0.15 * (random.random())
        
        rgb = colorsys.hls_to_rgb(h, lightness, saturation)
        colors.append(rgb)

    # Shuffle colors so similar hues are not adjacent
    random.shuffle(colors)
    
    return colors

colors = generate_high_contrast_colors(len(organoid_paths))

# ---- PLOT ----
plt.figure(figsize=(10, 10))

all_x = []
all_y = []

# ---- LOOP ----
for idx, (fov, organoid, organoid_path) in enumerate(organoid_paths):

    csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
    if not csv_files:
        continue

    csv_path = os.path.join(organoid_path, csv_files[0])
    df = pd.read_csv(csv_path)

    # ---- CLEAN DATA ----
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    if df.empty:
        continue

    x = df["mean_delta_d_um"]
    y = df["sigma_delta_d_um"]

    all_x.extend(x)
    all_y.extend(y)

    # ---- PLOT SMALL DOTS ----
    plt.scatter(x, y, s=8, color=colors[idx])

# ---- SAFE AXIS SCALING ----
all_x = np.array(all_x)
all_y = np.array(all_y)

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

if len(all_x) > 0 and len(all_y) > 0:
    x_margin = 0.05 * (all_x.max() - all_x.min())
    y_margin = 0.05 * (all_y.max() - all_y.min())

    plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
    plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Mean vs Std Dev of Beads (All Organoids)")
plt.grid(True)

plt.tight_layout()

# ---- SAVE ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

print(f"Plot saved at: {output_path}")


# In[11]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colorsys

# ---- INPUT & OUTPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_distict_allorganoid/all_organoids_distinct.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ---- COLLECT ALL ORGANOIDS ----
organoid_paths = []

for fov in os.listdir(input_root):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in os.listdir(fov_path):
        organoid_path = os.path.join(fov_path, organoid)
        if os.path.isdir(organoid_path):
            organoid_paths.append((fov, organoid, organoid_path))

print(f"Total organoids found: {len(organoid_paths)}")

# ---- GENERATE DISTINCT COLORS ----
def generate_distinct_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.5
        saturation = 0.9
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(rgb)
    return colors

colors = generate_distinct_colors(len(organoid_paths))

# ---- PLOT ----
plt.figure(figsize=(10, 10))

all_x = []
all_y = []

# ---- LOOP ----
for idx, (fov, organoid, organoid_path) in enumerate(organoid_paths):

    csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
    if not csv_files:
        continue

    csv_path = os.path.join(organoid_path, csv_files[0])
    df = pd.read_csv(csv_path)

    # ---- CLEAN DATA ----
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    if df.empty:
        continue

    x = df["mean_delta_d_um"]
    y = df["sigma_delta_d_um"]

    all_x.extend(x)
    all_y.extend(y)

    # ---- PLOT SMALL DOTS ----
    plt.scatter(x, y, s=8, color=colors[idx])

# ---- SAFE AXIS SCALING ----
all_x = np.array(all_x)
all_y = np.array(all_y)

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

if len(all_x) > 0 and len(all_y) > 0:
    x_margin = 0.05 * (all_x.max() - all_x.min())
    y_margin = 0.05 * (all_y.max() - all_y.min())

    plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
    plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Mean vs Std Dev of Beads (All Organoids)")
plt.grid(True)

plt.tight_layout()

# ---- SAVE ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

print(f"Plot saved at: {output_path}")


# In[10]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# ---- INPUT & OUTPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_folder = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_split"
os.makedirs(output_folder, exist_ok=True)

# ---- COLLECT ALL ORGANOID PATHS ----
organoid_paths = []

for fov in os.listdir(input_root):
    fov_path = os.path.join(input_root, fov)
    if not os.path.isdir(fov_path):
        continue

    for organoid in os.listdir(fov_path):
        organoid_path = os.path.join(fov_path, organoid)
        if os.path.isdir(organoid_path):
            organoid_paths.append((fov, organoid, organoid_path))

print(f"Total organoids found: {len(organoid_paths)}")

# ---- SPLIT INTO CHUNKS OF 10 ----
chunk_size = 10
num_chunks = math.ceil(len(organoid_paths) / chunk_size)

for chunk_idx in range(num_chunks):
    chunk = organoid_paths[chunk_idx*chunk_size : (chunk_idx+1)*chunk_size]

    plt.figure(figsize=(10, 10))

    all_x = []
    all_y = []

    # ---- COLOR MAP FOR 10 ----
    colors = plt.cm.get_cmap('tab10', len(chunk))

    for i, (fov, organoid, organoid_path) in enumerate(chunk):

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        # ---- CLEAN DATA ----
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        x = df["mean_delta_d_um"]
        y = df["sigma_delta_d_um"]

        all_x.extend(x)
        all_y.extend(y)

        color = colors(i)

        # ---- SMALL DOTS ----
        plt.scatter(x, y, s=8, color=color, label=f"{fov}_{organoid}")

    # ---- SAFE AXIS ----
    all_x = np.array(all_x)
    all_y = np.array(all_y)

    all_x = all_x[np.isfinite(all_x)]
    all_y = all_y[np.isfinite(all_y)]

    if len(all_x) > 0 and len(all_y) > 0:
        x_margin = 0.05 * (all_x.max() - all_x.min())
        y_margin = 0.05 * (all_y.max() - all_y.min())

        plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
        plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

    # ---- LABELS ----
    plt.xlabel("Mean Δd (µm)")
    plt.ylabel("Std Dev Δd (µm)")
    plt.title(f"Mean vs Std Dev (Organoids {chunk_idx*10+1}–{chunk_idx*10+len(chunk)})")
    plt.grid(True)

    plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()

    # ---- SAVE ----
    output_path = os.path.join(output_folder, f"plot_group_{chunk_idx+1}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.close()

    print(f"Saved: {output_path}")

print("All plots generated successfully.")


# In[9]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"

# ---- OUTPUT PATH ----
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_show_sir/all_organoids_clean_plot.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

plt.figure(figsize=(10, 10))

all_x = []
all_y = []

# ---- GET ALL FOV FOLDERS ----
fov_folders = [f for f in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, f))]

color_idx = 0
total_organoids = 0

# ---- COUNT TOTAL ORGANOIDS FIRST (for color scaling) ----
for fov in fov_folders:
    fov_path = os.path.join(input_root, fov)
    organoids = [o for o in os.listdir(fov_path) if os.path.isdir(os.path.join(fov_path, o))]
    total_organoids += len(organoids)

# ---- COLOR MAP (large range) ----
colors = plt.cm.get_cmap('hsv', total_organoids + 1)

# ---- MAIN LOOP ----
for fov in fov_folders:
    fov_path = os.path.join(input_root, fov)

    for organoid_folder in os.listdir(fov_path):
        organoid_path = os.path.join(fov_path, organoid_folder)

        if not os.path.isdir(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        # ---- CLEAN DATA ----
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        x = df["mean_delta_d_um"]
        y = df["sigma_delta_d_um"]

        all_x.extend(x)
        all_y.extend(y)

        color = colors(color_idx)
        color_idx += 1

        # ---- SMALL DOTS ONLY ----
        plt.scatter(x, y, s=8, color=color)

# ---- SAFE AXIS SCALING ----
all_x = np.array(all_x)
all_y = np.array(all_y)

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

if len(all_x) > 0 and len(all_y) > 0:
    x_margin = 0.05 * (all_x.max() - all_x.min())
    y_margin = 0.05 * (all_y.max() - all_y.min())

    plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
    plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Mean vs Std Dev of Beads (All Organoids)")
plt.grid(True)

plt.tight_layout()

# ---- SAVE ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

print(f"Plot saved at: {output_path}")


# In[8]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"

# ---- OUTPUT PATH ----
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_10/combined_selected_organoids.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ---- SELECT ONLY 10 ORGANOIDS ----
selected_data = {
    "00_01_05": [9],
    "00_01_06": [25],
    "00_02_04": [22],
    "00_02_05": [30],
    "00_02_06": [99],
    "00_02_07": [2],
    "00_02_08": [39],
    "00_03_03": [7],
    "00_03_04": [4],
    "00_03_05": [6]
}

# ---- COLOR MAP ----
colors = plt.cm.get_cmap('tab10', 10)

plt.figure(figsize=(10, 10))

all_x = []
all_y = []
color_idx = 0

# ---- LOOP ----
for fov, organoids in selected_data.items():
    fov_folder = f"{fov}_surface_distance_200frames"
    fov_path = os.path.join(input_root, fov_folder)

    for organoid in organoids:
        organoid_folder = f"organoid_{organoid}.0"
        organoid_path = os.path.join(fov_path, organoid_folder)

        if not os.path.exists(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        x = df["mean_delta_d_um"]
        y = df["sigma_delta_d_um"]
        particle_ids = df["particle_id"]

        all_x.extend(x)
        all_y.extend(y)

        color = colors(color_idx)
        color_idx += 1

        # ---- SMALL DOTS ----
        plt.scatter(x, y, s=10, color=color, label=f"{fov}_org{organoid}")

        # ---- LABEL PARTICLES ----
        for i in range(len(df)):
            plt.text(x.iloc[i], y.iloc[i], str(particle_ids.iloc[i]),
                     fontsize=6, color=color)

# ---- SAFE AXIS ----
all_x = np.array(all_x)
all_y = np.array(all_y)

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

if len(all_x) > 0 and len(all_y) > 0:
    x_margin = 0.05 * (all_x.max() - all_x.min())
    y_margin = 0.05 * (all_y.max() - all_y.min())

    plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
    plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Mean vs Std Dev of Beads (10 Organoids)")
plt.grid(True)

plt.legend(fontsize=7, loc='upper right')

plt.tight_layout()

# ---- SAVE ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

print(f"Plot saved at: {output_path}")


# In[7]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"

# ---- OUTPUT PATH (ADDED BACK) ----
output_path = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_half/combined_selected_organoids.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ---- SELECTED FOV + ORGANOIDS (REDUCED SET) ----
selected_data = {
    "00_01_05": [9],
    "00_01_06": [25],
    "00_02_04": [22],
    "00_02_05": [30],
    "00_02_06": [99, 75],
    "00_02_07": [2, 52],
    "00_02_08": [39, 78],
    "00_03_03": [7],
    "00_03_04": [4, 85],
    "00_03_05": [6, 73],
    "00_04_02": [28, 25],
    "00_04_03": [1, 13],
    "00_04_04": [21, 24],
    "00_04_05": [21],
    "00_04_06": [103],
    "00_04_07": [40, 38],
    "00_05_02": [40, 26],
    "00_05_03": [9, 10],
    "00_05_04": [2],
    "00_05_05": [79, 40],
    "00_06_02": [30],
    "00_06_03": [25],
    "00_06_04": [25, 12],
    "00_06_05": [40],
    "00_06_06": [56, 97],
    "00_07_03": [32],
    "00_07_04": [13],
    "00_07_05": [11, 29],
    "00_08_02": [6],
    "00_08_03": [27],
    "00_08_04": [1],
    "00_09_03": [24],
    "00_09_04": [24]
}

# ---- COLOR MAP ----
colors = plt.cm.get_cmap('tab20', 100)

plt.figure(figsize=(10, 10))

all_x = []
all_y = []
color_idx = 0

# ---- LOOP ----
for fov, organoids in selected_data.items():
    fov_folder = f"{fov}_surface_distance_200frames"
    fov_path = os.path.join(input_root, fov_folder)

    for organoid in organoids:
        organoid_folder = f"organoid_{organoid}.0"
        organoid_path = os.path.join(fov_path, organoid_folder)

        if not os.path.exists(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])
        df = pd.read_csv(csv_path)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            continue

        x = df["mean_delta_d_um"]
        y = df["sigma_delta_d_um"]
        particle_ids = df["particle_id"]

        all_x.extend(x)
        all_y.extend(y)

        color = colors(color_idx)
        color_idx += 1

        plt.scatter(x, y, s=10, color=color, label=f"{fov}_org{organoid}")

        for i in range(len(df)):
            plt.text(x.iloc[i], y.iloc[i], str(particle_ids.iloc[i]),
                     fontsize=6, color=color)

# ---- SAFE AXIS ----
all_x = np.array(all_x)
all_y = np.array(all_y)

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

if len(all_x) > 0 and len(all_y) > 0:
    x_margin = 0.05 * (all_x.max() - all_x.min())
    y_margin = 0.05 * (all_y.max() - all_y.min())

    plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
    plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Mean vs Std Dev of Beads (Selected Organoids)")
plt.grid(True)

plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()

# ---- SAVE (ADDED BACK) ----
plt.savefig(output_path, dpi=300, bbox_inches="tight")

plt.show()

print(f"Plot saved at: {output_path}")


# In[ ]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT PATH ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"

# ---- SELECTED FOV + ORGANOIDS (REDUCED SET) ----
selected_data = {
    "00_01_05": [9],
    "00_01_06": [25],
    "00_02_04": [22],
    "00_02_05": [30],
    "00_02_06": [99, 75],
    "00_02_07": [2, 52],
    "00_02_08": [39, 78],
    "00_03_03": [7],
    "00_03_04": [4, 85],
    "00_03_05": [6, 73],
    "00_04_02": [28, 25],
    "00_04_03": [1, 13],
    "00_04_04": [21, 24],
    "00_04_05": [21],
    "00_04_06": [103],
    "00_04_07": [40, 38],
    "00_05_02": [40, 26],
    "00_05_03": [9, 10],
    "00_05_04": [2],
    "00_05_05": [79, 40],
    "00_06_02": [30],
    "00_06_03": [25],
    "00_06_04": [25, 12],
    "00_06_05": [40],
    "00_06_06": [56, 97],
    "00_07_03": [32],
    "00_07_04": [13],
    "00_07_05": [11, 29],
    "00_08_02": [6],
    "00_08_03": [27],
    "00_08_04": [1],
    "00_09_03": [24],
    "00_09_04": [24]
}

# ---- COLOR MAP (many distinct colors) ----
colors = plt.cm.get_cmap('tab20', 100)

plt.figure(figsize=(10, 10))

all_x = []
all_y = []

color_idx = 0

# ---- LOOP THROUGH SELECTED DATA ----
for fov, organoids in selected_data.items():
    fov_folder = f"{fov}_surface_distance_200frames"
    fov_path = os.path.join(input_root, fov_folder)

    for organoid in organoids:
        organoid_folder = f"organoid_{organoid}.0"
        organoid_path = os.path.join(fov_path, organoid_folder)

        if not os.path.exists(organoid_path):
            continue

        csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]
        if not csv_files:
            continue

        csv_path = os.path.join(organoid_path, csv_files[0])

        df = pd.read_csv(csv_path)

        # ---- CLEAN DATA ----
        df = df.replace([np.inf, -np.inf], np.nan).dropna()

        if df.empty:
            continue

        x = df["mean_delta_d_um"]
        y = df["sigma_delta_d_um"]
        particle_ids = df["particle_id"]

        all_x.extend(x)
        all_y.extend(y)

        color = colors(color_idx)
        color_idx += 1

        # ---- PLOT SMALL DOTS ----
        plt.scatter(x, y, s=10, color=color, label=f"{fov}_org{organoid}")

        # ---- LABEL PARTICLE IDs ----
        for i in range(len(df)):
            plt.text(x.iloc[i], y.iloc[i], str(particle_ids.iloc[i]),
                     fontsize=6, color=color)

# ---- SAFE AXIS SCALING ----
all_x = np.array(all_x)
all_y = np.array(all_y)

all_x = all_x[np.isfinite(all_x)]
all_y = all_y[np.isfinite(all_y)]

if len(all_x) > 0 and len(all_y) > 0:
    x_margin = 0.05 * (all_x.max() - all_x.min())
    y_margin = 0.05 * (all_y.max() - all_y.min())

    plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
    plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Mean vs Std Dev of Beads (Selected Organoids)")
plt.grid(True)

# ---- LEGEND (optional: comment if too crowded) ----
plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()


# In[6]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_unique_colour"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION ----
selected_data = {
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

# ---- PREPARE PLOT ----
plt.figure(figsize=(10, 10))

# ---- UNIQUE COLORS ----
total_organoids = sum(len(v) for v in selected_data.values())
cmap = plt.cm.get_cmap('nipy_spectral', total_organoids)
color_index = 0

# ---- STORE DATA FOR AUTO SCALING ----
all_x = []
all_y = []

# ---- LOOP ----
for fov_prefix, organoid_numbers in selected_data.items():

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:

            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            color = cmap(color_index)
            first_plot = True

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)
                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]
                particle_ids = df["particle_id"]

                # ---- CLEAN DATA ----
                valid_mask = np.isfinite(x) & np.isfinite(y)
                x_clean = x[valid_mask]
                y_clean = y[valid_mask]
                pid_clean = particle_ids[valid_mask]

                # ---- STORE FOR SCALING ----
                all_x.extend(x_clean.tolist())
                all_y.extend(y_clean.tolist())

                # ---- SCATTER ----
                if first_plot:
                    plt.scatter(x_clean, y_clean, color=color,
                                label=f"{fov_prefix}-org{organoid_num}")
                    first_plot = False
                else:
                    plt.scatter(x_clean, y_clean, color=color)

                # ---- LABEL PARTICLES ----
                for i in range(len(x_clean)):
                    plt.text(
                        x_clean.iloc[i],
                        y_clean.iloc[i],
                        str(pid_clean.iloc[i]),
                        fontsize=5,
                        color=color
                    )

            color_index += 1

# ---- AUTO SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

mask = np.isfinite(all_x) & np.isfinite(all_y)
all_x = all_x[mask]
all_y = all_y[mask]

if len(all_x) == 0:
    raise ValueError("No valid data found!")

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

x_margin = 0.05 * (x_max - x_min) if x_max != x_min else 0.1
y_margin = 0.05 * (y_max - y_min) if y_max != y_min else 0.1

plt.xlim(x_min - x_margin, x_max + x_margin)
plt.ylim(y_min - y_margin, y_max + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead-level Mean vs Std Dev (Unique Colors + Auto Scale)")

plt.grid(True)
plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

# ---- SAVE ----
save_path = os.path.join(output_root, "bead_plot_unique_colors.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")

plt.close()

print("Final plot with unique colors generated successfully.")


# In[5]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_final"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION ----
selected_data = {
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

# ---- PREPARE PLOT ----
plt.figure(figsize=(10, 10))
colors = plt.cm.tab20.colors
color_index = 0

# ---- STORE DATA FOR AUTO SCALING ----
all_x = []
all_y = []

# ---- LOOP ----
for fov_prefix, organoid_numbers in selected_data.items():

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:

            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            color = colors[color_index % len(colors)]
            first_plot = True

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)
                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]
                particle_ids = df["particle_id"]

                # ---- CLEAN DATA (REMOVE NaN / INF) ----
                valid_mask = np.isfinite(x) & np.isfinite(y)
                x_clean = x[valid_mask]
                y_clean = y[valid_mask]
                pid_clean = particle_ids[valid_mask]

                # ---- STORE FOR GLOBAL SCALE ----
                all_x.extend(x_clean.tolist())
                all_y.extend(y_clean.tolist())

                # ---- SCATTER ----
                if first_plot:
                    plt.scatter(x_clean, y_clean, color=color,
                                label=f"{fov_prefix}-org{organoid_num}")
                    first_plot = False
                else:
                    plt.scatter(x_clean, y_clean, color=color)

                # ---- PARTICLE ID LABELS ----
                for i in range(len(x_clean)):
                    plt.text(
                        x_clean.iloc[i],
                        y_clean.iloc[i],
                        str(pid_clean.iloc[i]),
                        fontsize=5,
                        color=color
                    )

            color_index += 1

# ---- FINAL CLEAN + AUTO SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

mask = np.isfinite(all_x) & np.isfinite(all_y)
all_x = all_x[mask]
all_y = all_y[mask]

if len(all_x) == 0 or len(all_y) == 0:
    raise ValueError("No valid data available!")

x_min, x_max = all_x.min(), all_x.max()
y_min, y_max = all_y.min(), all_y.max()

x_margin = 0.05 * (x_max - x_min) if x_max != x_min else 0.1
y_margin = 0.05 * (y_max - y_min) if y_max != y_min else 0.1

plt.xlim(x_min - x_margin, x_max + x_margin)
plt.ylim(y_min - y_margin, y_max + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead-level Mean vs Std Dev (Auto-scaled, Cleaned)")

plt.grid(True)

plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

# ---- SAVE ----
save_path = os.path.join(output_root, "bead_plot_auto_scaled.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")

plt.close()

print("Final plot generated successfully.")


# In[4]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_big_sacle"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION ----
selected_data = {
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

# ---- PREPARE PLOT ----
plt.figure(figsize=(10, 10))
colors = plt.cm.tab20.colors
color_index = 0

# ---- STORE ALL DATA FOR AUTO SCALING ----
all_x = []
all_y = []

# ---- LOOP ----
for fov_prefix, organoid_numbers in selected_data.items():

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:

            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            color = colors[color_index % len(colors)]
            first_plot = True

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)
                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]
                particle_ids = df["particle_id"]

                # ---- STORE FOR GLOBAL SCALING ----
                all_x.extend(x.tolist())
                all_y.extend(y.tolist())

                # ---- SCATTER ----
                if first_plot:
                    plt.scatter(x, y, color=color,
                                label=f"{fov_prefix}-org{organoid_num}")
                    first_plot = False
                else:
                    plt.scatter(x, y, color=color)

                # ---- PARTICLE ID LABELS ----
                for i in range(len(df)):
                    plt.text(
                        x.iloc[i],
                        y.iloc[i],
                        str(particle_ids.iloc[i]),
                        fontsize=5,
                        color=color
                    )

            color_index += 1

# ---- AUTO SCALE ----
all_x = np.array(all_x)
all_y = np.array(all_y)

x_margin = 0.05 * (all_x.max() - all_x.min())
y_margin = 0.05 * (all_y.max() - all_y.min())

plt.xlim(all_x.min() - x_margin, all_x.max() + x_margin)
plt.ylim(all_y.min() - y_margin, all_y.max() + y_margin)

# ---- LABELS ----
plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead-level Mean vs Std Dev (All Data Auto-Scaled)")

plt.grid(True)

plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

# ---- SAVE ----
save_path = os.path.join(output_root, "bead_plot_auto_scaled.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")

plt.close()

print("Auto-scaled plot with particle IDs generated successfully.")


# In[3]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plots_labled"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION ----
selected_data = {
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

# ---- PREPARE PLOT ----
plt.figure(figsize=(10, 10))
colors = plt.cm.tab20.colors
color_index = 0

# ---- LOOP ----
for fov_prefix, organoid_numbers in selected_data.items():

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:

            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            color = colors[color_index % len(colors)]
            first_plot = True

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)
                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]
                particle_ids = df["particle_id"]

                # ---- SCATTER ----
                if first_plot:
                    plt.scatter(x, y, color=color,
                                label=f"{fov_prefix}-org{organoid_num}")
                    first_plot = False
                else:
                    plt.scatter(x, y, color=color)

                # ---- ADD PARTICLE ID LABELS ----
                for i in range(len(df)):
                    plt.text(
                        x.iloc[i],
                        y.iloc[i],
                        str(particle_ids.iloc[i]),
                        fontsize=5,
                        color=color
                    )

            color_index += 1

# ---- FIXED AXIS ----
plt.xlim(0, 1.5)
plt.ylim(0, 1.5)

plt.xticks(np.arange(0, 1.6, 0.5))
plt.yticks(np.arange(0, 1.6, 0.5))

plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead-level Mean vs Std Dev (with Particle IDs)")

plt.grid(True)

plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

# ---- SAVE ----
save_path = os.path.join(output_root, "bead_plot_with_particle_ids.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")

plt.close()

print("Plot with particle IDs generated successfully.")


# In[2]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_beads_plot_new"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION (FOV → organoid numbers) ----
selected_data = {
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

# ---- PREPARE PLOT ----
plt.figure(figsize=(10, 10))
colors = plt.cm.tab20.colors
color_index = 0

# ---- LOOP ----
for fov_prefix, organoid_numbers in selected_data.items():

    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        for organoid_num in organoid_numbers:

            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            # ---- FIX COLOR PER ORGANOID ----
            color = colors[color_index % len(colors)]
            first_plot = True  # for legend

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)

                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]

                # ---- PLOT ALL BEADS ----
                if first_plot:
                    plt.scatter(x, y, color=color,
                                label=f"{fov_prefix}-org{organoid_num}")
                    first_plot = False
                else:
                    plt.scatter(x, y, color=color)

            color_index += 1

# ---- FIXED AXIS ----
plt.xlim(0, 1.5)
plt.ylim(0, 1.5)

plt.xticks(np.arange(0, 1.6, 0.5))
plt.yticks(np.arange(0, 1.6, 0.5))

plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Bead-level Mean vs Std Dev (Selected Organoids)")

plt.grid(True)

plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

# ---- SAVE ----
save_path = os.path.join(output_root, "final_bead_level_plot.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")

plt.close()

print("Final bead-level plot generated successfully.")


# In[1]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT & OUTPUT PATHS ----
input_root = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads"
output_root = "/NAS2/Nikita/X_mean_Y_SD_all_organoid_delta_d"
os.makedirs(output_root, exist_ok=True)

# ---- YOUR SELECTION (FOV → organoid numbers) ----
selected_data = {
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

# ---- PREPARE PLOT ----
plt.figure(figsize=(10, 10))
colors = plt.cm.tab20.colors
color_index = 0

# ---- LOOP ----
for fov_prefix, organoid_numbers in selected_data.items():

    # match full folder name
    for fov in os.listdir(input_root):
        if not fov.startswith(fov_prefix):
            continue

        fov_path = os.path.join(input_root, fov)

        if not os.path.isdir(fov_path):
            continue

        for organoid_num in organoid_numbers:
            organoid_name = f"organoid_{float(organoid_num)}"
            organoid_path = os.path.join(fov_path, organoid_name)

            if not os.path.isdir(organoid_path):
                continue

            csv_files = [f for f in os.listdir(organoid_path) if f.endswith(".csv")]

            for csv_file in csv_files:
                csv_path = os.path.join(organoid_path, csv_file)

                df = pd.read_csv(csv_path)

                x = df["mean_delta_d_um"]
                y = df["sigma_delta_d_um"]

                color = colors[color_index % len(colors)]

                plt.scatter(x, y, color=color,
                            label=f"{fov_prefix}-org{organoid_num}")

                color_index += 1

# ---- FIXED AXIS ----
plt.xlim(0, 1.5)
plt.ylim(0, 1.5)

plt.xticks(np.arange(0, 1.6, 0.5))
plt.yticks(np.arange(0, 1.6, 0.5))

plt.xlabel("Mean Δd (µm)")
plt.ylabel("Std Dev Δd (µm)")
plt.title("Selected Organoids Combined Plot")

plt.grid(True)

# ---- LEGEND ----
plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

# ---- SAVE ----
save_path = os.path.join(output_root, "final_selected_organoids_plot.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")

plt.close()

print("Final combined plot generated successfully.")


# In[ ]:




