import os
import secrets
from utils import cleanup, routes, files
from flask import Flask, render_template, request, jsonify, session
from openpyxl import Workbook
import app as APP


def register (app):
    @app.route('/new/')
    def main2():
        spreadsheet_data=""
        if "last_uploaded_file" in session:
            last_uploaded_file = session['last_uploaded_file']
            spreadsheet_data=""
        return render_template('new_interface/new_interface.html', spreadsheet_data=spreadsheet_data)


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
        filename = 'spreadsheet.xlsx'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_key}_{filename}")
        wb.save(filepath)
        session['last_uploaded_file'] = os.path.basename(filepath)

        return jsonify({"result": "ok", "filename": filename})


