import os, secrets, schedule, threading, time
from io import BytesIO
from datetime import datetime, timedelta
from utils import downloads, files, pdp, kde
import applications
from applications import cmd
from flask import Flask, render_template, request, redirect, flash, send_from_directory, send_file, session

UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
SECRET_KEY = secrets.token_hex(16)
app.config['SECRET_KEY'] = SECRET_KEY
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/dz_nmf/', methods=['GET', 'POST'])
def dz_nmf():

    return render_template("dz_nmf.html")


@app.route('/dz_stats/', methods=['GET', 'POST'])
def dz_stats():
    # Set defaults to render the page
    results = render_template("dz_stats.html",
                              kde_bandwidth=10,
                              kde_graph=True,
                              cdf_graph=True)

    if request.method == 'POST':
        file = request.files.get('file')

        if not file and 'last_uploaded_file' not in session:
            flash('No file provided in the form, and no last uploaded file in the session.', 'error')
            session['display_alert'] = True  # Set a session flag to display the alert
            return redirect(request.url)

        try:
            kde_bandwidth = int(request.form.get('kde_bandwidth', 10))
            kde_stacked = request.form.get('kde_stacked') == "true"
            kde_graph = request.form.get('kde_graph') == "true"
            cdf_graph = request.form.get('cdf_graph') == "true"

            similarity_matrix = request.form.get('similarity_matrix') == "true"
            likeness_matrix = request.form.get('likeness_matrix') == "true"
            ks_matrix = request.form.get('ks_matrix') == "true"
            kuiper_matrix = request.form.get('kuiper_matrix') == "true"
            cross_correlation_matrix = request.form.get('cross_correlation_matrix') == "true"

            session_key = session.get('SECRET_KEY', SECRET_KEY)

            if file:
                # File provided in the form
                uploaded_file = files.upload_file(file, session_key)
                session['last_uploaded_file'] = os.path.basename(uploaded_file)
            else:
                # No file provided in the form, use the last uploaded file from the session
                last_uploaded_file = session.get('last_uploaded_file')
                if last_uploaded_file:
                    uploaded_file = os.path.join(UPLOAD_FOLDER, last_uploaded_file)
                else:
                    flash('No last uploaded file found in the session.')
                    return redirect(request.url)

            all_data = files.read_excel(uploaded_file)
            all_data = kde.replace_bandwidth(all_data, bandwidth=kde_bandwidth)
            all_data.reverse()

            # Save data to the file system
            filename = f"{session_key}_all_data.pkl"
            filepath = os.path.join(app.config['DATA_FOLDER'], filename)
            files.save_data_to_file(all_data, filepath)

            results = applications.dz_stats.display(all_data,
                                                    kde_graph=kde_graph,
                                                    kde_stacked=kde_stacked,
                                                    cdf_graph=cdf_graph,
                                                    similarity_matrix=similarity_matrix,
                                                    likeness_matrix=likeness_matrix,
                                                    ks_matrix=ks_matrix,
                                                    kuiper_matrix=kuiper_matrix,
                                                    cross_correlation_matrix=cross_correlation_matrix)
        except ValueError as e:
            flash(str(e))
            print(f"{e}")

    return results


@app.route('/pdp/', methods=['GET', 'POST'])  # App route for the PDP page
def pdp_page():
    graph_data = None
    similarity_data = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and files.allowed_file(file.filename):
            try:
                all_data = files.read_excel(file)
                all_data.reverse()
                filename = SECRET_KEY + 'all_data.pkl'
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(all_data, filepath)
                graph_data = pdp.plot_pdp(all_data)
                row_labels = pdp.get_headers(all_data)
                col_labels = pdp.get_headers(all_data)
                row_labels.reverse()
                similarity_data = files.generate_matrix(pdp.get_y_values(all_data),
                                                        row_labels=row_labels,
                                                        col_labels=col_labels)
            except ValueError as e:
                flash(str(e))
                print(f"{e}")
                return redirect(request.url)

    return render_template('pdp.html',
                           graph_data=graph_data,
                           similarity_data=similarity_data)


@app.route('/kde/', methods=['GET', 'POST'])  # App route for the KDE page
def kde_page():
    graph_data = None
    similarity_data = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and files.allowed_file(file.filename):
            try:
                all_data = files.read_excel(file)
                all_data.reverse()
                filename = SECRET_KEY + 'all_data.pkl'
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(all_data, filepath)
                graph_data = kde.kde_plot(all_data, stacked=True)
            except ValueError as e:
                flash(str(e))
                print(f"Error on KDE page: {e}")
                return redirect(request.url)  # Reload

    return render_template('kde.html',
                           graph_data=graph_data,
                           excel_data=similarity_data)  # If it passes, add our graph data to index.html


@app.route("/download_cdf", methods=["GET"])
def download_cdf():
    return downloads.download_plot(
        files.read_data_from_file(os.path.join(app.config['DATA_FOLDER'],
                                               SECRET_KEY + "all_data.pkl")),
        plot_type='cdf')


@app.route('/download_pdp', methods=['GET'])
def download_pdp():
    return downloads.download_plot(
        files.read_data_from_file(os.path.join(app.config['DATA_FOLDER'],
                                               SECRET_KEY + "all_data.pkl")),
        plot_type='pdp')


@app.route('/download_kde', methods=['GET'])
def download_kde():
    return downloads.download_plot(
        files.read_data_from_file(os.path.join(app.config['DATA_FOLDER'],
                                               SECRET_KEY + "all_data.pkl")),
        plot_type='kde')


@app.route('/download_excel')
def download_excel():
    matrix_type = request.args.get('matrix_type', "similarity")
    all_data = files.read_data_from_file(os.path.join(app.config['DATA_FOLDER'], SECRET_KEY + "all_data.pkl"))
    y_value_arrays = kde.get_y_values(all_data)
    y_value_arrays.reverse()
    row_labels = kde.get_headers(all_data)

    col_labels = kde.get_headers(all_data)
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


@app.route('/DZ.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/DZ.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/menu.ico')
def menu_icon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/menu.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/cmd/', methods=['GET', 'POST'])
def cmd():
    output = request.form.get('output', "")
    if request.method == 'POST':
        command = request.form['command']
        command = command.strip()
        result = applications.cmd.process_cmd(command)
        if result.startswith("text "):
            output = output + f"$ {command}\n" + result[5:] + " \n"
        elif result.startswith("page "):
            return result[5:]
    return render_template('cmd.html', output=output)


# Cleaning up data folder-----------------------------------------------------------------------------------------------


def cleanup_job():
    print("Cleaning up files in data folder...")
    cleanup_folder(app.config['DATA_FOLDER'])
    print("Cleaning up files in upload folder...")
    cleanup_folder(app.config['UPLOAD_FOLDER'])


def cleanup_folder(folder_path):
    current_time = datetime.now()
    twenty_four_hours_ago = current_time - timedelta(hours=24)

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))

        if file_creation_time < twenty_four_hours_ago:
            os.remove(filepath)
            print(f"Deleted: {filename}")


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Start the data cleanup scheduler in a separate thread
schedule.every().hour.do(cleanup_job)
schedule_thread = threading.Thread(target=run_scheduler)
schedule_thread.start()

if __name__ == '__main__':
    cleanup_job()
    app.run(port=8000, debug=True)
