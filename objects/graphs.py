import numpy as np
import matplotlib.pyplot as plt
from utils.kde_utils import kde_function
from utils.pdp_utils import pdp_function
from utils.cdf_utils import cdf_function
from utils import measures
from sklearn.manifold import MDS as MultidimensionalScaling
from utils.graph_utils import download_graph, plot_graph, get_x_max, get_x_min
from scipy.spatial.distance import squareform, pdist


class KDE:
    def __init__(self, samples, title, stacked=False):
        self.samples = samples
        self.title = title
        self.stacked = stacked

    def __plot(self):
        samples = self.samples
        x_max = get_x_max(samples)
        x_min = get_x_min(samples)
        fig, ax = plt.subplots(figsize=(9, 6), dpi=100)
        if not self.stacked:
            for i, sample in enumerate(samples):
                header = sample.name
                x, y = kde_function(sample, x_max=x_max, x_min=x_min)
                ax.plot(x, y, label=header)
                ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        else:
            if len(samples) == 1:
                fig, ax = plt.subplots(nrows=1, figsize=(9, 6), dpi=100, squeeze=False)
                for i, sample in enumerate(samples):
                    header = sample.name
                    x, y = kde_function(sample, x_max=x_max, x_min=x_min)
                    ax[0, 0].plot(x, y, label=header)
                    ax[0, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))
            else:
                fig, ax = plt.subplots(nrows=len(samples), figsize=(9, 6), dpi=100, squeeze=False)
                for i, sample in enumerate(samples):
                    header = sample.name
                    x, y = kde_function(sample, x_max=x_max, x_min=x_min)
                    ax[i, 0].plot(x, y, label=header)
                    ax[i, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))
        fig.suptitle(self.title if not None else "Kernel Density Estimate")
        fig.text(0.5, 0.01, 'Age (Ma)', ha='center', va='center', fontsize=12)
        fig.text(0.01, 0.5, 'Probability Differential', va='center', rotation='vertical', fontsize=12)

        fig.tight_layout(rect=[0.025, 0.025, 0.975, 1])
        return fig

    def plot(self):
        fig = self.__plot()
        return plot_graph(fig)

    def download(self, file_name, file_format):
        fig = self.__plot()
        return download_graph(fig, file_name, file_format)


class CDF:
    def __init__(self, samples, title):
        self.samples = samples
        self.title = title

    def __plot(self):
        samples = self.samples
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        for sample in samples:
            header = sample.name
            bins_count, cdf_values = cdf_function(sample)
            ax.plot(bins_count[1:], cdf_values, label=header)
        ax.set_title(self.title if self.title is not None else "Cumulative Distribution Function")
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        return fig

    def plot(self):
        fig = self.__plot()
        return plot_graph(fig)

    def download(self, file_name, file_format):
        fig = self.__plot()
        return download_graph(fig, file_name, file_format)


class PDP:
    def __init__(self, samples, title, stacked=False):
        self.samples = samples
        self.title = title
        self.stacked = stacked

    def __plot(self):
        samples = self.samples
        x_max = get_x_max(samples)
        x_min = get_x_min(samples)
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        if not self.stacked:
            for i, sample in enumerate(samples):
                header = sample.name
                x, y = pdp_function(sample, x_max=x_max, x_min=x_min)
                ax.plot(x, y, label=header)
                ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        else:
            if len(samples) == 1:
                fig, ax = plt.subplots(nrows=1, figsize=(8, 6), dpi=100, squeeze=False)
                for i, sample in enumerate(samples):
                    header = sample.name
                    x, y = pdp_function(sample, x_max=x_max, x_min=x_min)
                    ax[0, 0].plot(x, y, label=header)
                    ax[0, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))
            else:
                fig, ax = plt.subplots(nrows=len(samples), figsize=(8, 6), dpi=100, squeeze=False)
                for i, sample in enumerate(samples):
                    header = sample.name
                    x, y = pdp_function(sample, x_max=x_max, x_min=x_min)
                    ax[i, 0].plot(x, y, label=header)
                    ax[i, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))
        fig.suptitle(self.title if not None else "Kernel Density Estimate")
        fig.tight_layout()
        return fig

    def plot(self):
        fig = self.__plot()
        return plot_graph(fig)

    def download(self, file_name, file_format):
        fig = self.__plot()
        return download_graph(fig, file_name, file_format)


class MDS:
    def __init__(self, samples, title=None):
        self.samples = samples
        self.title = title

    def __plot(self):
        samples = self.samples
        num_samples = len(samples)
        dissimilarity_matrix = np.zeros((num_samples, num_samples))
        sample_names = [sample.name for sample in samples]

        for i in range(num_samples):
            for j in range(i + 1, num_samples):
                dissimilarity_matrix[i, j] = measures.dissimilarity_test(samples[i], samples[j])
                dissimilarity_matrix[j, i] = dissimilarity_matrix[i, j]

        embedding = MultidimensionalScaling(n_components=2, dissimilarity='precomputed')
        scaled_mds_result = embedding.fit_transform(dissimilarity_matrix)

        viridis = plt.cm.get_cmap('gist_ncar', num_samples)
        colors = viridis(np.linspace(0, 1, num_samples))
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        for i, (x, y) in enumerate(scaled_mds_result):
            ax.scatter(x, y, color=colors[i])
            ax.text(x, y + 0.005, sample_names[i], fontsize=8, ha='center', va='center')

        for i, (x, y) in enumerate(scaled_mds_result):
            ax.text(x, y + 0.005, sample_names[i], fontsize=8, ha='center', va='center')

        for i in range(num_samples):
            distance = float('inf')  # Initialize distance to positive infinity
            nearest_sample = None

            for j in range(num_samples):
                if i != j:  # Exclude the sample itself
                    dissimilarity = measures.dissimilarity_test(samples[i], samples[j])
                    if dissimilarity < distance:
                        distance = dissimilarity
                        nearest_sample = samples[j]

            if nearest_sample is not None:
                x1, y1 = scaled_mds_result[i]
                x2, y2 = scaled_mds_result[samples.index(nearest_sample)]
                ax.plot([x1, x2], [y1, y2], 'k--', linewidth=0.5)

        stress = embedding.stress_

        fig.suptitle(self.title if self.title is not None else f"Multidimensional Scaling Plot (Stress: {np.round(stress, decimals=6)})")
        fig.text(0.5, 0.01, 'Dimension 1', ha='center', va='center', fontsize=12)
        fig.text(0.01, 0.5, 'Dimension 2', va='center', rotation='vertical', fontsize=12)
        fig.tight_layout()
        return fig

    def plot(self):
        fig = self.__plot()
        return plot_graph(fig)

    def download(self, file_name, file_format):
        fig = self.__plot()
        return download_graph(fig, file_name, file_format)
