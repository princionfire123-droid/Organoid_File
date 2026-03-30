#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script sigma_by_mean_calculation.ipynb')


# In[1]:


import pandas as pd
from pathlib import Path

# -------- INPUT ROOT --------
input_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/histogram_mean_sigma_all_beads")  # change this

# -------- OUTPUT ROOT --------
output_root = Path("/NAS2/Nikita/sigma_by_mean")  # change this

# -------- PROCESS FILES --------
for csv_file in input_root.rglob("*.csv"):
    try:
        # Read CSV
        df = pd.read_csv(csv_file)

        # Check required columns exist
        required_cols = ["particle_id", "mean_delta_d_um", "sigma_delta_d_um"]
        if not all(col in df.columns for col in required_cols):
            print(f"Skipping {csv_file} (missing columns)")
            continue

        # Avoid division by zero
        df["sigma_over_mean"] = df["sigma_delta_d_um"] / df["mean_delta_d_um"]
        df.loc[df["mean_delta_d_um"] == 0, "sigma_over_mean"] = None

        # -------- CREATE OUTPUT PATH (same hierarchy) --------
        relative_path = csv_file.relative_to(input_root)
        output_file = output_root / relative_path

        # Make sure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save new CSV
        df.to_csv(output_file, index=False)

        print(f"Processed: {csv_file}")

    except Exception as e:
        print(f"Error processing {csv_file}: {e}")


# In[ ]:




