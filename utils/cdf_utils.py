import numpy as np


def cdf_function(sample):
    ages = [grain.age for grain in sample.grains]
    count, bins_count = np.histogram(ages, bins=1000, density=True)
    pdf = count / sum(count)
    cdf_values = np.cumsum(pdf)
    return bins_count, cdf_values
