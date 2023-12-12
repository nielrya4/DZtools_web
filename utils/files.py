import openpyxl
import itertools
import pandas as pd
import numpy as np

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_pdp_excel(file):
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
                data = [value for value in sheet.iter_rows(min_col=col, max_col=col, min_row=2, values_only=True)]
                sigma = [value for value in sheet.iter_rows(min_col=col + 1, max_col=col + 1, min_row=2, values_only=True)]
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
            similarity_score = np.sqrt(np.sum(np.multiply(y1, y2)))
            similarity_matrix[i, j] = similarity_score

    # Normalize the similarity matrix to have scores in the range [0, 1]
    normalized_similarity_matrix = similarity_matrix / similarity_matrix.max(axis=1, keepdims=True)

    # Create a DataFrame with the normalized similarity scores and labels
    if row_labels is None:
        row_labels = [f'Data {i+1}' for i in range(num_data_sets)]

    if col_labels is None:
        col_labels = [f'Data {i+1}' for i in range(num_data_sets)]

    df = pd.DataFrame(normalized_similarity_matrix, columns=col_labels, index=row_labels)

    return df

