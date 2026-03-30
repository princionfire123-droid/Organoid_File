#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script surface_distance_calculation.ipynb')


# In[1]:


from pathlib import Path
import pandas as pd

# ==============================
# INPUT FILE PATHS
# ==============================
radius_file = Path(
    "/NAS2/Nikita/3sep2025_beads_exp_10min/radius_organoid_mean/00_02_07.tif_mean_radius_calculated.csv"
)

distance_file = Path(
    "/NAS2/Nikita/3sep2025_beads_exp_10min/assigned_beads_50um_22/00_02_07_assigned.csv"
)

# ==============================
# OUTPUT FILE PATH
# ==============================
output_file = Path(
    "/NAS2/Nikita/3sep2025_beads_exp_10min/surface_distance/00_02_07_surface_distance_calculated.csv"
)

# CREATE OUTPUT DIRECTORY
output_file.parent.mkdir(parents=True, exist_ok=True)

# ==============================
# LOAD DATA (CSV NOW)
# ==============================
radius_df = pd.read_csv(radius_file)
distance_df = pd.read_csv(distance_file)

# ==============================
# RENAME FRAME COLUMN TO MATCH
# ==============================
distance_df = distance_df.rename(columns={"frame_in_file": "frame"})

# ==============================
# MERGE DATAFRAMES
# ==============================
merged_df = pd.merge(
    distance_df,
    radius_df[["organoid_id", "frame", "scaled_radius_px"]],
    on=["organoid_id", "frame"],
    how="inner"
)

# ==============================
# CALCULATE SURFACE DISTANCE (px)
# ==============================
merged_df["surface_distance_px"] = (
    merged_df["distance_to_organoid"] - merged_df["scaled_radius_px"]
)

# ==============================
# CONVERT TO MICROMETERS
# ==============================
PX_TO_UM = 0.65
merged_df["surface_distance_um"] = merged_df["surface_distance_px"] * PX_TO_UM

# ==============================
# SAVE OUTPUT
# ==============================
merged_df.to_csv(output_file, index=False)

print("Surface distance calculation complete.")
print(f"Output saved to: {output_file}")


# In[ ]:




