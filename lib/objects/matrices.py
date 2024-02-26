import pandas as pd
import numpy as np


class RelativeSourceContributionMatrix:
    def __init__(self, samples):
        self.samples = samples

    def get_contribution_matrix(self):
        samples = self.samples if len(self.samples) != 1 else [self.samples]
        rows = len(self.samples)
        cols = 3
        matrix = np.zeros((rows, cols))
        for i, sample in enumerate(samples):
            matrix[0, i] = sample.name
        for i, sample in enumerate(samples):
            matrix[1, i] = sample.get_relative_contribution()
        for i, sample in enumerate(samples):
            matrix[2, i] = sample.get_standard_deviation()

        row_labels = [i for i in range(0, len(samples))]
        col_labels = ["Sample Names", "Relative Contribution", "Standard Deviation"]

        df = pd.DataFrame(matrix, columns=col_labels, index=row_labels)
        return df
