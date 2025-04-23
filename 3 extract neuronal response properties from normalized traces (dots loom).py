import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps

# === Configuration Parameters ===
DATA_DIRECTORY = '/Users/nbenfey/Desktop/PythonProcessing'  # Update with your directory path
START_OFFSET = 5  # Number of frames after stimulus presentation when the window starts
END_OFFSET = 75  # Number of frames after stimulus presentation when the window ends
SMOOTHING_WINDOW = 1  # Size of the moving average window for smoothing
ANALYSIS_INTERVALS = [(0, 2600)]  # Set to a list of tuples for specific intervals

STIMULUS_POSITIONS = {
    "Dots": [235, 836, 1456, 2066, 2679, 3294, 3901],
    "Loom": [537, 1150, 1763, 2361, 2967, 3595, 4208]
}

BINS = {
    "Dots": [(0, 0.5), (0.5, 1)],
    "Loom": [(1.0, 2.0), (2.0, 4.0), (4.0, float('inf'))]
}

# === Function Definitions ===
def categorize_into_bins(selectivity_index, stimulus_type):
    for bin_range in BINS[stimulus_type]:
        if bin_range[0] <= selectivity_index < bin_range[1]:
            return bin_range
    return None

def read_csv(file_path):
    try:
        return pd.read_csv(file_path, header=None)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def smooth_signal(signal):
    return signal.rolling(window=SMOOTHING_WINDOW, min_periods=1, center=True).mean()

def calculate_area_under_curve(trace, start, end):
    adjusted_trace = trace[start:end + 1]
    return simps(adjusted_trace, dx=1)

def calculate_peak_value(trace, start, end):
    return trace[start:end + 1].max()

def process_trace(trace, is_smoothed, trace_index, analysis_intervals=None):
    if is_smoothed:
        trace = smooth_signal(trace)

    if analysis_intervals is None:
        analysis_intervals = [(0, len(trace))]

    results = {"During Stimulus": {}}
    peak_data = []

    for interval in analysis_intervals:
        start_interval, end_interval = interval
        for stimulus, times in STIMULUS_POSITIONS.items():
            stimulus_times = [time for time in times if start_interval <= time <= end_interval]
            areas_peaks = []
            for time in stimulus_times:
                start, end = max(time + START_OFFSET, 0), min(time + END_OFFSET, end_interval)
                area = calculate_area_under_curve(trace, start, end)
                peak = calculate_peak_value(trace, start, end)
                if area != 0:  # Exclude zero values
                    areas_peaks.append((area, peak))
                    peak_data.append({"Trace Index": trace_index, "Time": time, "Peak Value": peak, "Stimulus": stimulus})
            results["During Stimulus"][stimulus] = areas_peaks

    avg_peak_loom = np.mean([peak for _, peak in results["During Stimulus"]["Loom"] if peak != 0])
    avg_peak_dots = np.mean([peak for _, peak in results["During Stimulus"]["Dots"] if peak != 0])
    peak_ssi = avg_peak_loom / avg_peak_dots if avg_peak_dots != 0 else float('inf')

    return results, peak_data, avg_peak_loom, avg_peak_dots, peak_ssi

def plot_traces(data, file_name, smoothed=True):

    # Adjust the figsize to ensure smaller images, and optionally adjust dpi for lower resolution
    fig, axes = plt.subplots(len(data), 1, figsize=(10, 3 * len(data)))  # Reduced figure size
    axes = axes if len(data) > 1 else [axes]

    for idx, trace in enumerate(data.values):
        original_trace = pd.Series(trace)
        trace_to_plot = smooth_signal(original_trace) if smoothed else original_trace
        label = 'Smoothed Trace' if smoothed else 'Original Trace'

        axes[idx].plot(trace_to_plot, label=label, color='green' if smoothed else 'blue', alpha=0.5)

        for interval in ANALYSIS_INTERVALS:
            start_interval, end_interval = interval
            for stimulus, times in STIMULUS_POSITIONS.items():
                color = 'orange' if stimulus == 'Loom' else 'blue'
                for time in times:
                    if start_interval <= time <= end_interval:
                        start, end = max(time + START_OFFSET, 0), min(time + END_OFFSET, end_interval)
                        area_trace = trace_to_plot[start:end + 1]
                        axes[idx].fill_between(range(start, end + 1), area_trace, 0, color=color, alpha=0.3, interpolate=True)
                        axes[idx].axvline(x=time, color=color, linestyle='--', label=f'{stimulus} Stimulus Onset' if time == times[0] else "")
                        peak = calculate_peak_value(trace_to_plot, start, end)
                        peak_time = trace_to_plot[start:end + 1].idxmax()
                        axes[idx].plot(peak_time, peak, 'ro')  # Red dot for peak

        axes[idx].set_xlim(0, len(trace))
        axes[idx].set_title(f'Trace {idx + 1}')
        axes[idx].set_xlabel('Time')
        axes[idx].set_ylabel('Signal Amplitude')
        axes[idx].legend()

    plt.tight_layout()
    if smoothed:  # Save only if smoothed is True
        plt.savefig(file_name.replace('.csv', '_smoothed_processed_traces.png'), dpi=150)  # Adjusted DPI
    plt.close()

def process_all_files(directory):
    all_files_bin_counts = []
    all_files_peak_bin_counts = []

    # Sort the files alphabetically
    sorted_files = sorted(os.listdir(directory))

    for file in sorted_files:
        if file.endswith('_normalized.csv'):
            file_path = os.path.join(directory, file)
            data = read_csv(file_path)
            if data is None:
                continue

            rows_for_csv = []
            bin_counts = {stimulus: {bin_range: 0 for bin_range in BINS[stimulus]} for stimulus in BINS}
            peak_bin_counts = {stimulus: {bin_range: 0 for bin_range in BINS[stimulus]} for stimulus in BINS}
            raw_data = []  # Reset for each file

            for idx, trace in enumerate(data.values):
                areas, peak_data, avg_peak_loom, avg_peak_dots, peak_ssi = process_trace(pd.Series(trace), True, idx, ANALYSIS_INTERVALS)

                trace_avg_areas = {}
                selectivity_index = 0
                avg_area_loom = 0
                avg_area_dots = 0

                for condition, condition_areas in areas.items():
                    for stimulus_type in condition_areas:
                        avg_area = np.mean([area for area, _ in condition_areas[stimulus_type]])
                        trace_avg_areas[f'Avg Area {condition} {stimulus_type}'] = avg_area

                        for area, peak in condition_areas[stimulus_type]:
                            raw_data.append({
                                'Trace Index': idx,
                                'Stimulus': stimulus_type,
                                'Area Under Curve': area,
                                'Peak Value': peak
                            })

                        if condition == 'During Stimulus':
                            if stimulus_type == 'Loom':
                                avg_area_loom = avg_area
                            elif stimulus_type == 'Dots':
                                avg_area_dots = avg_area

                if avg_area_dots != 0:
                    selectivity_index = avg_area_loom / avg_area_dots
                trace_avg_areas['Selectivity Index (AUC)'] = selectivity_index
                trace_avg_areas['Selectivity Index (Peak)'] = peak_ssi

                bin_key = categorize_into_bins(selectivity_index, 'Loom' if avg_area_loom > avg_area_dots else 'Dots')
                peak_bin_key = categorize_into_bins(peak_ssi, 'Loom' if avg_peak_loom > avg_peak_dots else 'Dots')

                if bin_key:
                    bin_counts['Loom' if avg_area_loom > avg_area_dots else 'Dots'][bin_key] += 1
                if peak_bin_key:
                    peak_bin_counts['Loom' if avg_peak_loom > avg_peak_dots else 'Dots'][peak_bin_key] += 1

                rows_for_csv.append({
                    'Trace Index': idx, 
                    **trace_avg_areas, 
                    'Avg Peak Loom': avg_peak_loom, 
                    'Avg Peak Dots': avg_peak_dots
                })

            pd.DataFrame(rows_for_csv).to_csv(f'{os.path.splitext(file)[0]}_average_neuronal_properties.csv', index=False)

            # Save AUC data to CSV file for each input file
            pd.DataFrame(raw_data).to_csv(f'{os.path.splitext(file)[0]}_raw_neuronal_properties.csv', index=False)

            all_files_bin_counts.extend([{
                'File': file,
                'Data Type': 'Smoothed',
                'Stimulus': stimulus_type,
                'Bin Range': bin_range[0],
                'Count': count
            } for stimulus_type, bin_counts in bin_counts.items() for bin_range, count in bin_counts.items()])

            all_files_peak_bin_counts.extend([{
                'File': file,
                'Data Type': 'Smoothed',
                'Stimulus': stimulus_type,
                'Bin Range': bin_range[0],
                'Count': count
            } for stimulus_type, bin_counts in peak_bin_counts.items() for bin_range, count in bin_counts.items()])

            # Plot the traces
            plot_traces(data, file, smoothed=True)
            plot_traces(data, file, smoothed=False)

    # Save cumulative bin counts for both AUC-based and peak-based SSI
    pd.DataFrame(all_files_bin_counts).to_csv(os.path.join(directory, 'auc_bin_counts.csv'), index=False)
    pd.DataFrame(all_files_peak_bin_counts).to_csv(os.path.join(directory, 'peak_bin_counts.csv'), index=False)

if __name__ == "__main__":
    process_all_files(DATA_DIRECTORY)
