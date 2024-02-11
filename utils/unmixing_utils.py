from objects.trials import UnmixingTrial
import numpy as np
import pandas as pd


def do_monte_carlo(samples, num_trials=10000):
    samples.reverse()
    sink_sample = samples[0]
    source_samples = samples[1:]
    trials = []

    # First do the trials.py
    for i in range(num_trials):
        trial = UnmixingTrial(sink_sample, source_samples)
        trials.append(trial)

    sorted_trials = sorted(trials, key=lambda x: x.d_val)
    top_trials = get_percent_of_array(sorted_trials, 1)
    random_configurations = [trial.random_configuration for trial in top_trials]

    # Concatenate random_configurations into a single 2D array
    random_configurations_concatenated = np.vstack(random_configurations)

    source_contributions = np.average(random_configurations_concatenated, axis=0)
    source_std = np.std(random_configurations_concatenated, axis=0)

    contribution_table_d = build_contribution_table(source_samples, source_contributions, source_std, test_type="KS")
    return contribution_table_d


def get_percent_of_array(arr, percentage):
    array_length = len(arr)
    num_elements_in_percentage = int(array_length * percentage / 100)
    elements_returned = arr[:num_elements_in_percentage]
    return elements_returned


def build_contribution_table(samples, percent_contributions, standard_deviation, test_type="r2"):
    sample_names = [sample.name for sample in samples]
    data = {
        "Sample Name": sample_names,
        f"% Contribution ({test_type} test)": percent_contributions,
        "Standard Deviation": standard_deviation
    }
    df = pd.DataFrame(data).to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">')
    return df
