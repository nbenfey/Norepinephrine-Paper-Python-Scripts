import pandas as pd
import numpy as np
import os
import csv

# Define the path to the directory containing the files
path = '/Users/nbenfey/Desktop/PythonProcessing'

# Bins for grouping values
bins = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, np.inf]
bin_labels = ["'0-1'", "'1-2'", "'2-3'", "'3-4'", "'4-5'", "'5-6'", "'6-7'", "'7-8'", "'8-9'", "'9-10'", "'10+'"]

# Prepare the results file, adjust the path to your preferred location
output_filename = '/Users/nbenfey/Desktop/PythonProcessing/ResponseAmplitudesNeurons.csv'
with open(output_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Filename', 'Stimulus', 'Bin', 'Count'])

    # Get all files that end with 'average_neuronal_properties.csv' and sort them alphabetically
    filenames = sorted([f for f in os.listdir(path) if f.endswith('average_neuronal_properties.csv')])

    # Process each file in alphabetical order
    for filename in filenames:
        full_path = os.path.join(path, filename)
        df = pd.read_csv(full_path)

        for column in ['Avg Peak Loom', 'Avg Peak Dots']:
            # Count values in each bin
            counts = pd.cut(df[column], bins=bins, labels=bin_labels, right=False).value_counts().sort_index()

            # Write results to the CSV
            for bin_label, count in counts.items():
                writer.writerow([filename, column, bin_label, count])

print(f"Processing complete. Results are saved in {output_filename}")
