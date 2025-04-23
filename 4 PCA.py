import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Path to the directory containing your files
directory = '/Users/nbenfey/Desktop/PythonProcessing'

# Styling for plots
sns.set(style='whitegrid')
plt.rcParams['figure.figsize'] = (18, 6)

# Configurable axes limits for the plots
ORIGINAL_AXES_LIMITS = {'x': (-150, 150), 'y': (-100, 100)}
TRANSPOSED_AXES_LIMITS = {'x': (-5, 30), 'y': (-6, 12)}
TIMESERIES_AXES_LIMITS = {'x': (0, 2600), 'y': (-10, 30)}

# Configurable PCs to plot
PC_X = 1  # PC to plot on the x-axis
PC_Y = 2  # PC to plot on the y-axis

# Configurable smoothing factors
SMOOTHING_WINDOW = 1
LINE_SMOOTHING_WINDOW = 15

# Enable or disable smoothing
SMOOTHING_ENABLED = True

# Number of clusters for K-means
NUM_CLUSTERS = 5

# Number of principal components
N_COMPONENTS = 5

# Display settings for plots
SHOW_AXES = True
SHOW_LABELS = True
SHOW_TITLES = True
SHOW_GRIDLINES = True

# Stimuli onsets and window length (configurable)
STIMULI_WINDOWS = {
    "Dots": [235, 836, 1456, 2066, 2679, 3294, 3901],
    "Loom": [537, 1150, 1763, 2361, 2967, 3595, 4208]
}
WINDOW_LENGTH = 150

def smooth_data(data, window):
    return data.rolling(window=window, min_periods=1, center=True).mean()

def run_pca(data, suffix, ax, smoothing_enabled, n_components=N_COMPONENTS, window_length=WINDOW_LENGTH, stimuli_windows=STIMULI_WINDOWS, axes_limits=None, label_points=False):
    data = StandardScaler().fit_transform(data)
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(data)
    pca_df = pd.DataFrame(data=principal_components, columns=[f'PC{i+1}' for i in range(n_components)])

    if suffix.startswith('original'):
        kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=0, n_init='auto').fit(pca_df)
        pca_df['cluster'] = kmeans.labels_
        scatter = ax.scatter(pca_df[f'PC{PC_X}'], pca_df[f'PC{PC_Y}'], c=pca_df['cluster'], cmap='viridis', s=100, alpha=0.7)
        
        if label_points:
            for i, point in pca_df.iterrows():
                ax.annotate(str(i), (point[f'PC{PC_X}'], point[f'PC{PC_Y}']), textcoords="offset points", xytext=(0,10), ha='center')
        
        cbar = plt.colorbar(scatter, ax=ax, ticks=range(NUM_CLUSTERS))
        cbar.set_label('')
        cbar.ax.set_yticklabels([f'Cluster {i}' for i in range(NUM_CLUSTERS)])
        
        if SHOW_TITLES:
            ax.set_title(f'PCA of Data with K-means Clustering - {suffix}')
    else:
        if smoothing_enabled:
            pca_df = smooth_data(pca_df, LINE_SMOOTHING_WINDOW)
        ax.plot(pca_df['PC1'], pca_df['PC2'], color=(0.8, 0.8, 0.8), linestyle='-')

        for stimulus, onsets in stimuli_windows.items():
            color = (0.5, 0.5, 0.5) if stimulus == 'Dots' else (0.2, 0.2, 0.2)
            for onset in onsets:
                start, end = onset, onset + window_length
                ax.plot(pca_df.loc[start:end, 'PC1'], pca_df.loc[start:end, 'PC2'], color=color, linestyle='-')

        if SHOW_TITLES:
            ax.set_title(f'PCA of Data - {suffix}')

    if SHOW_LABELS:
        ax.set_xlabel(f'PC{PC_X}')
        ax.set_ylabel(f'PC{PC_Y}')

    if axes_limits:
        ax.set_xlim(axes_limits['x'])
        ax.set_ylim(axes_limits['y'])

    ax.axison = SHOW_AXES
    ax.grid(SHOW_GRIDLINES)

    return pca_df, pca.explained_variance_ratio_

def plot_time_series(pca_df, n_components, axes_limits=TIMESERIES_AXES_LIMITS):
    fig, axs = plt.subplots(n_components, 1, figsize=(18, 6 * n_components))
    
    for i in range(n_components):
        ax = axs[i] if n_components > 1 else axs
        if SHOW_TITLES:
            ax.set_title(f'PC{i+1} Time Series')
        pca_df[f'PC{i+1}'].plot(ax=ax)

        if SHOW_LABELS:
            ax.set_xlabel('Timepoints')
            ax.set_ylabel(f'PC{i+1} Value')

        ax.set_xlim(axes_limits['x'])
        ax.set_ylim(axes_limits['y'])
        ax.grid(SHOW_GRIDLINES)
        ax.axison = SHOW_AXES

    plt.tight_layout()
    return fig

def process_all_files(directory, start_timepoint, end_timepoint, smoothing_enabled=SMOOTHING_ENABLED, n_components=N_COMPONENTS):
    variance_original = []
    variance_transposed = []
    
    # Process files in alphabetical order
    for file in sorted(os.listdir(directory)):
        if file.endswith('_normalized.csv'):
            file_path = os.path.join(directory, file)
            data_original = pd.read_csv(file_path, header=None)

            if start_timepoint < 0 or end_timepoint > data_original.shape[1]:
                raise ValueError(f"Timepoints out of range. File has {data_original.shape[1]} timepoints.")
            data_original = data_original.iloc[:, start_timepoint:end_timepoint]

            data_smoothed = smooth_data(data_original, SMOOTHING_WINDOW) if smoothing_enabled else data_original
            data_transposed = data_original.T
            data_transposed_smoothed = smooth_data(data_transposed, SMOOTHING_WINDOW) if smoothing_enabled else data_transposed
            
            fig, axs = plt.subplots(1, 2, figsize=(18, 6))
            
            pca_df_orig, variance_orig = run_pca(data_smoothed, 'original_smoothed', axs[0], smoothing_enabled, n_components, axes_limits=ORIGINAL_AXES_LIMITS)
            pca_csv_path_orig = file_path.replace('_normalized.csv', '_pca_original.csv')
            pca_df_orig.to_csv(pca_csv_path_orig, index=False)
            variance_original.append([file.replace('_normalized.csv', ''), *variance_orig])
            
            pca_df_trans, variance_trans = run_pca(data_transposed_smoothed, 'transposed_smoothed', axs[1], smoothing_enabled, n_components, axes_limits=TRANSPOSED_AXES_LIMITS)
            pca_csv_path_trans = file_path.replace('_normalized.csv', '_pca_transposed.csv')
            pca_df_trans.to_csv(pca_csv_path_trans, index=False)
            variance_transposed.append([file.replace('_normalized.csv', ''), *variance_trans])
            
            plt.tight_layout()
            plt.savefig(file_path.replace('_normalized.csv', '_pca_analysis.png'), transparent=False, dpi=300)
            plt.close()

            time_series_fig = plot_time_series(pca_df_trans, n_components, axes_limits={'x': (start_timepoint, end_timepoint), 'y': TIMESERIES_AXES_LIMITS['y']})
            time_series_fig.savefig(file_path.replace('_normalized.csv', '_transposed_plot.png'), transparent=False, dpi=300)
            plt.close(time_series_fig)

            print(f'Processed file: {file} - PCA data saved to: {pca_csv_path_orig}, {pca_csv_path_trans}')

    pd.DataFrame(variance_original, columns=['File'] + [f'PC{i+1}' for i in range(n_components)]).to_csv(os.path.join(directory, 'PCAVariance_original.csv'), index=False)
    pd.DataFrame(variance_transposed, columns=['File'] + [f'PC{i+1}' for i in range(n_components)]).to_csv(os.path.join(directory, 'PCAVariance_transposed.csv'), index=False)

if __name__ == '__main__':
    process_all_files(directory, 0, 4500)
