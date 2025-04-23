import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# Configuration
directory = '/Users/nbenfey/Desktop/PythonProcessing'
smoothing_enabled = False  # Toggle smoothing on or off
smoothing_window_size = 1
heatmap_colormap = 'inferno'  # Default colormap for the heatmap
high_resolution_dpi = 300  # High DPI for publication quality
show_colorbar = False  # Toggle to show/hide colorbar
row_height_inches = 0.1  # Height of each row in inches
BOTTOM = 0
TOP = 0.05

# Timepoint range to plot
start_timepoint = 0
end_timepoint = 4500  # Adjust this value as needed

# Function to smooth the traces
def smooth_trace(data, window_size):
    return data.rolling(window=window_size, min_periods=1, center=True).mean()

# Function to optionally smooth the traces
def process_data(data, smoothing_enabled, window_size):
    if smoothing_enabled:
        return data.apply(lambda row: smooth_trace(row, window_size), axis=1)
    else:
        return data

# Sort and loop over each CSV file in the directory alphabetically
for filepath in sorted(glob.glob(os.path.join(directory, '*_normalized.csv'))):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filepath, header=None)

    # Select the range of timepoints
    df = df.iloc[:, start_timepoint:end_timepoint]

    # Apply optional smoothing to each row (neuron trace)
    df_processed = process_data(df, smoothing_enabled, smoothing_window_size)

    # Determine figure height based on number of rows
    fig_height = df_processed.shape[0] * row_height_inches
    fig_width = 10  # Keep the width constant or adjust as needed

    # Create the heatmap with dynamic figure size
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    cax = ax.imshow(df_processed, aspect='auto', cmap=heatmap_colormap, vmin=BOTTOM, vmax=TOP)

    # Hide x and y axis labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Hide x and y tick marks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add a colorbar if enabled
    if show_colorbar:
        fig.colorbar(cax)

    # Save the heatmap to file
    output_filename_heatmap = os.path.basename(filepath).replace('.csv', '_heatmap.svg')
    output_filepath_heatmap = os.path.join(directory, output_filename_heatmap)
    fig.savefig(output_filepath_heatmap, dpi=high_resolution_dpi, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)

print("Heatmaps have been generated and saved to", directory)
