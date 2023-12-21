import openpyxl
import pandas as pd
import numpy as np
from utils import format
import pickle

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_excel(file):
    try:
        wb = openpyxl.load_workbook(file, read_only=False)
        sheet = wb.active

        num_cols = 0
        for col in sheet.iter_cols(values_only=True):
            num_cols += 1

        all_data = []
        for col in range(1, num_cols + 1, 2):
            if sheet.cell(row=1, column=col).value != None:
                header = f"{sheet.cell(row=1, column=col).value}"
                data = format.trim_none([value for value in sheet.iter_rows(min_col=col, max_col=col, min_row=2, values_only=True)])
                sigma = format.trim_none([value for value in sheet.iter_rows(min_col=col + 1, max_col=col + 1, min_row=2, values_only=True)])
                data_set = [header, data, sigma]
                all_data.append(data_set)

    except Exception as e:
        print(f"{e}")
        raise ValueError(f"Error parsing Excel file: {e}")

    return all_data


def generate_excel_data(y_value_arrays, row_labels=None, col_labels=None):
    num_data_sets = len(y_value_arrays)
    similarity_matrix = np.zeros((num_data_sets, num_data_sets))

    for i, y1 in enumerate(y_value_arrays):
        for j, y2 in enumerate(y_value_arrays):
            # print(f"Y1 VALUE {y1}")
            # print(f"Y2 VALUE {y2}")
            similarity_score = np.sum(np.sqrt(np.multiply(y1, y2)))
            similarity_matrix[i, j] = similarity_score

    # Create a DataFrame with the normalized similarity scores and labels
    if row_labels is None:
        row_labels = [f'Data {i+1}' for i in range(num_data_sets)]

    if col_labels is None:
        col_labels = [f'Data {i+1}' for i in range(num_data_sets)]

    df = pd.DataFrame(similarity_matrix, columns=col_labels, index=row_labels)

    return df


def save_data_to_file(data, filepath):
    with open(filepath, 'wb') as file:
        pickle.dump(data, file)

# Example of reading data from a file
def read_data_from_file(filepath):
    with open(filepath, 'rb') as file:
        return pickle.load(file)
