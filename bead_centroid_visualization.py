#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os
import tifffile
import pandas as pd
import numpy as np
import cv2
from tqdm import tqdm

# ---- INPUT FILES (single pair) ----
tif_path = "/NAS2/Nikita/3sep2025_beads_exp_10min/t_stack_25/00_04_07.tif"
csv_path = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/200_beads_trajectory_surface_distance/00_04_07_surface_distance_200frames.csv"

# ---- OUTPUT FOLDER ----
output_folder = "/NAS2/Nikita/beads_visulatitoon_tif/00_04_07"
os.makedirs(output_folder, exist_ok=True)

# ---- PIXEL CONVERSION ----
um_per_pixel = 0.32

# ---- COLOR FUNCTION ----
def get_particle_color(pid):
    np.random.seed(pid)
    color = tuple(np.random.randint(50,255,3).tolist())
    return (int(color[0]), int(color[1]), int(color[2]))

# ---- LOAD DATA ----
stack = tifffile.imread(tif_path)
df = pd.read_csv(csv_path)

# ---- CONVERT um → pixels ----
df["x_px"] = df["x_um"] / um_per_pixel
df["y_px"] = df["y_um"] / um_per_pixel

frames, height, width = stack.shape

# ---- PROCESS EACH ORGANOID ----
organoid_ids = df["organoid_id"].unique()

for organoid in organoid_ids:
    print("Processing Organoid:", organoid)

    organoid_df = df[df["organoid_id"] == organoid]

    output_video = os.path.join(
        output_folder,
        f"organoid_{organoid}.mp4"
    )

    # ---- VIDEO WRITER ----
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

    # ---- PROCESS FRAMES ----
    for frame in tqdm(range(frames), desc=f"Organoid {organoid}", leave=False):
        image = stack[frame]

        if image.dtype != np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            image = image.astype(np.uint8)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        beads = organoid_df[organoid_df["frame"] == frame]

        for _, bead in beads.iterrows():
            x = int(bead["x_px"])
            y = int(bead["y_px"])
            pid = int(bead["particle"])

            color = get_particle_color(pid)

            # draw circle
            cv2.circle(image, (x, y), 8, color, 1, cv2.LINE_AA)

            # label
            cv2.putText(
                image,
                str(pid),
                (x + 10, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )

        video.write(image)

    video.release()
    print("Saved:", output_video)

print("Done ✅")


# In[ ]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2
from tqdm import tqdm   # progress bar


# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/3sep2025_beads_exp_10min/t_stack_25"
bead_csv_folder = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/200_beads_trajectory_surface_distance"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output_all_progress_overnight"

os.makedirs(output_folder, exist_ok=True)


# -------- PIXEL CONVERSION --------
um_per_pixel = 0.32


# -------- FUNCTION TO EXTRACT SAMPLE ID --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- GENERATE COLOR FOR EACH PARTICLE --------
def get_particle_color(pid):
    np.random.seed(pid)
    color = tuple(np.random.randint(50,255,3).tolist())
    return (int(color[0]), int(color[1]), int(color[2]))


# -------- BUILD TIFF DICTIONARY --------
tif_dict = {}
for file in os.listdir(tif_folder):
    if file.endswith(".tif") or file.endswith(".tiff"):
        sample_id = extract_id(file)
        if sample_id:
            tif_dict[sample_id] = os.path.join(tif_folder, file)


# -------- BUILD CSV DICTIONARY --------
csv_dict = {}
for file in os.listdir(bead_csv_folder):
    if file.endswith(".csv"):
        sample_id = extract_id(file)
        if sample_id:
            csv_dict[sample_id] = os.path.join(bead_csv_folder, file)


# -------- MATCH FILES --------
tif_ids = set(tif_dict.keys())
csv_ids = set(csv_dict.keys())

common_ids = tif_ids.intersection(csv_ids)
missing_csv = tif_ids - csv_ids
missing_tif = csv_ids - tif_ids

print("--------------------------------------------------")
print("Matched datasets:", len(common_ids))
print("TIFF without CSV:", len(missing_csv))
print("CSV without TIFF:", len(missing_tif))
print("--------------------------------------------------")

if missing_csv:
    print("TIFF files missing CSV:")
    for m in missing_csv:
        print("   ", m)

if missing_tif:
    print("CSV files missing TIFF:")
    for m in missing_tif:
        print("   ", m)

print("--------------------------------------------------")


# -------- PROCESS EACH MATCHED FOV --------
for sample_id in tqdm(common_ids, desc="Processing FOVs"):

    tif_path = tif_dict[sample_id]
    csv_path = csv_dict[sample_id]

    print("Processing FOV:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    # -------- CONVERT µm → PIXELS --------
    df["x_px"] = df["x_um"] / um_per_pixel
    df["y_px"] = df["y_um"] / um_per_pixel

    frames, height, width = stack.shape

    # -------- GET UNIQUE ORGANOIDS --------
    organoid_ids = df["organoid_id"].unique()

    for organoid in organoid_ids:

        print("  Organoid:", organoid)

        organoid_df = df[df["organoid_id"] == organoid]

        output_video = os.path.join(
            output_folder,
            f"{sample_id}_organoid_{organoid}.mp4"
        )

        # -------- VIDEO WRITER --------
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

        # -------- PROCESS FRAMES --------
        for frame in tqdm(range(frames), desc=f"{sample_id} Organoid {organoid}", leave=False):

            image = stack[frame]

            if image.dtype != np.uint8:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                image = image.astype(np.uint8)

            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            beads = organoid_df[organoid_df["frame"] == frame]

            for _, bead in beads.iterrows():

                x = int(bead["x_px"])
                y = int(bead["y_px"])
                pid = int(bead["particle"])

                color = get_particle_color(pid)

                # draw thin outline circle
                cv2.circle(image, (x, y), 8, color, 1, cv2.LINE_AA)

                # label bead ID
                cv2.putText(
                    image,
                    str(pid),
                    (x + 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )

            video.write(image)

        video.release()

        print("  Saved:", output_video)


print("All videos created successfully")


# In[ ]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/3sep2025_beads_exp_10min/t_stack_25"
bead_csv_folder = "/NAS2/Nikita/Raw_data_3rd_Sep_2025/200_beads_trajectory_surface_distance"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output_all"

os.makedirs(output_folder, exist_ok=True)

# -------- PIXEL CONVERSION --------
um_per_pixel = 0.32


# -------- FUNCTION TO EXTRACT SAMPLE ID --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- GENERATE COLOR FOR EACH PARTICLE --------
def get_particle_color(pid):
    np.random.seed(pid)
    color = tuple(np.random.randint(50,255,3).tolist())
    return (int(color[0]), int(color[1]), int(color[2]))


# -------- BUILD TIFF DICTIONARY --------
tif_dict = {}
for file in os.listdir(tif_folder):
    if file.endswith(".tif") or file.endswith(".tiff"):
        sample_id = extract_id(file)
        if sample_id:
            tif_dict[sample_id] = os.path.join(tif_folder, file)


# -------- BUILD CSV DICTIONARY --------
csv_dict = {}
for file in os.listdir(bead_csv_folder):
    if file.endswith(".csv"):
        sample_id = extract_id(file)
        if sample_id:
            csv_dict[sample_id] = os.path.join(bead_csv_folder, file)


# -------- MATCH FILES --------
tif_ids = set(tif_dict.keys())
csv_ids = set(csv_dict.keys())

common_ids = tif_ids.intersection(csv_ids)
missing_csv = tif_ids - csv_ids
missing_tif = csv_ids - tif_ids

print("--------------------------------------------------")
print("Matched datasets:", len(common_ids))
print("TIFF without CSV:", len(missing_csv))
print("CSV without TIFF:", len(missing_tif))
print("--------------------------------------------------")

if missing_csv:
    print("⚠ TIFF files missing CSV:")
    for m in missing_csv:
        print("   ", m)

if missing_tif:
    print("⚠ CSV files missing TIFF:")
    for m in missing_tif:
        print("   ", m)

print("--------------------------------------------------")


# -------- PROCESS EACH MATCHED FOV --------
for sample_id in common_ids:

    tif_path = tif_dict[sample_id]
    csv_path = csv_dict[sample_id]

    print("Processing FOV:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    # -------- CONVERT µm → PIXELS --------
    df["x_px"] = df["x_um"] / um_per_pixel
    df["y_px"] = df["y_um"] / um_per_pixel

    frames, height, width = stack.shape

    # -------- GET UNIQUE ORGANOIDS --------
    organoid_ids = df["organoid_id"].unique()

    for organoid in organoid_ids:

        print("  Organoid:", organoid)

        organoid_df = df[df["organoid_id"] == organoid]

        output_video = os.path.join(
            output_folder,
            f"{sample_id}_organoid_{organoid}.mp4"
        )

        # -------- VIDEO WRITER --------
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

        # -------- PROCESS FRAMES --------
        for frame in range(frames):

            image = stack[frame]

            if image.dtype != np.uint8:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                image = image.astype(np.uint8)

            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            beads = organoid_df[organoid_df["frame"] == frame]

            for _, bead in beads.iterrows():

                x = int(bead["x_px"])
                y = int(bead["y_px"])
                pid = int(bead["particle"])

                color = get_particle_color(pid)

                # draw thin outline circle
                cv2.circle(image, (x, y), 8, color, 1, cv2.LINE_AA)

                # label bead ID
                cv2.putText(
                    image,
                    str(pid),
                    (x + 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )

            video.write(image)

        video.release()

        print("  Saved:", output_video)


print("All videos created successfully")


# In[12]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/tif_folder"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/csv_folder"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output_no_trajectory_only_bead"

os.makedirs(output_folder, exist_ok=True)

# -------- PIXEL CONVERSION --------
um_per_pixel = 0.32


# -------- FUNCTION TO EXTRACT SAMPLE ID --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- GENERATE COLOR FOR EACH PARTICLE --------
def get_particle_color(pid):
    np.random.seed(pid)
    color = tuple(np.random.randint(50,255,3).tolist())
    return (int(color[0]), int(color[1]), int(color[2]))


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)
    if sample_id is None:
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print("No CSV found for", tif_file)
        continue


    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)

    print("Processing:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    # -------- CONVERT µm → PIXELS --------
    df["x_px"] = df["x_um"] / um_per_pixel
    df["y_px"] = df["y_um"] / um_per_pixel

    frames, height, width = stack.shape

    # -------- GET UNIQUE ORGANOIDS --------
    organoid_ids = df["organoid_id"].unique()

    for organoid in organoid_ids:

        print("Processing organoid:", organoid)

        organoid_df = df[df["organoid_id"] == organoid]

        output_video = os.path.join(
            output_folder,
            f"{sample_id}_organoid_{organoid}.mp4"
        )

        # -------- VIDEO WRITER --------
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

        # -------- PROCESS FRAMES --------
        for frame in range(frames):

            image = stack[frame]

            # normalize if not 8-bit
            if image.dtype != np.uint8:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                image = image.astype(np.uint8)

            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            beads = organoid_df[organoid_df["frame_in_file"] == frame]

            for _, bead in beads.iterrows():

                x = int(bead["x_px"])
                y = int(bead["y_px"])
                pid = int(bead["particle"])

                color = get_particle_color(pid)

                # draw thin outline circle (bead visible inside)
                cv2.circle(image, (x, y), 8, color, 1, cv2.LINE_AA)

                # label bead ID
                cv2.putText(
                    image,
                    str(pid),
                    (x + 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )

            video.write(image)

        video.release()

        print("Saved:", output_video)


print("All videos created successfully")


# In[11]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/tif_folder"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/csv_folder"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output_organoid_bead_good_viz"

os.makedirs(output_folder, exist_ok=True)

# -------- PIXEL CONVERSION --------
um_per_pixel = 0.32

# -------- TRAIL LENGTH --------
trail_length = 10


# -------- FUNCTION TO EXTRACT SAMPLE ID --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- GENERATE COLOR FOR EACH PARTICLE --------
def get_particle_color(pid):
    np.random.seed(pid)
    color = tuple(np.random.randint(50,255,3).tolist())
    return (int(color[0]), int(color[1]), int(color[2]))


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)
    if sample_id is None:
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print("No CSV found for", tif_file)
        continue


    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)

    print("Processing:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    # -------- CONVERT µm → PIXELS --------
    df["x_px"] = df["x_um"] / um_per_pixel
    df["y_px"] = df["y_um"] / um_per_pixel

    frames, height, width = stack.shape

    # -------- GET UNIQUE ORGANOIDS --------
    organoid_ids = df["organoid_id"].unique()

    for organoid in organoid_ids:

        print("Processing organoid:", organoid)

        organoid_df = df[df["organoid_id"] == organoid]

        output_video = os.path.join(
            output_folder,
            f"{sample_id}_organoid_{organoid}.mp4"
        )

        trajectories = {}

        # -------- VIDEO WRITER --------
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

        # -------- PROCESS FRAMES --------
        for frame in range(frames):

            image = stack[frame]

            # normalize if not 8-bit
            if image.dtype != np.uint8:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                image = image.astype(np.uint8)

            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            beads = organoid_df[organoid_df["frame_in_file"] == frame]

            for _, bead in beads.iterrows():

                x = int(bead["x_px"])
                y = int(bead["y_px"])
                pid = int(bead["particle"])

                color = get_particle_color(pid)

                # initialize trajectory
                if pid not in trajectories:
                    trajectories[pid] = []

                trajectories[pid].append((x, y))

                if len(trajectories[pid]) > trail_length:
                    trajectories[pid].pop(0)

                # draw trajectory trail
                pts = trajectories[pid]
                for i in range(1, len(pts)):
                    cv2.line(image, pts[i-1], pts[i], color, 2)

                # draw thin outline circle (bead visible inside)
                cv2.circle(image, (x, y), 8, color, 1, cv2.LINE_AA)

                # label bead ID
                cv2.putText(
                    image,
                    str(pid),
                    (x + 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )

            video.write(image)

        video.release()

        print("Saved:", output_video)


print("All videos created successfully")


# In[10]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/tif_folder"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/csv_folder"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output_organoid_wise"

os.makedirs(output_folder, exist_ok=True)

# -------- PIXEL CONVERSION --------
um_per_pixel = 0.32


# -------- FUNCTION TO EXTRACT ID --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)
    if sample_id is None:
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print("No CSV found for", tif_file)
        continue


    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)

    print("Processing:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    # -------- CONVERT UM TO PIXEL --------
    df["x_px"] = df["x_um"] / um_per_pixel
    df["y_px"] = df["y_um"] / um_per_pixel

    frames, height, width = stack.shape

    # -------- GET ORGANOID IDS --------
    organoid_ids = df["organoid_id"].unique()

    for organoid in organoid_ids:

        print("Processing organoid:", organoid)

        organoid_df = df[df["organoid_id"] == organoid]

        output_video = os.path.join(
            output_folder,
            f"{sample_id}_organoid_{organoid}.mp4"
        )

        # store trajectories
        trajectories = {}

        # video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

        for frame in range(frames):

            image = stack[frame]

            if image.dtype != np.uint8:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                image = image.astype(np.uint8)

            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            beads = organoid_df[organoid_df["frame_in_file"] == frame]

            for _, bead in beads.iterrows():

                x = int(bead["x_px"])
                y = int(bead["y_px"])
                pid = int(bead["particle"])

                # initialize trajectory
                if pid not in trajectories:
                    trajectories[pid] = []

                trajectories[pid].append((x, y))

                # keep last 10 positions
                if len(trajectories[pid]) > 10:
                    trajectories[pid].pop(0)

                # draw trajectory
                pts = trajectories[pid]
                for i in range(1, len(pts)):
                    cv2.line(image, pts[i-1], pts[i], (0,255,255), 2)

                # draw bead
                cv2.circle(image, (x, y), 10, (0,0,255), 2)

                cv2.putText(
                    image,
                    str(pid),
                    (x + 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,255,0),
                    1
                )

            video.write(image)

        video.release()

        print("Saved:", output_video)


print("All videos created successfully")


# In[9]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/tif_folder"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/csv_folder"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output_colour_beads_2"

os.makedirs(output_folder, exist_ok=True)

# -------- SELECT BEADS TO HIGHLIGHT --------
# particle_id : (B, G, R)
highlight_beads = {
    147397: (0,0,255),      # red
    147430: (0,255,0),     # green
    150643: (255,0,0),     # blue
    147399: (0,255,255),   # yellow
    151555: (255,0,255)    # purple
}

# how many frames of trail to show
trail_length = 10


# -------- FUNCTION TO EXTRACT ID --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)
    if sample_id is None:
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print("No CSV found for", tif_file)
        continue


    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)
    output_video = os.path.join(output_folder, f"{sample_id}_beads.mp4")

    print("Processing:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    frames, height, width = stack.shape

    # -------- STORE TRAJECTORIES --------
    trajectories = {pid: [] for pid in highlight_beads.keys()}

    # -------- VIDEO WRITER --------
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

    # -------- PROCESS FRAMES --------
    for frame in range(frames):

        image = stack[frame]

        if image.dtype != np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            image = image.astype(np.uint8)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        beads = df[df["frame_in_file"] == frame]

        for _, bead in beads.iterrows():

            x = int(bead["x"])
            y = int(bead["y"])
            pid = int(bead["particle"])

            if pid not in highlight_beads:
                continue

            color = highlight_beads[pid]

            # save trajectory
            trajectories[pid].append((x, y))

            # keep only last N frames
            if len(trajectories[pid]) > trail_length:
                trajectories[pid].pop(0)

            # draw trajectory line
            pts = trajectories[pid]
            for i in range(1, len(pts)):
                cv2.line(image, pts[i-1], pts[i], color, 2)

            # draw circle
            cv2.circle(image, (x, y), 12, color, 3)

            # label particle id
            cv2.putText(
                image,
                str(pid),
                (x + 14, y + 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        video.write(image)

    video.release()

    print("Saved video:", output_video)


print("All videos created successfully!")


# In[5]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/tif_folder"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/csv_folder"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/video_output"

os.makedirs(output_folder, exist_ok=True)


# -------- FUNCTION TO EXTRACT ID (00_02_07 etc) --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)
    if sample_id is None:
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print(f"No CSV found for {tif_file}")
        continue


    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)

    output_video = os.path.join(output_folder, f"{sample_id}_beads.mp4")

    print("Processing:", sample_id)

    # -------- LOAD DATA --------
    stack = tifffile.imread(tif_path)
    df = pd.read_csv(csv_path)

    frames, height, width = stack.shape

    # -------- CREATE VIDEO WRITER --------
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

    # -------- PROCESS EACH FRAME --------
    for frame in range(frames):

        image = stack[frame]

        if image.dtype != np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            image = image.astype(np.uint8)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        beads = df[df["frame_in_file"] == frame]

        for _, bead in beads.iterrows():

            x = int(bead["x"])
            y = int(bead["y"])
            pid = int(bead["particle"])

            cv2.circle(image, (x, y), 10, (0, 0, 255), 2)

            cv2.putText(
                image,
                str(pid),
                (x + 12, y + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1
            )

        video.write(image)

    video.release()

    print("Saved video:", output_video)


print("All videos created successfully!")


# In[4]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/tif_folder"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/csv_folder"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/centroid_output"

os.makedirs(output_folder, exist_ok=True)

print("Folders loaded successfully")


# -------- FUNCTION TO EXTRACT ID (00_02_07 etc) --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]

print(f"Found {len(tif_files)} tif files")
print(f"Found {len(csv_files)} csv files")


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)

    if sample_id is None:
        print(f"Skipping file (pattern not found): {tif_file}")
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print(f"No CSV found for {tif_file}")
        continue


    # -------- FILE PATHS --------
    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)

    output_path = os.path.join(output_folder, f"{sample_id}_annotated.tif")

    print("\nProcessing dataset:", sample_id)
    print("TIF:", tif_path)
    print("CSV:", csv_path)

    # -------- LOAD DATA --------
    print("Loading TIFF stack...")
    stack = tifffile.imread(tif_path)

    print("Loading CSV file...")
    df = pd.read_csv(csv_path)

    # Confirm required columns exist
    required_columns = ["x", "y", "particle", "frame_in_file"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    frames = stack.shape[0]
    print("Total frames:", frames)

    annotated_frames = []

    # -------- PROCESS EACH FRAME --------
    for frame in range(frames):

        image = stack[frame]

        # Convert to 8-bit if needed
        if image.dtype != np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            image = image.astype(np.uint8)

        # Convert to color so we can draw colored markers
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        beads = df[df["frame_in_file"] == frame]

        for _, bead in beads.iterrows():

            x = int(bead["x"])
            y = int(bead["y"])
            particle_id = int(bead["particle"])

            # Draw bead marker
            cv2.circle(image, (x, y), 10, (0, 0, 255), 2)

            # Write particle ID
            cv2.putText(
                image,
                str(particle_id),
                (x + 12, y + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
                cv2.LINE_AA
            )

        annotated_frames.append(image)

    annotated_stack = np.array(annotated_frames)

    # -------- SAVE RESULT --------
    print("Saving annotated TIFF stack...")
    tifffile.imwrite(output_path, annotated_stack)

    print("Finished:", sample_id)


print("\nAll files processed successfully!")


# In[2]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FOLDER PATHS --------
tif_folder = "/NAS2/Nikita/visulization_centroid_bead/00_02_07.tif"
bead_csv_folder = "/NAS2/Nikita/visulization_centroid_bead/00_02_07.tif.csv"
output_folder = "/NAS2/Nikita/visulization_centroid_bead/cenrtroid_bead_viz"

os.makedirs(output_folder, exist_ok=True)


# -------- FUNCTION TO EXTRACT ID (00_02_07 etc) --------
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# -------- LIST FILES --------
tif_files = [f for f in os.listdir(tif_folder) if f.endswith(".tif") or f.endswith(".tiff")]
csv_files = [f for f in os.listdir(bead_csv_folder) if f.endswith(".csv")]


# -------- PROCESS EACH TIFF --------
for tif_file in tif_files:

    sample_id = extract_id(tif_file)

    if sample_id is None:
        continue

    # find matching CSV
    csv_match = None
    for csv_file in csv_files:
        if sample_id in csv_file:
            csv_match = csv_file
            break

    if csv_match is None:
        print(f"No CSV found for {tif_file}")
        continue


    # -------- FILE PATHS --------
    tif_path = os.path.join(tif_folder, tif_file)
    csv_path = os.path.join(bead_csv_folder, csv_match)

    output_path = os.path.join(output_folder, f"{sample_id}_annotated.tif")

    print("Processing:", sample_id)

    # -------- LOAD DATA --------
    print("Loading TIFF stack...")
    stack = tifffile.imread(tif_path)

    print("Loading CSV file...")
    df = pd.read_csv(csv_path)

    # Confirm required columns exist
    required_columns = ["x", "y", "particle", "frame_in_file"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    frames, height, width = stack.shape
    print(f"Stack loaded: {frames} frames")

    annotated_frames = []

    # -------- PROCESS EACH FRAME --------
    for frame in range(frames):

        image = stack[frame]

        # Convert to 8-bit if needed
        if image.dtype != np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            image = image.astype(np.uint8)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        beads = df[df["frame_in_file"] == frame]

        for _, bead in beads.iterrows():

            x = int(bead["x"])
            y = int(bead["y"])
            particle_id = int(bead["particle"])

            cv2.circle(image, (x, y), 10, (0, 0, 255), 2)

            cv2.putText(
                image,
                str(particle_id),
                (x + 12, y + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
                cv2.LINE_AA
            )

        annotated_frames.append(image)

    annotated_stack = np.array(annotated_frames)

    # -------- SAVE RESULT --------
    print("Saving annotated TIFF stack...")
    tifffile.imwrite(output_path, annotated_stack)

    print("Finished:", sample_id)


print("All files processed!")


# In[ ]:


import os
import re
import tifffile
import pandas as pd
import numpy as np
import cv2

# --- Folder paths ---
beads_folder = r"/NAS2/Nikita/visulization_centroid_bead/beads_file"
organoid_folder = r"/NAS2/Nikita/visulization_centroid_bead/organoid_file"
output_folder = r"/NAS2/Nikita/visulization_centroid_bead/assigned_beads"

os.makedirs(output_folder, exist_ok=True)

print("Folders loaded successfully")

# --- Function to extract pattern like 00_03_04 ---
def extract_id(filename):
    match = re.search(r"\d{2}_\d{2}_\d{2}", filename)
    if match:
        return match.group(0)
    return None


# --- Build file dictionaries ---
bead_files = {}
for f in os.listdir(beads_folder):
    if f.endswith(".csv"):
        key = extract_id(f)
        if key:
            bead_files[key] = os.path.join(beads_folder, f)

tif_files = {}
for f in os.listdir(organoid_folder):
    if f.endswith(".tif") or f.endswith(".tiff"):
        key = extract_id(f)
        if key:
            tif_files[key] = os.path.join(organoid_folder, f)


# --- Process matching files ---
common_ids = set(bead_files.keys()).intersection(tif_files.keys())

print(f"Found {len(common_ids)} matching datasets")

for sample_id in common_ids:

    print(f"Processing {sample_id}")

    csv_path = bead_files[sample_id]
    tif_path = tif_files[sample_id]

    df = pd.read_csv(csv_path)
    stack = tifffile.imread(tif_path)

    frames = stack.shape[0]
    annotated_frames = []

    for frame in range(frames):

        img = stack[frame]

        # normalize to 8-bit
        if img.dtype != np.uint8:
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        beads = df[df["frame_in_file"] == frame]

        for _, bead in beads.iterrows():

            x = int(bead["x"])
            y = int(bead["y"])
            pid = int(bead["particle"])

            cv2.circle(img, (x, y), 10, (0, 0, 255), 2)

            cv2.putText(
                img,
                str(pid),
                (x + 12, y + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1
            )

        annotated_frames.append(img)

    annotated_stack = np.array(annotated_frames)

    output_path = os.path.join(output_folder, f"{sample_id}_annotated.tif")

    tifffile.imwrite(output_path, annotated_stack)

    print(f"Saved: {output_path}")

print("All files processed successfully")


# In[1]:


import tifffile
import pandas as pd
import numpy as np
import cv2

# -------- FILE PATHS --------
tif_path = "NAS2/Nikita/visulization_centroid_bead/00_02_07.tif"
csv_path = "NAS2/Nikita/visulization_centroid_bead/00_02_07.tif.csv"
output_path = "NAS2/Nikita/visulization_centroid_bead/centroid_output.tif"

# -------- LOAD DATA --------
print("Loading TIFF stack...")
stack = tifffile.imread(tif_path)   # shape: (frames, height, width)

print("Loading CSV file...")
df = pd.read_csv(csv_path)

# Confirm required columns exist
required_columns = ["x", "y", "particle", "frame_in_file"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

frames, height, width = stack.shape
print(f"Stack loaded: {frames} frames, size {height}x{width}")

annotated_frames = []

# -------- PROCESS EACH FRAME --------
for frame in range(frames):

    image = stack[frame]

    # Convert to 8-bit if needed
    if image.dtype != np.uint8:
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        image = image.astype(np.uint8)

    # Convert to color so we can draw colored markers
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Get beads in this frame
    beads = df[df["frame_in_file"] == frame]

    for _, bead in beads.iterrows():

        x = int(bead["x"])
        y = int(bead["y"])
        particle_id = int(bead["particle"])

        # Draw bead marker
        cv2.circle(image, (x, y), 10, (0, 0, 255), 2)

        # Write particle ID
        cv2.putText(
            image,
            str(particle_id),
            (x + 12, y + 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 0),
            1,
            cv2.LINE_AA
        )

    annotated_frames.append(image)

annotated_stack = np.array(annotated_frames)

# -------- SAVE RESULT --------
print("Saving annotated TIFF stack...")
tifffile.imwrite(output_path, annotated_stack)

print("Finished!")


# In[ ]:




