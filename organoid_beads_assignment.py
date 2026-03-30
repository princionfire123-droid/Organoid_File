#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script organoid_beads_assignment.ipynb')


# In[1]:


import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import re

# --- Parameters ---
assign_radius_um = 50  # already in µm

# --- Folder paths ---
beads_folder = r"/NAS2/Nikita/Raw_data_3rd_Sep_2025/beads_file_um"
organoid_root = r"/NAS2/Nikita/Raw_data_3rd_Sep_2025/organoid_scaled_um_centroid"
output_folder = r"/NAS2/Nikita/Raw_data_3rd_Sep_2025/assigned_beads"

os.makedirs(output_folder, exist_ok=True)

# --- Extract FOV ID ---
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    return match.group(0) if match else None

# --- Assignment function (same logic as before, untouched) ---
def assign_nearest_organoid(beads_frame, organoids_frame, max_dist):

    if beads_frame.empty or organoids_frame.empty:
        beads_frame["organoid_id"] = np.nan
        beads_frame["organoid_x"] = np.nan
        beads_frame["organoid_y"] = np.nan
        beads_frame["distance_to_organoid"] = np.nan
        return beads_frame

    dx = beads_frame["x_um"].values[:, None] - organoids_frame["organoid_x"].values[None, :]
    dy = beads_frame["y_um"].values[:, None] - organoids_frame["organoid_y"].values[None, :]

    dist = np.sqrt(dx**2 + dy**2)

    nearest_idx = dist.argmin(axis=1)
    nearest_dist = dist.min(axis=1)

    assigned_ids = np.where(
        nearest_dist <= max_dist,
        organoids_frame["organoid_id"].values[nearest_idx],
        np.nan
    )

    assigned_x = np.where(
        nearest_dist <= max_dist,
        organoids_frame["organoid_x"].values[nearest_idx],
        np.nan
    )

    assigned_y = np.where(
        nearest_dist <= max_dist,
        organoids_frame["organoid_y"].values[nearest_idx],
        np.nan
    )

    beads_frame["organoid_id"] = assigned_ids
    beads_frame["organoid_x"] = assigned_x
    beads_frame["organoid_y"] = assigned_y
    beads_frame["distance_to_organoid"] = np.where(
        nearest_dist <= max_dist,
        nearest_dist,
        np.nan
    )

    return beads_frame


# --- Collect all organoid files from chunk folders ---
organoid_files = {}

for chunk in os.listdir(organoid_root):
    chunk_path = os.path.join(organoid_root, chunk)
    if not os.path.isdir(chunk_path):
        continue

    for file in os.listdir(chunk_path):
        if file.endswith(".xlsx"):
            fov_id = extract_id(file)
            if fov_id:
                organoid_files[fov_id] = os.path.join(chunk_path, file)

print("Found organoid files:", len(organoid_files))

# --- Process bead files ---
bead_files = [f for f in os.listdir(beads_folder) if f.endswith(".csv")]

print("Assigning nearest organoid per FOV and per frame...")

for bead_file in tqdm(bead_files):

    bead_id = extract_id(bead_file)

    if bead_id is None:
        print(f"Skipping {bead_file} - no FOV ID found")
        continue

    if bead_id not in organoid_files:
        print(f"No matching organoid file for {bead_file}")
        continue

    bead_path = os.path.join(beads_folder, bead_file)
    organoid_path = organoid_files[bead_id]

    # --- Load beads ---
    beads_df = pd.read_csv(bead_path)
    beads_df = beads_df[["frame_in_file", "particle", "x_um", "y_um"]]

    # --- Load organoids ---
    organoids_df = pd.read_excel(organoid_path)
    organoids_df = organoids_df[
        ["frame", "organoid_id", "x_scaled_um", "y_scaled_um"]
    ]

    organoids_df = organoids_df.rename(columns={
        "x_scaled_um": "organoid_x",
        "y_scaled_um": "organoid_y"
    })

    assigned_results = []

    # --- Per frame assignment ---
    for frame_no in beads_df["frame_in_file"].unique():

        b_frame = beads_df[beads_df["frame_in_file"] == frame_no].copy()
        o_frame = organoids_df[organoids_df["frame"] == frame_no].copy()

        b_frame = assign_nearest_organoid(
            b_frame,
            o_frame,
            assign_radius_um
        )

        assigned_results.append(b_frame)

    final_df = pd.concat(assigned_results, ignore_index=True)

    output_path = os.path.join(output_folder, f"{bead_id}_assigned.csv")
    final_df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")

print("All bead-organoid assignments completed successfully.")


# In[ ]:




