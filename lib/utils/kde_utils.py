import numpy as np
from sklearn.neighbors import KernelDensity


def kde_function(sample, num_steps=1000, x_min=0, x_max=4000):
    grains = sample.grains

    # Precompute bandwidth
    bandwidths = np.abs([grain.uncertainty for grain in grains])
    mean_bandwidth = np.mean(bandwidths)

    # Vectorized extraction of ages
    ages = np.array([grain.age for grain in grains])

    # Generate x values
    x = np.linspace(x_min, x_max, num_steps).reshape(-1, 1)

    # Fit KDE
    kde = KernelDensity(bandwidth=mean_bandwidth, kernel='gaussian')
    kde.fit(ages.reshape(-1, 1))

    # Score samples
    log_dens = kde.score_samples(x)
    y = np.exp(log_dens)

    # Normalize
    y_normalized = y / np.sum(y)

    return x.flatten(), y_normalized


def get_y_values(sample):
    x, y = kde_function(sample)
    return y


def replace_bandwidth(all_data, bandwidth):
    for i in range(0, len(all_data)):
        for j in range(0, len(all_data[i][2])):
            all_data[i][2][j] = (bandwidth,)
    return all_data
