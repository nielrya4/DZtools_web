import numpy as np


def kde_function(sample, num_steps=1000, x_min=0, x_max=4000):
    x = np.linspace(x_min, x_max, num_steps)
    y = np.zeros_like(x)
    ages = [grain.age for grain in sample.grains]
    bandwidths = [grain.uncertainty for grain in sample.grains]
    for i in range(len(ages)):
        kernel_sum = np.zeros(num_steps)
        s = bandwidths[i]
        kernel_sum += (1.0 / (np.sqrt(2 * np.pi) * s)) * np.exp(-(x - float(ages[i])) ** 2 / (2 * float(s) ** 2))
        kernel_sum /= np.sum(kernel_sum)
        y += kernel_sum
    y /= np.sum(y)
    return x, y


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
