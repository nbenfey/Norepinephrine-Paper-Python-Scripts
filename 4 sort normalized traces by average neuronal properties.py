import pandas as pd
import os

# Define the directory containing the files
directory = "/Users/nbenfey/Desktop/PythonProcessing"

# Define the sorting columns options
sort_options = {
    '1': 'Selectivity Index (Peak)',
    '2': 'Avg Peak Loom',
    '3': 'Avg Peak Dots'
}

# Set your sorting option here: '1' for Selectivity Index (Peak), '2' for Avg Peak Loom, '3' for Avg Peak Dots
sort_option = '3'

# Function to sort and save the normalized data based on the specified column in the smoothed file
def sort_and_save(normalized_file, smoothed_file, column):
    # Load the normalized data
    normalized_data = pd.read_csv(normalized_file, header=None)
    
    # Load the smoothed data
    smoothed_data = pd.read_csv(smoothed_file)
    
    # Get the sort column index
    sort_column_index = smoothed_data.columns.get_loc(column)
    
    # Sort the normalized data based on the smoothed data column
    sorted_data = normalized_data.iloc[smoothed_data.iloc[:, sort_column_index].argsort()[::-1]]
    
    # Save the sorted normalized data
    sorted_filename = normalized_file.replace("_normalized.csv", f"_sorted_by_{column.replace(' ', '_')}.csv")
    sorted_data.to_csv(sorted_filename, index=False, header=False)
    print(f"Sorted file saved as: {sorted_filename}")

# List all csv files in the directory
files = os.listdir(directory)

# Process each pair of files
for file in files:
    if file.endswith('_normalized.csv'):
        base_name = file.replace('_normalized.csv', '')
        smoothed_file = f"{base_name}_normalized_smoothed.csv"

        normalized_file_path = os.path.join(directory, file)
        smoothed_file_path = os.path.join(directory, smoothed_file)
        
        if smoothed_file in files:
            print(f"Processing: {normalized_file_path} and {smoothed_file_path}")
            
            # Check if the selected sort option is valid
            try:
                # Proceed with sorting if the column is in the smoothed file
                sort_and_save(normalized_file_path, smoothed_file_path, sort_options[sort_option])
            except KeyError:
                print(f"Column for sorting not found in {smoothed_file_path}.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print(f"No matching smoothed file found for {file}")
