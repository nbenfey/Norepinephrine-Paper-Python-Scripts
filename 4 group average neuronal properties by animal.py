import pandas as pd
import glob
import os

# Define the directory where the files are located
directory = "/Users/nbenfey/Desktop/PythonProcessing"

# Pattern to match files ending with _average_neuronal_properties.csv
file_pattern = os.path.join(directory, "*_average_neuronal_properties.csv")

# Find all files in the directory matching the pattern
csv_files = glob.glob(file_pattern)

# Sort the file paths alphabetically
csv_files = sorted(csv_files)

# Prepare a list to store the averages for each file
averages_list = []

# Prepare lists to store the Selectivity Index (Peak) values for Baseline and Norepinephrine
selectivity_index_baseline = []
selectivity_index_norepinephrine = []

# Loop through each file
for file_path in csv_files:
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Ensure there are at least 7 columns
        if df.shape[1] >= 7:
            # Get the column names based on their indices
            col_names = df.columns[[4, 5, 6]]

            # Calculate the average for the specified columns by their indices
            averages = df.iloc[:, [4, 5, 6]].mean()

            # Append the averages and the file name (for identification) to the list
            averages_list.append({
                "File Name": os.path.basename(file_path),
                col_names[0] + " Average": averages[0],
                col_names[1] + " Average": averages[1],
                col_names[2] + " Average": averages[2]
            })
            
            # Extract Selectivity Index (Peak) values based on file name
            selectivity_index_values = df.iloc[:, 4].values
            if "Baseline" in file_path:
                selectivity_index_baseline.extend(selectivity_index_values)
            elif "Norepinephrine" in file_path:
                selectivity_index_norepinephrine.extend(selectivity_index_values)
        else:
            print(f"Warning: File '{file_path}' does not have enough columns.")

    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")

# Convert the list of averages into a DataFrame
averages_df = pd.DataFrame(averages_list)

# Define the output file path for the first CSV
output_file_path_averages = os.path.join(directory, "AveragesPerAnimal.csv")

# Save the averages DataFrame to a CSV file
averages_df.to_csv(output_file_path_averages, index=False)

print(f"Output CSV file has been saved to '{output_file_path_averages}'.")

# Prepare a DataFrame for the Selectivity Index (Peak) values
# The lengths of the two lists may differ, so we'll fill the shorter list with NaNs
max_length = max(len(selectivity_index_baseline), len(selectivity_index_norepinephrine))
selectivity_index_baseline.extend([float('nan')] * (max_length - len(selectivity_index_baseline)))
selectivity_index_norepinephrine.extend([float('nan')] * (max_length - len(selectivity_index_norepinephrine)))

selectivity_df = pd.DataFrame({
    "Baseline Selectivity Index (Peak)": selectivity_index_baseline,
    "Norepinephrine Selectivity Index (Peak)": selectivity_index_norepinephrine
})

# Define the output file path for the second CSV
output_file_path_selectivity = os.path.join(directory, "CumulativeProbability.csv")

# Save the selectivity index DataFrame to a CSV file
selectivity_df.to_csv(output_file_path_selectivity, index=False)

print(f"Output CSV file for Selectivity Index (Peak) has been saved to '{output_file_path_selectivity}'.")
