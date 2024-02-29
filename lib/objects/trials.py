from lib.utils import kde_utils, cdf_utils
from sklearn.metrics import r2_score
import numpy as np
import random


class UnmixingTrial:
    def __init__(self, sink_kde, source_kdes):
        self.sink_kde = sink_kde
        self.source_kdes = source_kdes
        rands, d_val, v_val, r2_val = self.__do_trial()
        self.random_configuration = rands
        self.d_val = d_val
        self.v_val = v_val
        self.r2_val = r2_val

    def __do_trial(self):
        sink_kde = self.sink_kde
        source_kdes = self.source_kdes

        num_sources = len(source_kdes)
        rands = self.__make_cumulative_random(num_sources)

        model_kde = np.zeros_like(sink_kde)
        for j, source_kde in enumerate(source_kdes):
            scale_weight = rands[j]
            for k in range(len(sink_kde)):
                model_kde[k] += source_kde[k] * scale_weight

        d_val = self.__r2(sink_kde, model_kde)
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
