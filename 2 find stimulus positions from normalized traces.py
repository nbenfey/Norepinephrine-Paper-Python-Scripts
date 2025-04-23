import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, argrelextrema

# === Configuration Parameters ===
DATA_DIRECTORY = '/Users/nbenfey/Desktop/PythonProcessing'  # Update with your directory path
NUMBER_OF_STIMULI = 14  # Total number of stimuli presented
INTER_STIMULUS_INTERVAL = 290  # Fixed distance between stimuli in data points
SMOOTHING_WINDOW = 15  # Size of the moving average window for smoothing
PEAKS_START_WINDOW = 200  # Timepoints to skip at the start for peak detection

def read_csv(file_path):
    """Reads a CSV file and returns its data."""
    try:
        return pd.read_csv(file_path, header=None)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def smooth_signal(signal):
    """Smooths the signal using a rolling window."""
    return signal.rolling(window=SMOOTHING_WINDOW, min_periods=1, center=True).mean()

def find_stimulus_peaks_and_onsets(signal, num_stimuli, isi):
    """Find the top N stimulus peaks and their onsets by looking for local minima."""
    # Ignore the first PEAKS_START_WINDOW timepoints for peak detection
    signal_to_search = signal[PEAKS_START_WINDOW:]
    peaks, _ = find_peaks(signal_to_search, distance=isi)
    peaks += PEAKS_START_WINDOW  # Adjust peak indices due to offset

    if len(peaks) < num_stimuli:
        return [], []
    
    sorted_peaks = sorted(peaks[np.argsort(signal_to_search[peaks])[-num_stimuli:]])
    onsets = []
    for peak in sorted_peaks:
        # Look for local minima in the vicinity before the peak
        search_region = signal[max(0, peak - isi):peak]
        local_minima_indices = argrelextrema(search_region.values, np.less)[0]
        if len(local_minima_indices) > 0:
            # The last local minimum before the peak could be the onset
            onset = local_minima_indices[-1] + max(0, peak - isi)
        else:
            # If no local minima are found, default to the peak itself
            onset = peak
        onsets.append(onset)
    
    return sorted_peaks, onsets

def visualize_traces(data, stimulus_peaks, stimulus_onsets, file_name):
    """Visualizes all traces, peaks, and onsets in subplots, splitting into multiple figures if necessary."""
    num_traces = len(data)
    max_traces_per_fig = 10  # Set a limit for traces per figure
    num_figs = (num_traces - 1) // max_traces_per_fig + 1  # Calculate the number of figures needed
    
    for fig_idx in range(num_figs):
        start_idx = fig_idx * max_traces_per_fig
        end_idx = min(start_idx + max_traces_per_fig, num_traces)
        fig, axes = plt.subplots(end_idx - start_idx, 1, figsize=(12, 6 * (end_idx - start_idx)))
        if end_idx - start_idx == 1:
            axes = [axes]
        for idx, ax in enumerate(axes, start=start_idx):
            signal = data.values[idx]
            peaks = stimulus_peaks.get(idx, [])
            onsets = stimulus_onsets.get(idx, [])
            ax.plot(signal, label=f'Trace {idx}')
            ax.plot(peaks, signal[peaks], "x", label='Detected Peaks')
            for onset in onsets:
                ax.axvline(x=onset, color='g', linestyle='--', label='Onset' if onset == onsets[0] else None)
            ax.set_title(f'Trace {idx}')
            ax.set_xlabel('Time Points')
            ax.set_ylabel('Signal Amplitude')
            ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(DATA_DIRECTORY, f'{os.path.splitext(file_name)[0]}_visualization_{fig_idx}.png'))
        plt.close()

def process_file(file_path):
    """Processes a single file to find stimulus peaks, onsets, visualizes the traces, and saves them to CSV files."""
    data = read_csv(file_path)
    stimulus_peaks = {}
    stimulus_onsets = {}
    if data is not None:
        for idx, row in data.iterrows():
            signal = smooth_signal(row)
            peaks, onsets = find_stimulus_peaks_and_onsets(signal, NUMBER_OF_STIMULI, INTER_STIMULUS_INTERVAL)
            stimulus_peaks[idx] = peaks
            stimulus_onsets[idx] = onsets
        visualize_traces(data, stimulus_peaks, stimulus_onsets, os.path.basename(file_path))
        
        # Save onsets to CSV
        onsets_df = pd.DataFrame.from_dict(stimulus_onsets, orient='index')
        onsets_df.to_csv(os.path.join(DATA_DIRECTORY, f'{os.path.splitext(file_path)[0]}_stimulus_onsets.csv'))
        
        # Save peaks to CSV
        peaks_df = pd.DataFrame.from_dict(stimulus_peaks, orient='index')
        peaks_df.to_csv(os.path.join(DATA_DIRECTORY, f'{os.path.splitext(file_path)[0]}_stimulus_peaks.csv'))

def process_all_files(directory):
    """Processes all files in the given directory that end with '_normalized.csv', in alphabetical order."""
    files = sorted([file for file in os.listdir(directory) if file.endswith('_normalized.csv')])
    
    for file in files:
        file_path = os.path.join(directory, file)
        process_file(file_path)

if __name__ == "__main__":
    process_all_files(DATA_DIRECTORY)
