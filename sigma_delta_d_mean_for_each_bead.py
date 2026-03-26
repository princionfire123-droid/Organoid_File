#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('jupyter nbconvert --to script sigma_delta_d_mean_for_each_bead.ipynb')


# In[1]:


import os
import pandas as pd
import numpy as np
from pathlib import Path

# ---- INPUT & OUTPUT ROOT ----
input_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/delta_d_for_all_organoid_beads")   # <-- change this
output_root = Path("/NAS2/Nikita/delta_d_analysis_23_march/SD_mean_delta_d_all_beads")  # <-- change this

# ---- LOOP THROUGH ALL FILES ----
for fov_path in input_root.iterdir():
    if not fov_path.is_dir():
        continue

    for organoid_path in fov_path.iterdir():
        if not organoid_path.is_dir():
            continue

        for csv_file in organoid_path.glob("*.csv"):

            try:
                df = pd.read_csv(csv_file)

                # ---- CHECK COLUMN ----
                if "delta_d" not in df.columns:
                    print(f"Skipping (no delta_d): {csv_file}")
                    continue

                # ---- CLEAN DATA ----
                delta_d = df["delta_d"]
                valid = np.isfinite(delta_d)
                delta_clean = delta_d[valid]

                if len(delta_clean) == 0:
                    print(f"Skipping (empty): {csv_file}")
                    continue

                # ---- CALCULATE ----
                mean_val = np.mean(delta_clean)
                sigma_val = np.std(delta_clean)

                # ---- OUTPUT DATAFRAME ----
                out_df = pd.DataFrame({
                    "mean_delta_d": [mean_val],
                    "sigma_delta_d": [sigma_val]
                })

                # ---- CREATE SAME STRUCTURE ----
                relative_path = csv_file.relative_to(input_root)
                output_path = output_root / relative_path
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # ---- SAVE ----
                out_df.to_csv(output_path, index=False)

                print(f"Saved: {output_path}")

            except Exception as e:
                print(f"Error processing {csv_file}: {e}")

print("All files processed successfully.")


# In[ ]:




