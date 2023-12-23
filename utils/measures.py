# measures.py by Kurt Sundell. Reformatted by Ryan Nielsen
import numpy as np


# KS Test (Massey, 1951) is the max absolute difference btw 2 CDF curves
def ks_test(data1, data2):
    data1, data2 = np.ma.asarray(data1), np.ma.asarray(data2)
    n1, n2 = (data1.count(), data2.count())
    mix = np.ma.concatenate((data1.compressed(), data2.compressed()))
    mix_sort = mix.argsort(kind='mergesort')
    csum = np.where(mix_sort < n1, 1. / n1, -1. / n2).cumsum()
    ks_test_d = max(np.abs(csum))
    return ks_test_d


# Kuiper test (Kuiper, 1960) is the sum of the max difference of CDF1 - CDF2 and CDF2 - CDF1
def kuiper_test(data1, data2):
    data1, data2 = np.ma.asarray(data1), np.ma.asarray(data2)
    n1, n2 = data1.count(), data2.count()
    mix = np.ma.concatenate((data1.compressed(), data2.compressed()))
    mix_sort = mix.argsort(kind='mergesort')
    csum = np.where(mix_sort < n1, 1. / n1, -1. / n2).cumsum()
    kuiper_test_v = max(csum) + max(csum * -1)
    return kuiper_test_v


# Similarity (Gehrels, 2000) is the sum of the geometric mean of each point along x for two PDPs or KDEs
def similarity_test(data1, data2):
    similarity = np.sum(np.sqrt(data1*data2))
    return similarity


# Likeness (Satkoski et al., 2013) is the complement to Mismatch (Amidon et al., 2005) and is the sum of the
# absolute difference divided by 2 for every pair of points along x for two PDPs or KDEs
def likeness_test(data1, data2):
    likeness = 1 - np.sum(abs(data1 - data2)) / 2
    return likeness


# Cross-correlation is the coefficient of determination (R squared),
# the simple linear regression between two PDPs or KDEs
def cross_correlation_test(data1, data2):
    correlation_matrix = np.corrcoef(data1, data2)
    correlation_xy = correlation_matrix[0, 1]
    cross_correlation = correlation_xy ** 2
    return cross_correlation
