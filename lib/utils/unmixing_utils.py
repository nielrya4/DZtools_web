from lib.objects.trials import UnmixingTrial
import numpy as np
import pandas as pd
from lib.utils import kde_utils


def do_monte_carlo(samples, num_trials=10000):
    samples.reverse()
    sink_sample = samples[0]
    source_samples = samples[1:]
    trials = [None] * num_trials

    sink_sample.replace_bandwidth(10)
    for source_sample in source_samples:
        source_sample.replace_bandwidth(10)

    sink_kde = kde_utils.get_y_values(sink_sample)
    source_kdes = [kde_utils.get_y_values(source_sample) for source_sample in source_samples]

    for i in range(0, num_trials):
        trial = UnmixingTrial(sink_kde, source_kdes)
        trials[i] = trial

    sorted_trials = sorted(trials, key=lambda x: x.d_val, reverse=True)
    top_trials = get_percent_of_array(sorted_trials, 1)
    random_configurations = [trial.random_configuration for trial in top_trials]

    source_contributions = np.average(random_configurations, axis=0)*100
    source_std = np.std(random_configurations, axis=0)*100

    contribution_table_d = build_contribution_table(source_samples, source_contributions, source_std, test_type="KS")
    return contribution_table_d, None, None


def get_percent_of_array(arr, percentage):
    array_length = len(arr)
    num_elements_in_percentage = int(np.round(array_length * percentage / 100, decimals=0))
    elements_returned = arr[:num_elements_in_percentage]
    return elements_returned


def build_contribution_table(samples, percent_contributions, standard_deviation, test_type="r2"):
    sample_names = [sample.name for sample in samples]
    data = {
        "Sample Name": sample_names,
        f"% Contribution ({test_type} test)": percent_contributions,
        "Standard Deviation": standard_deviation
    }
    df = pd.DataFrame(data)
    df.columns.name = "-"
    output = df.to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">')
    return output
