from utils import unmixing_utils, measures, kde_utils, cdf_utils
from objects.zircon import Sample
import numpy as np
import random


class UnmixingTrial:
    def __init__(self, sink_sample, source_samples):
        self.sink_sample = sink_sample
        self.source_samples = source_samples
        rands, d_val, v_val, r2_val = self.__do_trial_2()
        self.random_configuration = rands
        self.d_val = d_val
        self.v_val = v_val
        self.r2_val = r2_val

    def __do_trial(self):
        sink_sample = self.sink_sample
        source_samples = self.source_samples
        num_sources = len(source_samples)
        rands = self.__make_cumulative_random(num_sources)
        model_sample_grains = []
        for j, source_sample in enumerate(source_samples):
            source_sample_grains = [grain for grain in source_sample.grains]
            random.shuffle(source_sample_grains)
            subsample_weight = rands[j]
            subsample_grains = []
            for i in range(0, int(subsample_weight)):
                subsample_grains.append(self.__get_percent_of_array(source_sample_grains, subsample_weight*100))
            for grain in subsample_grains:
                model_sample_grains.append(grain)
        model_sample = Sample(name=f"Model", grains=[grain for grain in model_sample_grains])
        d_val = measures.ks_test(sink_sample, model_sample)
        v_val = measures.kuiper_test(sink_sample, model_sample)
        r2_val = measures.cross_correlation_test(sink_sample, model_sample)
        return rands, d_val, v_val, r2_val

    def __do_trial_2(self):
        sink_sample = self.sink_sample
        source_samples = self.source_samples
        num_sources = len(source_samples)
        rands = self.__make_cumulative_random(num_sources)

        sink_cdf = cdf_utils.get_y_values(sink_sample)
        source_cdfs = [cdf_utils.get_y_values(source_sample) for source_sample in source_samples]

        model_cdf = []
        for j, source_cdf in enumerate(source_cdfs):
            random.shuffle(source_cdf)
            subsample_weight = rands[j]
            subsample_y_values = self.__get_percent_of_array(source_cdf, subsample_weight * 100)
            for y_value in subsample_y_values:
                model_cdf.append(y_value)
        model_cdf.sort()
        d_val = self.__ks(sink_cdf, model_cdf)
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
        num_elements_in_percentage = int(array_length * percentage / 100)
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