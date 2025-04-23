import os
import pandas as pd
import numpy as np
import glob

# Parameters for data processing
default_window_size = 4500
quartile_for_baseline = 0.1

def read_csv_files(directory):
    """Reads all CSV files in the specified directory.
    Selects only y columns and excludes the rightmost y column if there are 6 or more y columns."""
    file_paths = glob.glob(os.path.join(directory, '*.csv'))
    file_paths.sort()  # Sort the file paths alphabetically
    data = []
    for file in file_paths:
        df = pd.read_csv(file, header=0)
        y_data_columns = [col for col in df.columns if col.startswith('y')]
        # Exclude the last 'y' column only if there are 6 or more y columns
        if len(y_data_columns) >= 6:
            df = df[y_data_columns[:-1]]
        else:
            df = df[y_data_columns]
        data.append(df)
    return data, file_paths

def apply_scaling_factor(data):
    """Applies a scaling factor to the data columns."""
    num_y_data_columns = data.shape[1]
    for i, column in enumerate(data.columns):
        scaling_factor = (num_y_data_columns - (i + 1)) * 0.5
        data[column] -= scaling_factor
    return data

def sliding_window_baseline(data, window_size=default_window_size):
    """Calculates the baseline using a sliding window approach with edge case handling."""
    baseline = pd.DataFrame(index=data.index)
    for column in data:
        col_data = data[column]
        baseline[col_data.name] = col_data.rolling(window=window_size, min_periods=1, center=True).quantile(quartile_for_baseline)
        # Handle edge cases for the beginning of the data
        baseline.iloc[:window_size // 2, baseline.columns.get_loc(col_data.name)] = baseline.iloc[window_size // 2, baseline.columns.get_loc(col_data.name)]
    return baseline

def normalize_data(data, baseline):
    """Normalizes the data to the baseline values (DeltaF/F)."""
    normalized_data = (data - baseline) / (baseline + 10)
    # Handle edge cases for normalization
    normalized_data.replace([np.inf, -np.inf], np.nan, inplace=True)
    normalized_data.fillna(0, inplace=True)
    return normalized_data

def transpose_and_save_data(data, file_paths):
    """Transposes and saves the processed data to new CSV files without headers."""
    for df, path in zip(data, file_paths):
        transposed_df = df.transpose()
        new_filename = os.path.splitext(path)[0] + '_normalized.csv'
        transposed_df.to_csv(new_filename, index=False, header=False)

def process_fluorescence_data(directory):
    """Main function to process fluorescence data from CSV files."""
    try:
        data, file_paths = read_csv_files(directory)  # Read CSV files
        processed_data = []
        for df in data:
            scaled_data = apply_scaling_factor(df)
            baseline = sliding_window_baseline(scaled_data)
            normalized_data = normalize_data(scaled_data, baseline)
            processed_data.append(normalized_data)
        transpose_and_save_data(processed_data, file_paths)
        print('Data processing complete. Files saved.')
    except Exception as e:
        print(f'Error occurred: {e}')

if __name__ == '__main__':
    directory = '/Users/nbenfey/Desktop/PythonProcessing'
    process_fluorescence_data(directory)
