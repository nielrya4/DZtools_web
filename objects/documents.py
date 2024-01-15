import openpyxl
from objects.zircon import Sample, Grain


class Spreadsheet:
    def __init__(self, file):
        self.file = file

    def read_samples(self):
        file = self.file
        samples = []
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        for i in range(1, sheet.max_column + 1, 2):
            sample_name = sheet.cell(row=1, column=i).value
            grains = []
            for row in range(2, sheet.max_row + 1):
                age = sheet.cell(row=row, column=i).value
                uncertainty = sheet.cell(row=row, column=i + 1).value
                if age is not None and uncertainty is not None:
                    grains.append(Grain(age, uncertainty))
            sample = Sample(sample_name, grains)
            samples.append(sample)
        samples.reverse()
        return samples
