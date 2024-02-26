import os
from flask import render_template, session, request, flash, redirect
import app as APP
from lib.objects.documents import SampleSheet
from lib.utils import files, dz_script


def register(app):
    @app.route('/project_editor/', methods=['GET', 'POST'])
    def project_editor():
        items = None
        if session.get("last_uploaded_file") is not None and session.get("last_uploaded_script_file") is not None:
            last_uploaded_file = session.get("last_uploaded_file")
            file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
            sample_sheet = SampleSheet(file)
            samples = sample_sheet.read_samples()

            last_uploaded_script_file = session.get("last_uploaded_script_file")
            code_file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_script_file)
            items = dz_script.run(code_file, samples)
            code = open(code_file, "r").read()
            return render_template('project_editor/project_editor.html', items=items, code=code)
        return render_template('project_editor/project_editor.html')

    @app.route('/upload_script_file', methods=['POST'])
    def upload_script_file():
        session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
        file = request.files['code_file']
        if not file and 'last_uploaded_script_file' not in session:
            flash('No file provided in the form, and no last uploaded file in the session.', 'error')
            session['display_alert'] = True  # Set a session flag to display the alert
            print("No file...")
            return redirect(request.referrer)

        if file:
            # File provided in the form
            uploaded_file = files.upload_file(file, session_key)
            session['last_uploaded_script_file'] = os.path.basename(uploaded_file)
            print(f"Uploading file: {file.filename} as {session['last_uploaded_script_file']}")
        else:
            flash('No last uploaded file found in the session.')
            return redirect(request.referrer)
        return redirect(request.referrer)

    @app.route('/submit_code', methods=['GET', 'POST'])
    def submit_code():
        pass
