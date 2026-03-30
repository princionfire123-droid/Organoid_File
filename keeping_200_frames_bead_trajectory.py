#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script keeping_200_frames_bead_trajectory.ipynb')


# In[1]:


from pathlib import Path
import pandas as pd

# =========================
# INPUT & OUTPUT FOLDERS
# =========================

input_folder = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/surface_distance_24_feb_2026")
output_folder = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/200_beads_trajectory_surface_distance")

# Create output folder if it doesn't exist
output_folder.mkdir(parents=True, exist_ok=True)

# =========================
# PROCESS ALL CSV FILES
# =========================

for input_file in input_folder.glob("*.csv"):
    
    print(f"\nProcessing: {input_file.name}")
    
    # LOAD DATA
    df = pd.read_csv(input_file)

    # Clean essential columns
    df = df.dropna(subset=["particle", "frame"])
    df["frame"] = pd.to_numeric(df["frame"], errors="coerce")
    df = df.dropna(subset=["frame"])

    # STEP 1: REMOVE ROWS WITHOUT ORGANOID
    df["organoid_id"] = df["organoid_id"].replace("", pd.NA)
    df_clean = df.dropna(subset=["organoid_id"]).copy()

    # STEP 2: KEEP PARTICLES WITH >= 200 UNIQUE FRAMES
    frame_counts = df_clean.groupby("particle")["frame"].nunique()
    particles_to_keep = frame_counts[frame_counts >= 200].index
    df_final = df_clean[df_clean["particle"].isin(particles_to_keep)].copy()

    # Print summary
    print("Filtering complete")
    print(f"Original rows: {len(df)}")
    print(f"After organoid filter: {len(df_clean)}")
    print(f"After 200-frame filter: {len(df_final)}")
    print(f"Final particles count: {df_final['particle'].nunique()}")

    if not df_final.empty:
        print(f"Minimum frames per particle: {df_final.groupby('particle')['frame'].nunique().min()}")
    else:
        print("No particles passed 200-frame filter")

    # SAVE with modified filename
    output_file = output_folder / f"{input_file.stem}_200frames.csv"
    df_final.to_csv(output_file, index=False)

print("\nAll files processed successfully.")

