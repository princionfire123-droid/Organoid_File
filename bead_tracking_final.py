#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script bead_tracking_final.ipynb')


# In[ ]:


import os
import glob
import tifffile
import trackpy as tp
import pandas as pd
import numpy as np
import cv2
from tqdm import tqdm

# === USER PARAMETERS ===
input_folder = "/NAS2/Nikita/3sep2025_beads_exp_10min/t_stack_25"   # Folder with TIFF stacks
output_folder = "/NAS2/Nikita/3sep2025_beads_exp_10min/beads_dark_trajectories"
os.makedirs(output_folder, exist_ok=True)

pixel_size = 0.32   # µm/px
ecc_cutoff = 0.5    # Keep mostly circular beads

# Two best parameter sets
d_minmass_pairs = [(21, 2000), (19, 1500)]

# Linking parameters
search_range_px = 5
memory = 3
make_global_frame_index = True

# === FIND TIFF FILES ===
tif_files = sorted(glob.glob(os.path.join(input_folder, "*.tif")))
if not tif_files:
    raise ValueError(f"No .tif files found in {input_folder}!")
print(f"Found {len(tif_files)} .tif files. Processing...")

# === INITIALIZE ===
all_particles = []
global_frame_offset = 0

# === PROCESS EACH FILE ===
for tif_path in tif_files:
    fname = os.path.basename(tif_path)
    print(f"\nProcessing {fname} ...")
    frames = tifffile.imread(tif_path)
    n_frames = frames.shape[0]

    for i in tqdm(range(n_frames), desc=f"Detecting in {fname}", unit="frame"):
        frame = frames[i]

        # --- Convert to grayscale if RGB ---
        if frame.ndim == 3:
            frame_gray = frame.mean(axis=-1).astype('uint8')
        else:
            frame_gray = frame.astype('uint8')

        # --- ENHANCE FOR DARK BEADS ---
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(32, 32))
        frame_eq = clahe.apply(frame_gray)

        # Morphological top-hat to highlight dark spots
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        dark_enhanced = cv2.morphologyEx(255 - frame_eq, cv2.MORPH_TOPHAT, kernel)

        # Normalize for better contrast
        dark_enhanced = cv2.normalize(dark_enhanced, None, 0, 255, cv2.NORM_MINMAX)

        # --- DETECT BEADS FOR EACH PARAMETER SET ---
        for d, mm in d_minmass_pairs:
            f = tp.locate(dark_enhanced, diameter=d, minmass=mm, characterize=True)
            if f is not None and not f.empty:
                f = f[f['ecc'] < ecc_cutoff].copy()
                f['frame_in_file'] = i
                f['diameter'] = d
                f['minmass_used'] = mm
                f['source_file'] = fname
                f['frame'] = (i + global_frame_offset) if make_global_frame_index else i
                all_particles.append(f)

    global_frame_offset += n_frames

# === COMBINE DETECTIONS ===
if not all_particles:
    raise ValueError("No dark beads detected in any file!")

particles_df = pd.concat(all_particles, ignore_index=True)
particles_outfile = os.path.join(output_folder, "all_detected_dark_beads.csv")
particles_df.to_csv(particles_outfile, index=False)

print(f"\nSaved detected beads to: {particles_outfile}")
print(f"Total detected bead entries: {len(particles_df)}")

# === LINK TRAJECTORIES ===
print("\nLinking dark bead trajectories...")
trajectories = tp.link_df(particles_df, search_range=search_range_px, memory=memory)
trajectories_outfile = os.path.join(output_folder, "linked_dark_trajectories.csv")
trajectories.to_csv(trajectories_outfile, index=False)

print(f"Saved {trajectories['particle'].nunique()} trajectories to: {trajectories_outfile}")

# === SUMMARY ===
print("\nExample columns in detections: ", list(particles_df.columns))
print("Coordinates (x, y) are in pixels of the original images (2000x2000).")

