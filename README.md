Plaintext
# Calcium Imaging and Behavioral Analysis Pipeline

## Description
This repository contains a suite of Python scripts for processing and analyzing calcium imaging and behavioral data. The pipeline is designed to take raw fluorescence traces and video files as input and perform a series of analyses including normalization, event detection, feature extraction, correlation analysis, and behavioral tracking. The scripts are structured to process data related to neuronal, glial, and behavioral responses to visual stimuli.

## Table of Contents
- [Dependencies](#dependencies)
- [Input Data Format](#input-data-format)
- [Analysis Pipeline Workflow](#analysis-pipeline-workflow)
  - [Step 1: Normalization](#step-1-normalization)
  - [Step 2: Post-Normalization Processing](#step-2-post-normalization-processing)
  - [Step 3: Advanced Calcium Imaging Analysis](#step-3-advanced-calcium-imaging-analysis)
  - [Step 4: Post-Analysis and Grouping](#step-4-post-analysis-and-grouping)
- [Additional Scripts](#additional-scripts)
  - [Behavioral Tracking](#behavioral-tracking)
  - [Stimulus Presentation](#stimulus-presentation)
- [Script Descriptions](#script-descriptions)
- [Output Files](#output-files)

## Dependencies
These scripts are written in Python and require the following libraries. You can install them using `pip`:

pip install pandas numpy matplotlib scipy scikit-learn seaborn pygame psychopy opencv-python imutils

You may also need to install `tkinter`, which typically comes with Python but may require a separate installation on some systems (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu).

## Input Data Format
* **Calcium Imaging**: The primary input for the imaging pipeline is CSV files containing fluorescence data.
    * Each CSV file should represent a single recording session.
    * The file must contain columns with headers starting with 'y' (e.g., 'y1', 'y2', ...), where each column represents the fluorescence trace of a single cell.
    * The scripts require data files to be located in a specific directory. This is defined by the `directory` or `DATA_DIRECTORY` variable in each script, with a default path of `/Users/nbenfey/Desktop/PythonProcessing`.

* **Behavioral Tracking**: The `working-tadpole-tracker.py` script requires an `.avi` video file and a corresponding `_timings.csv` file containing stimulus timing information.

## Analysis Pipeline Workflow
The scripts for calcium imaging analysis are designed to be run sequentially. Ensure the output files from one step are available before proceeding to the next.

### Step 1: Normalization
This initial step processes the raw fluorescence data. Choose the script based on the cell type being analyzed.

1.  **For Neuronal Data**: Run `1 normalize neurons.py`. This script reads raw CSV files, applies a sliding window baseline correction (window size: 1500), and calculates the normalized fluorescence (ΔF/F). Output files are saved with a `_normalized.csv` suffix.

2.  **For Glial Data**: Run `1 normalize glia.py`. This script performs a similar normalization process but uses a larger window size (4500) appropriate for the slower dynamics of glia. Output files are also saved with a `_normalized.csv` suffix.

### Step 2: Post-Normalization Processing
After generating `_normalized.csv` files, the following scripts can be run in any order.

* **Generate Heatmaps**:
    * `2 heatmaps of normalized traces neurons.py`
    * `2 heatmaps of normalized traces glia.py`
    * These scripts create SVG heatmap images from the normalized data for visual inspection of cellular activity.

* **Count Traces and Calculate AUC**:
    * `2 count traces AUC neurons.py`
    * `2 count traces AUC glia.py`
    * These scripts calculate the Area Under the Curve (AUC) for each trace, save it to an `_AUC.csv` file, and generate a summary count of traces (`CellCountsNeurons.csv` or `CellCountsGlia.csv`).

* **Identify Stimulus Positions**:
    * `2 find stimulus positions from normalized traces.py`. This script detects and saves the onsets and peaks of stimulus responses from the normalized traces into separate CSV files.

### Step 3: Advanced Calcium Imaging Analysis
These scripts perform more detailed analyses on the normalized data.

* **Extract Neuronal Response Properties**:
    * `3 extract neuronal response properties from normalized traces (dots loom).py`. This script calculates response characteristics (e.g., AUC, peak response) for each neuron in response to "Dots" and "Loom" stimuli. It computes a selectivity index and bins cells based on their response preference. It also generates plots of the processed traces with response windows highlighted.

* **Correlation Analysis**:
    * `3 correlation analysis from normalized traces.py`. This script calculates the neuron-to-neuron correlation matrix for each recording, performs k-means clustering, and saves the sorted correlation matrices as heatmaps and CSV files.

### Step 4: Post-Analysis and Grouping
These scripts aggregate and further process the results from the previous steps.

* **Principal Component Analysis (PCA)**:
    * `4 PCA.py`. This script performs PCA on the normalized data to identify dominant patterns of population activity and saves the results as plots and CSV files.

* **Generate Histograms of Response Amplitudes**:
    * `4 generate histograms of neuronal response amplitudes.py`. This script uses the `_average_neuronal_properties.csv` files to create histograms of peak response amplitudes for "Loom" and "Dots" stimuli.

* **Group Average Neuronal Properties**:
    * `4 group average neuronal properties by animal.py` (for norepinephrine experiments).
    * `4 group average neuronal properties by animal(5-HT).py` (for serotonin experiments).
    * These scripts aggregate the `_average_neuronal_properties.csv` files to calculate average metrics per animal and compile selectivity index data for comparing experimental conditions.

* **Sort Traces by Neuronal Properties**:
    * `4 sort normalized traces by average neuronal properties.py`. This script reorders the `_normalized.csv` files based on a selected response metric (e.g., 'Selectivity Index (Peak)', 'Avg Peak Loom') from the analysis files.

## Additional Scripts

### Behavioral Tracking
* **`working-tadpole-tracker.py`**: This script uses OpenCV to track the movement of a tadpole from a video file, analyzing its escape response to a stimulus. It calculates metrics such as escape distance, velocity, and angle.

### Stimulus Presentation
These scripts use the Pygame library to display visual stimuli.

* **`dots loom stimulus.py`**: Presents alternating sequences of moving dots and a looming circle.
* **`dots dots stimulus.py`**: Presents alternating sequences of randomly moving dots and coherently moving dots.

## Script Descriptions
| Filename | Description |
|---|---|
| `1 normalize neurons.py` | Normalizes raw fluorescence traces for neurons using a sliding window baseline correction. |
| `1 normalize glia.py` | Normalizes raw fluorescence traces for glia using a larger sliding window for baseline correction. |
| `2 heatmaps of normalized traces neurons.py` | Generates SVG heatmaps from normalized neuronal traces. |
| `2 heatmaps of normalized traces glia.py` | Generates SVG heatmaps from normalized glial traces. |
| `2 count traces AUC neurons.py` | Counts neuronal traces and calculates the Area Under the Curve (AUC) for each. |
| `2 count traces AUC glia.py` | Counts glial traces and calculates the AUC for each. |
| `2 find stimulus positions from normalized traces.py` | Detects and saves the timing of stimulus onsets and peaks from normalized traces. |
| `3 extract neuronal response properties from normalized traces (dots loom).py` | Extracts, analyzes, and plots neuronal responses to "Dots" and "Loom" stimuli. |
| `3 correlation analysis from normalized traces.py` | Performs neuron-to-neuron correlation analysis and k-means clustering on normalized traces. |
| `4 PCA.py` | Performs Principal Component Analysis (PCA) on normalized traces to identify population activity patterns. |
| `4 generate histograms of neuronal response amplitudes.py` | Generates histograms of peak neuronal response amplitudes from processed data files. |
| `4 group average neuronal properties by animal.py` | Groups average neuronal properties by animal for norepinephrine experiments. |
| `4 group average neuronal properties by animal(5-HT).py` | Groups average neuronal properties by animal for serotonin experiments. |
| `4 sort normalized traces by average neuronal properties.py` | Sorts normalized traces based on calculated neuronal response properties. |
| `working-tadpole-tracker.py` | Tracks tadpole movement from video files to analyze escape responses. |
| `dots loom stimulus.py` | A Pygame script to present moving dots and looming circle stimuli. |
| `dots dots stimulus.py` | A Pygame script to present random and coherent dot motion stimuli. |

## Output Files
This pipeline generates numerous output files, saved either in the main processing directory or in specified subdirectories (`CorrelationsNeurons`, `output_videos`, etc.).

* **`*_normalized.csv`**: Normalized fluorescence data for each input file.
* **`*_heatmap.svg`**: Heatmap visualizations of cellular activity.
* **`*_AUC.csv`**: Area Under the Curve for each cell trace.
* **`CellCountsNeurons.csv` / `CellCountsGlia.csv`**: Summary of cell counts in each processed file.
* **`*_stimulus_onsets.csv` / `*_stimulus_peaks.csv`**: Detected start times and peak times of stimuli for each trace.
* **`*_average_neuronal_properties.csv`**: Average response properties (AUC, peak) for each neuron.
* **`*_raw_neuronal_properties.csv`**: Raw response properties for each individual stimulus presentation.
* **`auc_bin_counts.csv` / `peak_bin_counts.csv`**: Counts of cells categorized into different selectivity bins.
* **`/CorrelationsNeurons/*_neuron_corr_heatmap_sorted.png`**: Heatmaps of sorted neuron-to-neuron correlation matrices.
* **`*_pca_original.csv` / `*_pca_transposed.csv`**: Data from Principal Component Analysis.
* **`PCAVariance_original.csv` / `PCAVariance_transposed.csv`**: Explained variance for each principal component.
* **`ResponseAmplitudesNeurons.csv`**: Binned counts of neuronal response amplitudes.
* **`AveragesPerAnimal.csv`**: Averaged response properties for each recording file.
* **`CumulativeProbability.csv`**: Compilation of selectivity index values for comparing experimental conditions.
* **`*_sorted_by_*.csv`**: Normalized data sorted by a specific neuronal response property.
* **`output_videos/*_tracked.avi`**: Tracked video output from the tadpole tracker.
* **`output_contrails/*.jpg`**: Image of the tadpole's path during the stimulus.
* **`data.csv`**: Saved behavioral data from the tadpole tracker.
* **`output_speed/*.csv`**: Instantaneous speed data from the tadpole tracker.


![image](https://github.com/user-attachments/assets/bddc01b0-adae-43a2-a970-9e1f05de0d51)
