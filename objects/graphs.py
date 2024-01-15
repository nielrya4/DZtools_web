import numpy as np
import matplotlib.pyplot as plt
from utils.kde_utils import kde_function
from utils.pdp_utils import pdp_function
from utils.graph_utils import download_graph, plot_graph, get_x_max, get_x_min


class KDE:
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
                x, y = kde_function(sample, x_max=x_max, x_min=x_min)
                ax.plot(x, y, label=header)
                ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        else:
            if len(samples) == 1:
                fig, ax = plt.subplots(nrows=1, figsize=(8, 6), dpi=100, squeeze=False)
                for i, sample in enumerate(samples):
                    header = sample.name
                    x, y = kde_function(sample, x_max=x_max, x_min=x_min)
                    ax[0, 0].plot(x, y, label=header)
                    ax[0, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))
            else:
                fig, ax = plt.subplots(nrows=len(samples), figsize=(8, 6), dpi=100, squeeze=False)
                for i, sample in enumerate(samples):
                    header = sample.name
                    x, y = kde_function(sample, x_max=x_max, x_min=x_min)
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


class CDF:
    def __init__(self, samples, title):
        self.samples = samples
        self.title = title

    def __plot(self):
        samples = self.samples
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        for sample in samples:
            header = sample.name
            ages = [grain.age for grain in sample.grains]
            count, bins_count = np.histogram(ages, bins=1000, density=True)
            pdf = count / sum(count)
            cdf_values = np.cumsum(pdf)
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

