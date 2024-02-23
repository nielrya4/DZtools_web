import os
import openpyxl
from flask import render_template, request, jsonify, session
from openpyxl import Workbook
import app as APP


def register(app):
    @app.route('/data_editor/')
    def data_editor():
        spreadsheet_data = []
        if "last_uploaded_file" in session:
            last_uploaded_file = session.get("last_uploaded_file")
            file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            max_rows = sheet.max_row
            max_cols = sheet.max_column
            for row in range(1, max_rows + 1):
                row_data = []
                for col in range(1, max_cols + 1):
                    cell_value = sheet.cell(row=row, column=col).value
                    # Replace empty cell values with None
                    cell_value = cell_value if cell_value is not None else None
                    row_data.append(cell_value)
                spreadsheet_data.append(row_data)
        else:
            # If no file uploaded, create a 5x5 array with all cells set to None
            spreadsheet_data = [[None for _ in range(6)] for _ in range(6)]
        return render_template('data_editor/data_editor.html', spreadsheet_data=spreadsheet_data)

    @app.route('/json/save', methods=['POST'])
    def json_save():
        session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
        data = request.get_json()['data']

        # Create a new Workbook
        wb = Workbook()
        ws = wb.active

        # Write the data to the worksheet
        for col_idx, column in enumerate(data, start=1):
            for row_idx, value in enumerate(column, start=1):
                ws.cell(row=col_idx, column=row_idx, value=value)

        # Save the workbook to a file in the uploads folder
        if session.get('last_uploaded_file', 0) == 0:
            filename = 'spreadsheet.xlsx'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_key}_{filename}")
            session['last_uploaded_file'] = os.path.basename(filepath)
            print(session["last_uploaded_file"])
        else:
            filepath = os.path.join(APP.UPLOAD_FOLDER, session['last_uploaded_file'])
            print(filepath)
        wb.save(str(filepath))
        return jsonify({"result": "ok", "filename": filepath})


