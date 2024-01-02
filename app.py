import os, secrets, schedule, threading, time
from io import BytesIO
from utils import downloads, files, pdp, cdf, kde
from flask import Flask, render_template, request, redirect, flash, send_from_directory, send_file

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


@app.route('/dz_stats/', methods=['GET', 'POST'])
def dz_stats():
    kde_bandwidth = request.form.get("kde_bandwidth", 10)
    kde_stacked = False
    graph_data, cdf_data, similarity_data, likeness_data, ks_data, kuiper_data, cross_correlation_data \
        = None, None, None, None, None, None, None
    kde_graph, cdf_graph = True, True
    similarity_matrix, likeness_matrix, ks_matrix, kuiper_matrix, cross_correlation_matrix \
        = None, None, None, None, None
    if request.method == 'POST':
        if 'file' not in request.files:
            print('Incomplete form submission')
            return redirect(request.url)

        kde_bandwidth = int(request.form['kde_bandwidth'])
        kde_stacked = True if request.form.get('kde_stacked') == "true" else False
        kde_graph = True if request.form.get('kde_graph') == "true" else False

        cdf_graph = True if request.form.get('cdf_graph') == "true" else False

        similarity_matrix = True if request.form.get('similarity_matrix') == "true" else False
        likeness_matrix = True if request.form.get('likeness_matrix') == "true" else False
        ks_matrix = True if request.form.get('ks_matrix') == "true" else False
        kuiper_matrix = True if request.form.get('kuiper_matrix') == "true" else False
        cross_correlation_matrix = True if request.form.get('cross_correlation_matrix') == "true" else False

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and files.allowed_file(file.filename):
            try:
                filename = SECRET_KEY + 'uploaded_file.pkl'
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(file.filename, filepath)

                all_data = files.read_excel(file)
                all_data = kde.replace_bandwidth(all_data, bandwidth=kde_bandwidth)
                all_data.reverse()
                # Save data to the file system
                filename = SECRET_KEY + 'all_data.pkl'
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(all_data, filepath)

                graph_data = kde.kde_plot(all_data, stacked=kde_stacked) if kde_graph else None
                cdf_data = cdf.plot_cdf(all_data) if cdf_graph else None

                row_labels = kde.get_headers(all_data)
                col_labels = kde.get_headers(all_data)
                col_labels.reverse()
                if similarity_matrix:
                    similarity_data = files.generate_matrix(kde.get_y_values(all_data),
                                                            row_labels=row_labels,
                                                            col_labels=col_labels,
                                                            matrix_type="similarity")
                if likeness_matrix:
                    likeness_data = files.generate_matrix(kde.get_y_values(all_data),
                                                          row_labels=row_labels,
                                                          col_labels=col_labels,
                                                          matrix_type="likeness")
                if ks_matrix:
                    ks_data = files.generate_matrix(kde.get_y_values(all_data),
                                                    row_labels=row_labels,
                                                    col_labels=col_labels,
                                                    matrix_type="ks")
                if kuiper_matrix:
                    kuiper_data = files.generate_matrix(kde.get_y_values(all_data),
                                                        row_labels=row_labels,
                                                        col_labels=col_labels,
                                                        matrix_type="kuiper")
                if cross_correlation_matrix:
                    cross_correlation_data = files.generate_matrix(kde.get_y_values(all_data),
                                                                   row_labels=row_labels,
                                                                   col_labels=col_labels,
                                                                   matrix_type="cross_correlation")
            except ValueError as e:
                flash(str(e))
                print(f"{e}")
                return redirect(request.url)
    return render_template('dz_stats.html',
                           graph_data=graph_data,
                           kde_bandwidth=kde_bandwidth,
                           cdf_data=cdf_data,
                           similarity_data=similarity_data,
                           likeness_data=likeness_data,
                           ks_data=ks_data,
                           kuiper_data=kuiper_data,
                           cross_correlation_data=cross_correlation_data,
                           kde_graph=kde_graph,
                           cdf_graph=cdf_graph,
                           similarity_matrix=similarity_matrix,
                           likeness_matrix=likeness_matrix,
                           ks_matrix=ks_matrix,
                           kuiper_matrix=kuiper_matrix,
                           cross_correlation_matrix=cross_correlation_matrix,
                           kde_stacked=kde_stacked)


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

    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=download_name,
        mimetype=mimetype
    )


@app.route('/DZ.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/DZ.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/menu.ico')
def menu_icon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/menu.ico', mimetype='image/vnd.microsoft.icon')


# Cleaning up data folder-----------------------------------------------------------------------------------------------


def cleanup_job():
    print("Cleaning up .pkl files...")
    for filename in os.listdir(app.config['DATA_FOLDER']):
        if filename.endswith(".pkl"):
            filepath = os.path.join(app.config['DATA_FOLDER'], filename)
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
