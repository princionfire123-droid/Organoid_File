#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script plot_bead_organoid_centroid_distance.ipynb')


# In[1]:


from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# INPUT (file OR folder)
input_path = Path("/NAS2/Nikita/Raw_data_3rd_Sep_2025/200_beads_trajectory_surface_distance")

# OUTPUT BASE FOLDER
output_base = Path("/NAS2/Nikita/Plot_centroid_surface_ditance/centroid_distance_plot")
output_base.mkdir(parents=True, exist_ok=True)

MIN_PER_FRAME = 10  # 10 minutes between consecutive frames

# CHECK IF FILE OR FOLDER
if input_path.is_file():
    csv_files = [input_path]
elif input_path.is_dir():
    csv_files = list(input_path.glob("*.csv"))
else:
    raise ValueError("Input path is neither a file nor a directory.")

# PROCESS EACH CSV
for input_file in csv_files:

    # Extract only FOV number like 00_02_00
    file_id = "_".join(input_file.stem.split("_")[:3])

    output_dir = output_base / f"organoid_surface_distance_plots_{file_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing: {input_file.name}")

    # LOAD DATA
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.strip().str.lower()

    # CONVERT FRAME TO HOURS
    df["time_hr"] = df["frame"] * (MIN_PER_FRAME / 60)

    # FIXED AXIS LIMITS (same for all graphs)
    x_min = 0
    x_max = 70

    y_min = -10
    y_max = 50

    # PLOT PER ORGANOID
    for organoid_id, organoid_df in df.groupby("organoid_id"):

        fig, ax1 = plt.subplots(figsize=(8, 6))

        # Unique beads
        bead_ids = organoid_df["particle"].unique()
        num_beads = len(bead_ids)

        # Color Logic for many beads
        cmap = plt.cm.hsv
        colors = [cmap(i / num_beads) for i in range(num_beads)]

        # Plot bead trajectories
        for i, bead_id in enumerate(bead_ids):

            bead_df = organoid_df[organoid_df["particle"] == bead_id]

            ax1.plot(
                bead_df["time_hr"],
                bead_df["distance_to_organoid"],
                color=colors[i],
                alpha=0.9,
                linewidth=1.3,
            )

        ax1.set_xlabel("Time (hours)")
        ax1.set_ylabel("Organoid-bead centroid distance (um)")

        # FIXED AXIS SCALE
        ax1.set_xlim(x_min, x_max)
        ax1.set_ylim(y_min, y_max)

        # FIXED TICKS
        ax1.set_xticks([0, 10, 20, 30, 40, 50, 60, 70, 80])
        ax1.set_yticks([-10, 0, 10, 20, 30, 40, 50, 60])

        ax1.axhline(0)

        # UPDATED TITLE FORMAT
        plt.title(f"{file_id}_organoid-bead centroid distance - organoid {int(organoid_id)}")

        plt.tight_layout()

        save_path = output_dir / f"organoid_{int(organoid_id)}.png"
        plt.savefig(save_path, dpi=300)
        plt.close()

    print(f"Finished: {file_id}")

print("All processing completed successfully.")

