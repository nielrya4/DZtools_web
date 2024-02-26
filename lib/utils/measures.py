# measures.py by Kurt Sundell. Interpreted by Ryan Nielsen to work directly with detrital zircon samples.
import numpy as np
from lib.utils.cdf_utils import cdf_function
from lib.utils import kde_utils


# KS Test (Massey, 1951) is the max absolute difference btw 2 CDF curves
def ks_test(sample1, sample2):
    bins_count1, data1 = cdf_function(sample1)
    bins_count2, data2 = cdf_function(sample2)
    data1, data2 = np.ma.asarray(data1), np.ma.asarray(data2)
    n1, n2 = (data1.count(), data2.count())
    mix = np.ma.concatenate((data1.compressed(), data2.compressed()))
    mix_sort = mix.argsort(kind='mergesort')
    csum = np.where(mix_sort < n1, 1. / n1, -1. / n2).cumsum()
    ks_test_d = max(np.abs(csum))
    return ks_test_d


# Kuiper test (Kuiper, 1960) is the sum of the max difference of CDF1 - CDF2 and CDF2 - CDF1
def kuiper_test(sample1, sample2):
    bins_count1, data1 = cdf_function(sample1)
    bins_count2, data2 = cdf_function(sample2)
    data1, data2 = np.ma.asarray(data1), np.ma.asarray(data2)
    n1, n2 = data1.count(), data2.count()
    mix = np.ma.concatenate((data1.compressed(), data2.compressed()))
    mix_sort = mix.argsort(kind='mergesort')
    csum = np.where(mix_sort < n1, 1. / n1, -1. / n2).cumsum()
    kuiper_test_v = max(csum) + max(csum * -1)
    return kuiper_test_v


# Similarity (Gehrels, 2000) is the sum of the geometric mean of each point along x for two PDPs or KDEs
def similarity_test(sample1, sample2):
    y1_values = kde_utils.get_y_values(sample1)
    y2_values = kde_utils.get_y_values(sample2)
    similarity = np.sum(np.sqrt(y1_values * y2_values))
    return similarity


def dissimilarity_test(sample1, sample2):
    dissimilarity = float(1 - similarity_test(sample1, sample2))
    return dissimilarity


# Likeness (Satkoski et al., 2013) is the complement to Mismatch (Amidon et al., 2005) and is the sum of the
# absolute difference divided by 2 for every pair of points along x for two PDPs or KDEs
def likeness_test(sample1, sample2):
    y1_values = kde_utils.get_y_values(sample1)
    y2_values = kde_utils.get_y_values(sample2)
    likeness = 1 - np.sum(abs(y1_values - y2_values)) / 2
    return likeness


# Cross-correlation is the coefficient of determination (R squared),
# the simple linear regression between two PDPs or KDEs
def cross_correlation_test(sample1, sample2):
    y1_values = kde_utils.get_y_values(sample1)
    y2_values = kde_utils.get_y_values(sample2)
    correlation_matrix = np.corrcoef(y1_values, y2_values)
    correlation_xy = correlation_matrix[0, 1]
    cross_correlation = correlation_xy ** 2
    return cross_correlation
