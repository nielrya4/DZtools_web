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


class Grain:
    def __init__(self, age, uncertainty):
        self.age = age
        self.uncertainty = uncertainty

    def __str__(self):
        return f"Age: {self.age} Ma, Uncertainty: ±{self.uncertainty} Ma"
