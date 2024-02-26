import numpy as np


class Sample:
    def __init__(self, name, grains):
        self.name = name
        self.grains = grains  # Now storing instances of Grain objects

    def __str__(self):
        result = f"Name: {self.name}; Grains:"
        for grain in self.grains:
            result += f" ({str(grain)})"
        result += ";"
        return result

    def replace_bandwidth(self, new_bandwidth):
        for grain in self.grains:
            grain.uncertainty = new_bandwidth
        return self

    def get_relative_contribution(self):
        target_ages = np.array([grain.age for grain in self.grains])
        target_uncertainties = np.array([grain.uncertainty for grain in self.grains])
        total_target_ages = np.sum(target_ages)
        total_target_uncertainties = np.sum(target_uncertainties)
        relative_contribution = total_target_ages / total_target_uncertainties
        return relative_contribution

    def get_standard_deviation(self):
        uncertainties = np.array([grain.uncertainty for grain in self.grains])
        standard_deviation = np.std(uncertainties)
        return standard_deviation


class Grain:
    def __init__(self, age, uncertainty):
        self.age = age
        self.uncertainty = uncertainty

    def __str__(self):
        return f"Age: {self.age} Ma, Uncertainty: ±{self.uncertainty} Ma"
