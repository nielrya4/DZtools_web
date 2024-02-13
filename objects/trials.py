from utils import unmixing_utils, measures, kde_utils, cdf_utils, pdp_utils
from sklearn.metrics import r2_score
from objects.zircon import Sample
import numpy as np
import random
import math


class UnmixingTrial:
    def __init__(self, sink_sample, source_samples):
        self.sink_sample = sink_sample
        self.source_samples = source_samples
        rands, d_val, v_val, r2_val = self.__do_trial()
        self.random_configuration = rands
        self.d_val = d_val
        self.v_val = v_val
        self.r2_val = r2_val

    def __do_trial(self):
        sink_sample = self.sink_sample
        source_samples = self.source_samples

        sink_sample.replace_bandwidth(10)
        for source_sample in source_samples:
            source_sample.replace_bandwidth(10)

        sink_cdf = kde_utils.get_y_values(sink_sample)
        source_cdfs = [kde_utils.get_y_values(source_sample) for source_sample in source_samples]

        num_sources = len(source_samples)
        rands = self.__make_cumulative_random(num_sources)

        model_cdf = np.zeros_like(sink_cdf)
        for j, source_cdf in enumerate(source_cdfs):
            scale_weight = rands[j]
            for k in range(len(sink_cdf)):
                model_cdf[k] += source_cdf[k] * scale_weight

        d_val = self.__r2(sink_cdf, model_cdf)
        v_val = None
        r2_val = None
        return rands, d_val, v_val, r2_val

    @staticmethod
    def __make_cumulative_random(num_samples):
        rands = [random.random() for _ in range(num_samples)]
        total = sum(rands)
        normalized_rands = [rand / total for rand in rands]
        return normalized_rands

    @staticmethod
    def __get_percent_of_array(arr, percentage):
        array_length = len(arr)
        num_elements_in_percentage = int(np.round(array_length * percentage / 100, decimals=0))
        print(num_elements_in_percentage)
        elements_returned = arr[:num_elements_in_percentage]
        return elements_returned

    @staticmethod
    def __ks(data1, data2):
        data1, data2 = np.ma.asarray(data1), np.ma.asarray(data2)
        n1, n2 = (data1.count(), data2.count())
        mix = np.ma.concatenate((data1.compressed(), data2.compressed()))
        mix_sort = mix.argsort(kind='mergesort')
        csum = np.where(mix_sort < n1, 1. / n1, -1. / n2).cumsum()
        ks_test_d = max(np.abs(csum))
        return ks_test_d

    @staticmethod
    def __kuiper(data1, data2):
        data1, data2 = np.ma.asarray(data1), np.ma.asarray(data2)
        n1, n2 = data1.count(), data2.count()
        mix = np.ma.concatenate((data1.compressed(), data2.compressed()))
        mix_sort = mix.argsort(kind='mergesort')
        csum = np.where(mix_sort < n1, 1. / n1, -1. / n2).cumsum()
        kuiper_test_v = max(csum) + max(csum * -1)
        return kuiper_test_v

    @staticmethod
    def __r2(data1, data2):
        r_squared = r2_score(data1, data2)
        return r_squared

    @staticmethod
    def __similarity(data1, data2):
        similarity = np.sum(np.sqrt(data1 * data2))
        return similarity
