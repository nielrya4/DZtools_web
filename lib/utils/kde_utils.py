import numpy as np
from sklearn.neighbors import KernelDensity


def kde_function(sample, num_steps=1000, x_min=0, x_max=4000):
    x = np.linspace(x_min, x_max, num_steps).reshape(-1, 1)
    ages = np.array([grain.age for grain in sample.grains]).reshape(-1, 1)
    bandwidths = np.array([np.abs(grain.uncertainty) for grain in sample.grains])

    kde = KernelDensity(bandwidth=np.mean(bandwidths), kernel='gaussian')
    kde.fit(ages)

    log_dens = kde.score_samples(x)
    y = np.exp(log_dens)

    return x.flatten(), y / np.sum(y)


def get_y_values(sample):
    y = []
    try:
        x, y = kde_function(sample)
    except ValueError as e:
        print(f"{e}")
    return y


def replace_bandwidth(all_data, bandwidth):
    for i in range(0, len(all_data)):
        for j in range(0, len(all_data[i][2])):
            all_data[i][2][j] = (bandwidth,)
    return all_data
