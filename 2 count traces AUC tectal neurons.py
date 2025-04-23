import pandas as pd
import numpy as np
import os
import glob
from scipy.integrate import trapz

def smooth_data_rowwise(data, window_size=1):
    return data.apply(lambda row: row.rolling(window=window_size, min_periods=1, center=True).mean(), axis=1)

def calculate_auc_rowwise(row):
    # Finding the lowest positive y-value in the trace
    positive_values = row[row > 0]
    baseline = positive_values.min() if not positive_values.empty else 0

    # Calculating the AUC relative to the baseline
    adjusted_trace = row - baseline
    return trapz(adjusted_trace[adjusted_trace > 0], dx=1)

def process_file(filepath):
    data = pd.read_csv(filepath, header=None)
    smoothed_data = smooth_data_rowwise(data)
    auc_values = smoothed_data.apply(calculate_auc_rowwise, axis=1)

    auc_df = pd.DataFrame({'Trace Number': range(1, len(auc_values) + 1), 'AUC': auc_values})
    auc_df.to_csv(f'{os.path.splitext(filepath)[0]}_AUC.csv', index=False)

    return len(auc_values)

def main(directory):
    files = glob.glob(os.path.join(directory, '*_normalized.csv'))
    files.sort()  # This will sort the files alphabetically
    summary = {}

    for file in files:
        n_traces = process_file(file)
        summary[os.path.basename(file)] = n_traces

    summary_df = pd.DataFrame(list(summary.items()), columns=['File', 'Number of Traces'])
    summary_df.to_csv(os.path.join(directory, 'CellCountsNeurons.csv'), index=False)

    print("Processing complete.")

if __name__ == '__main__':
    directory = '/Users/nbenfey/Desktop/PythonProcessing'
    main(directory)
