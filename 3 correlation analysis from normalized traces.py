import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Configuration Parameters
NUMBER_OF_CLUSTERS = 1  # Easily configurable number of clusters
SMOOTHING_WINDOW = 1
ENABLE_SMOOTHING = True  # Toggle for smoothing
COLOURMAP = 'inferno'  # Configurable colourmap for the plots
CENTRE_RANGE = 0.4  # Centre of the colour range for the heatmap

def load_and_smooth_data(folder_path):
    data_dict = {}
    # Sort the file names alphabetically before processing
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith("_normalized.csv"):
            file_path = os.path.join(folder_path, file_name)
            data = pd.read_csv(file_path, header=None)
            if ENABLE_SMOOTHING:
                data = data.rolling(window=SMOOTHING_WINDOW, min_periods=1, axis=1).mean()
            data_dict[file_name] = data
    return data_dict

def calculate_neuron_correlations_and_visualize(data_dict, output_folder):
    average_correlations = {}
    correlation_matrices = {}
    cluster_labels_dict = {}

    for file_name, data in data_dict.items():
        corr_matrix_df = data.T.corr()
        avg_corr = corr_matrix_df.values[np.triu_indices_from(corr_matrix_df, 1)].mean()
        average_correlations[file_name] = avg_corr
        correlation_matrices[file_name] = corr_matrix_df

        kmeans = KMeans(n_clusters=NUMBER_OF_CLUSTERS, n_init=10, random_state=0)
        cluster_labels = kmeans.fit_predict(corr_matrix_df)
        cluster_labels_dict[file_name] = cluster_labels

        sorted_indices = np.argsort(cluster_labels)
        sorted_corr_matrix = corr_matrix_df.iloc[sorted_indices, sorted_indices]

        plt.figure(figsize=(10, 8))
        sns.heatmap(sorted_corr_matrix, annot=False, cmap=COLOURMAP, center=CENTRE_RANGE, vmin=0, vmax=1)
        plt.title(f"Sorted Neuron-to-Neuron Correlation for {file_name}")
        sorted_heatmap_path = os.path.join(output_folder, f"{file_name}_neuron_corr_heatmap_sorted.png")
        plt.savefig(sorted_heatmap_path, dpi=300)
        plt.close()

        # Save sorted matrix as CSV
        sorted_csv_path = os.path.join(output_folder, f"{file_name}_neuron_corr_sorted.csv")
        sorted_corr_matrix.to_csv(sorted_csv_path, index=False)

    return average_correlations, correlation_matrices, cluster_labels_dict

def save_average_correlations_and_clusters(average_correlations, correlation_matrices, clustered_data, output_folder):
    average_correlations_df = pd.DataFrame(list(average_correlations.items()), columns=['File', 'Average_Correlation'])
    csv_output_path = os.path.join(output_folder, 'average_correlations.csv')
    average_correlations_df.to_csv(csv_output_path, index=False)

    for file_name, cluster_labels in clustered_data.items():
        cluster_output_path = os.path.join(output_folder, f"{file_name}_clusters.csv")
        cluster_df = pd.DataFrame({'Neuron': range(1, len(cluster_labels) + 1), 'Cluster': cluster_labels})
        cluster_df.to_csv(cluster_output_path, index=False)

        corr_matrix = correlation_matrices[file_name]
        cluster_avg_corr = {}
        cluster_counts = {}
        for cluster in np.unique(cluster_labels):
            cluster_indices = np.where(cluster_labels == cluster)[0]
            cluster_matrix = corr_matrix.iloc[cluster_indices, cluster_indices]
            cluster_avg_corr[cluster] = cluster_matrix.values[np.triu_indices(len(cluster_indices), 1)].mean()
            cluster_counts[cluster] = len(cluster_indices)

        cluster_avg_corr_df = pd.DataFrame(list(cluster_avg_corr.items()), columns=['Cluster', 'Average_Correlation'])
        cluster_avg_corr_df['Number_of_Neurons'] = cluster_avg_corr_df['Cluster'].map(cluster_counts)
        cluster_avg_corr_output_path = os.path.join(output_folder, f"{file_name}_cluster_avg_correlations.csv")
        cluster_avg_corr_df.to_csv(cluster_avg_corr_output_path, index=False)

def main():
    folder_path = '/Users/nbenfey/Desktop/PythonProcessing'
    output_folder = os.path.join(folder_path, 'CorrelationsNeurons')
    os.makedirs(output_folder, exist_ok=True)

    data_dict = load_and_smooth_data(folder_path)
    average_correlations, correlation_matrices, clustered_data = calculate_neuron_correlations_and_visualize(data_dict, output_folder)
    save_average_correlations_and_clusters(average_correlations, correlation_matrices, clustered_data, output_folder)

    print(f"Average correlations and clusters saved to: {output_folder}")

if __name__ == "__main__":
    main()
