from lib.objects.zircon import Sample, Grain


def create_mixed_sample(samples):
    sample_name = "Mixed Sample"
    sample_grains = []
    for sample in samples:
        for grain in sample.grains:
            sample_grains.append(grain)
    mixed_sample = Sample(sample_name, sample_grains)
    return mixed_sample

# delete this:
def create_mean_sample(samples):
    longest_sample = max(samples, key=lambda sample: len(sample.grains))
    target_length = len(longest_sample.grains)
    sample_name = "Mean Sample"
    sample_grains = []
    for i in range(target_length):
        age_sum = 0
        uncertainty_sum = 0
        samples_with_grains = 0
        for sample in samples:
            if i < len(sample.grains) and sample.grains[i] is not None:
                age_sum += sample.grains[i].age
                uncertainty_sum += sample.grains[i].uncertainty
                samples_with_grains += 1
        if samples_with_grains > 0:
            age_average = age_sum / samples_with_grains
            uncertainty_average = uncertainty_sum / samples_with_grains
            sample_grains.append(Grain(age_average, uncertainty_average))
        else:
            sample_grains.append(None)
    mean_sample = Sample(sample_name, sample_grains)
    return mean_sample