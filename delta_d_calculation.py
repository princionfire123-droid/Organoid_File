#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script delta_d_calculation.ipynb')


# In[1]:


from pathlib import Path
import pandas as pd

#
# USER INPUT
#

input_folder = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/200_beads_trajectory_surface_distance")
output_root = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/delta_d_for_all_organoid_beads")
output_root.mkdir(parents=True, exist_ok=True)

# Find all surface distance CSV files
csv_files = list(input_folder.glob("*_surface_distance_200frames.csv"))

print(f"Total CSV files found: {len(csv_files)}")

for input_file in csv_files:

    print(f"\nProcessing file: {input_file.name}")

    # Create main folder based on filename (without .csv)
    file_folder = output_root / input_file.stem
    file_folder.mkdir(parents=True, exist_ok=True)

    #
    # LOAD DATA
    #
    df = pd.read_csv(input_file)

    # Ensure proper sorting FIRST
    df = df.sort_values(["particle", "organoid_id", "frame"])

    #
    # COMPUTE DELTA D PER TRUE PAIR
    #
    df["frame_prev"] = df.groupby(["particle", "organoid_id"])["frame"].shift(1)
    df["distance_prev"] = df.groupby(["particle", "organoid_id"])["surface_distance_um"].shift(1)

    # Keep only strictly consecutive frames
    df_valid = df[df["frame"] == df["frame_prev"] + 1].copy()

    # Compute delta d
    df_valid["delta_d"] = df_valid["surface_distance_um"] - df_valid["distance_prev"]

    #
    # SAVE PER ORGANOID FOLDER
    #
    pairs = df_valid[["particle", "organoid_id"]].drop_duplicates()
    print(f"Total valid particle-organoid pairs found: {len(pairs)}")

    for _, row in pairs.iterrows():
        particle_id = row["particle"]
        organoid_id = row["organoid_id"]

        # Create organoid folder inside file folder
        organoid_folder = file_folder / f"organoid_{organoid_id}"
        organoid_folder.mkdir(parents=True, exist_ok=True)

        df_pair = df_valid[
            (df_valid["particle"] == particle_id) &
            (df_valid["organoid_id"] == organoid_id)
        ]

        if len(df_pair) == 0:
            continue

        output_csv = organoid_folder / f"particle_{particle_id}_delta_d.csv"
        df_pair[["frame_prev", "frame", "delta_d"]].to_csv(output_csv, index=False)

    print(f"Finished processing: {input_file.name}")

print("\nAll processing completed successfully.")

