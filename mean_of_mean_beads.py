#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script mean_of_mean_beads.ipynb')


# In[1]:


import pandas as pd
from pathlib import Path

# -------- PATHS --------
input_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads")
output_file = Path("/NAS2/Nikita/histogram_mean_nikk/mean_delta_d_summary.csv")

output_file.parent.mkdir(parents=True, exist_ok=True)

# -------- HELPERS --------
def extract_fov(folder_name):
    # assumes FOV folder name like "00_02_07_surface_distance_..."
    return "_".join(folder_name.split("_")[:3])

def extract_organoid(folder_name):
    try:
        # assumes "organoid_2.0", "organoid_5" etc.
        return int(float(folder_name.lower().replace("organoid_", "")))
    except:
        return None

# -------- COLLECT --------
results = []

for csv_file in input_root.rglob("*.csv"):
    try:
        # FOV folder is two levels above CSV
        fov_folder = csv_file.parents[1].name
        organoid_folder = csv_file.parent.name

        fov = extract_fov(fov_folder)
        organoid = extract_organoid(organoid_folder)

        df = pd.read_csv(csv_file)

        if "mean_delta_d_um" not in df.columns:
            print(f"Skipping (missing column): {csv_file}")
            continue

        mean_value = df["mean_delta_d_um"].mean()

        results.append({
            "FOV": fov,
            "Organoid": organoid,
            "Mean_mean_delta_d_um": mean_value
        })

        print(f"Processed: {fov} | Organoid {organoid}")

    except Exception as e:
        print(f"Error: {csv_file} -> {e}")

# -------- SAVE OUTPUT --------
if len(results) == 0:
    print("No data found.")
else:
    output_df = pd.DataFrame(results)

    # optional: sort
    output_df = output_df.sort_values(by=["FOV", "Organoid"])

    output_df.to_csv(output_file, index=False)

    print(f"\n✅ Output saved at: {output_file}")

