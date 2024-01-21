import os
from io import BytesIO
from flask import session, redirect, flash, request, send_from_directory, send_file, url_for
from utils import files, kde_utils, graph_utils
from objects.graphs import KDE, CDF, PDP
from objects.documents import SampleSheet
import app as APP


def register(app):
    @app.route("/download_cdf", methods=["GET"])
    def download_cdf():
        file_name = session["last_uploaded_file"][33:]
        file_format = request.args.get('format', 'png')
        title = f"Cumulative Distribution"
        if file_format in {'png', 'svg', 'pdf', 'eps'}:
            last_uploaded_file = session.get("last_uploaded_file")
            file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
            samples = SampleSheet(file).read_samples()
            cdf_graph = CDF(samples, title)
            return cdf_graph.download(f"{file_name.split('.', 1)[0]}.{file_format}", file_format)
        else:
            flash('Invalid download format')
            return redirect(url_for('main'))

    @app.route('/download_pdp', methods=['GET'])
    def download_pdp():
        file_name = session["last_uploaded_file"][33:]
        file_format = request.args.get('format', 'png')
        title = f"Probability Density Plot"
        if file_format in {'png', 'svg', 'pdf', 'eps'}:
            last_uploaded_file = session.get("last_uploaded_file")
            file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
            samples = SampleSheet(file).read_samples()
            pdp_graph = PDP(samples, title, False)
            return pdp_graph.download(f"{file_name.split('.', 1)[0]}.{file_format}", file_format)
        else:
            flash('Invalid download format')
            return redirect(url_for('main'))

    @app.route('/download_kde', methods=['GET'])
    def download_kde():
        file_name = session["last_uploaded_file"][33:]
        file_format = request.args.get('format', 'png')
        kde_bandwidth = int(session.get("kde_bandwidth", 10))
        kde_stacked = session.get("kde_stacked", False)
        title = f"Kernel Density Estimate (Bandwidth:{kde_bandwidth})"
        if file_format in {'png', 'svg', 'pdf', 'eps'}:
            last_uploaded_file = session.get("last_uploaded_file")
            file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
            samples = SampleSheet(file).read_samples()
            for sample in samples:
                sample.replace_bandwidth(kde_bandwidth)
            kde_graph = KDE(samples, title, kde_stacked)
            return kde_graph.download(f"{file_name.split('.', 1)[0]}.{file_format}", file_format)
        else:
            flash('Invalid download format')
            return redirect(url_for('main'))

    @app.route('/download_excel')
    def download_excel():
        matrix_type = request.args.get('matrix_type', "similarity")
        all_data = files.read_data_from_file(os.path.join(app.config['DATA_FOLDER'], APP.SECRET_KEY + "all_data.pkl"))
        y_value_arrays = kde_utils.get_y_values(all_data)
        y_value_arrays.reverse()
        row_labels = graph_utils.get_sample_names(all_data)

        col_labels = graph_utils.get_sample_names(all_data)
        col_labels.reverse()
        excel_data = files.generate_matrix(y_value_arrays,
                                           row_labels=row_labels,
                                           col_labels=col_labels,
                                           matrix_type=matrix_type)
        excel_buffer = BytesIO()
        download_format = request.args.get('format', 'xlsx')

        if download_format == 'xlsx':
            excel_data.to_excel(excel_buffer, index=True, engine='openpyxl', header=True)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            download_name = f'{matrix_type}_scores.xlsx'
        elif download_format == 'xls':
            excel_data.to_excel(excel_buffer, index=True, engine='xlwt', header=True)
            mimetype = 'application/vnd.ms-excel'
            download_name = f'{matrix_type}_scores.xls'
        elif download_format == 'csv':
            excel_data.to_csv(excel_buffer, index=True, header=True)
            mimetype = 'text/csv'
            download_name = f'{matrix_type}_scores.csv'
        else:
            return "Invalid format specified", 400

        excel_buffer.seek(0)

        return send_file(excel_buffer,
                         as_attachment=True,
                         download_name=download_name,
                         mimetype=mimetype)

    @app.route('/upload_file', methods=['POST'])
    def upload_file():
        session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
        file = request.files['file']

        if not file and 'last_uploaded_file' not in session:
            flash('No file provided in the form, and no last uploaded file in the session.', 'error')
            session['display_alert'] = True  # Set a session flag to display the alert
            print("No file...")
            return redirect(request.referrer)

        if file:
            # File provided in the form
            uploaded_file = files.upload_file(file, session_key)
            session['last_uploaded_file'] = os.path.basename(uploaded_file)
            print(f"Uploading file: {file.filename} as {session['last_uploaded_file']}")
        else:
            flash('No last uploaded file found in the session.')
            return redirect(request.referrer)
        return redirect(request.referrer)

    @app.route('/DZ.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'static/DZ.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/menu.ico')
    def menu_icon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'static/menu.ico', mimetype='image/vnd.microsoft.icon')
