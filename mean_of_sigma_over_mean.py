#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('jupyter nbconvert --to script mean_of_sigma_over_mean.ipynb')


# In[2]:


import pandas as pd
from pathlib import Path

# -------- INPUT ROOT FOLDER --------
input_root = Path("/NAS2/Nikita/sigma_by_mean")  # <-- change this

# -------- OUTPUT CSV PATH --------
output_csv_path = Path("/NAS2/Nikita/sigma_over_mean_mean_24_march/output_sigma_over_mean_summary.csv")  # <-- change if needed

results = []

# -------- TRAVERSE FOLDERS --------
for fov_folder in input_root.iterdir():
    if fov_folder.is_dir():
        fov_name = fov_folder.name  # e.g., 00_02_07

        # Iterate through organoid folders
        for organoid_folder in fov_folder.iterdir():
            if organoid_folder.is_dir():
                organoid_name = organoid_folder.name

                # Look for CSV file inside organoid folder
                csv_files = list(organoid_folder.glob("*.csv"))

                if len(csv_files) == 0:
                    continue  # skip if no CSV found

                csv_file = csv_files[0]  # assuming one CSV per organoid

                try:
                    df = pd.read_csv(csv_file)

                    if "sigma_over_mean" in df.columns:
                        mean_val = df["sigma_over_mean"].dropna().mean()

                        results.append({
                            "FOV": fov_name,
                            "Organoid": organoid_name,
                            "Mean_sigma_over_mean": mean_val
                        })
                    else:
                        print(f"'sigma_over_mean' column not found in {csv_file}")

                except Exception as e:
                    print(f"Error processing {csv_file}: {e}")

# -------- SAVE RESULTS --------
output_df = pd.DataFrame(results)

# Create output directory if it doesn't exist
output_csv_path.parent.mkdir(parents=True, exist_ok=True)

# Save CSV
output_df.to_csv(output_csv_path, index=False)

print(f"Results saved to: {output_csv_path}")


# In[1]:


import pandas as pd
from pathlib import Path

# -------- INPUT ROOT FOLDER --------
input_root = Path("/NAS2/Nikita/sigma_by_mean")  # <-- change this

# -------- OUTPUT CSV PATH --------
output_csv_path = Path("/NAS2/Nikita/sigma_over_mean_mean_24_march/output_sigma_over_mean_summary.csv")  # <-- change this

results = []

# -------- TRAVERSE FOLDERS --------
for fov_folder in input_root.iterdir():
    if fov_folder.is_dir():
        fov_name = fov_folder.name  # e.g., 00_02_07

        # Iterate through organoid folders
        for organoid_folder in fov_folder.iterdir():
            if organoid_folder.is_dir():
                organoid_name = organoid_folder.name

                # Look for CSV file inside organoid folder
                csv_files = list(organoid_folder.glob("*.csv"))

                if len(csv_files) == 0:
                    continue  # skip if no CSV found

                csv_file = csv_files[0]  # assuming one CSV per organoid

                try:
                    df = pd.read_csv(csv_file)

                    if "sigma_over_mean" in df.columns:
                        mean_val = df["sigma_over_mean"].dropna().mean()

                        results.append({
                            "FOV": fov_name,
                            "Organoid": organoid_name,
                            "Mean_sigma_over_mean": mean_val
                        })

                except Exception as e:
                    print(f"Error processing {csv_file}: {e}")

# -------- SAVE RESULTS --------
output_df = pd.DataFrame(results)
output_df.to_csv(output_csv_path, index=False)

print(f"Results saved to: {output_csv_path}")


# In[ ]:




