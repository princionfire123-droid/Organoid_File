#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script all_organoid_radius_calculation.ipynb')


# In[1]:


from pathlib import Path
import pandas as pd
import numpy as np

# ===============================
# INPUT ROOT FOLDER (contains chunk_0, chunk_1, chunk_2, ...)
# ===============================

input_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/model_output")

# ===============================
# OUTPUT ROOT FOLDER
# ===============================

output_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/radius_organoid_mean_all_chunks")
output_root.mkdir(parents=True, exist_ok=True)

# ===============================
# CONSTANTS
# ===============================

PIXEL_SCALING_FACTOR = 3.90625
UM_PER_PIXEL = 0.32

# ===============================
# LOOP THROUGH ALL CHUNKS + XLSX FILES
# ===============================

for chunk_folder in input_root.glob("chunk_*"):
    for input_file in chunk_folder.glob("*.xlsx"):

        print(f"Processing: {input_file}")

        # Load data
        major_df = pd.read_excel(input_file, sheet_name="axis_major_length", header=None)
        minor_df = pd.read_excel(input_file, sheet_name="axis_minor_length", header=None)

        # Extract numeric data
        major_values = major_df.iloc[2:, 1:].astype(float)
        minor_values = minor_df.iloc[2:, 1:].astype(float)

        frames = major_df.iloc[0, 1:].astype(int).values
        organoid_ids = np.arange(1, major_values.shape[0] + 1)

        # Convert axis length to radius
        major_radius = major_values / 2
        minor_radius = minor_values / 2

        # Scale to raw pixels
        major_radius_scaled = major_radius * PIXEL_SCALING_FACTOR
        minor_radius_scaled = minor_radius * PIXEL_SCALING_FACTOR

        # Mean radius
        scaled_radius_px = (major_radius_scaled + minor_radius_scaled) / 2
        radius_um = scaled_radius_px * UM_PER_PIXEL

        # Format output
        output_records = []

        for org_idx, organoid_id in enumerate(organoid_ids):
            for frame_idx, frame in enumerate(frames):
                output_records.append({
                    "organoid_id": organoid_id,
                    "frame": frame,
                    "scaled_radius_px": scaled_radius_px.iloc[org_idx, frame_idx],
                    "radius_um": radius_um.iloc[org_idx, frame_idx]
                })

        output_df = pd.DataFrame(output_records)

        # Save with same name as Excel file
        output_filename = input_file.stem + "_mean_radius.csv"
        output_file = output_root / output_filename

        output_df.to_csv(output_file, index=False)

        print(f"Saved: {output_file}")

print("All files processed successfully.")


# In[ ]:




