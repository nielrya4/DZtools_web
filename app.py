import base64
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file, Response, session
from werkzeug.utils import secure_filename
from io import BytesIO
from matplotlib.figure import Figure
import openpyxl
import numpy as np
import secrets


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secrets.token_hex(16)


@app.route('/', methods=['GET', 'POST'])
def main():
    graph_data = None

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                data, sigma = read_excel(file)
                session['data'] = data  # Store data in the session
                session['sigma'] = sigma  # Store sigma in the session
                graph_data = plotKDE(data, sigma)
            except ValueError as e:
                flash(str(e))
                return redirect(request.url)

    return render_template('index.html', graph_data=graph_data)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_excel(file):
    data = []
    sigma = []
    try:
        wb = openpyxl.load_workbook(file, read_only=True)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(row[0])
            sigma.append(row[1])
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
    return data, sigma


def plotKDE(data, sigma):
    fig = Figure(figsize=(8, 6), dpi=100)                                              #Build the graph off of matplotlib's Figure
    plt = fig.subplots()
    kde_result = kernel_density_estimation(data, sigma)         #Calculate the (x,y) points from our data and uncertainty
    x_values = kde_result[:, 0]                                 #Separate x and y values
    y_values = kde_result[:, 1]
    plt.plot(x_values, y_values, label='KDE')                   #Plot our graph
    plt.legend()                                                #Make it have a legend
    buf = BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")  # Save the figure as SVG
    data = buf.getvalue().decode("utf-8")
    return f"<div>{data}</div>"


def download_image_from_session(format, filename):
    data = session.get('data', [])
    sigma = session.get('sigma', 1)

    fig = Figure(figsize=(8, 6), dpi=300)
    plt = fig.subplots()
    kde_result = kernel_density_estimation(data, sigma)
    x_values = kde_result[:, 0]
    y_values = kde_result[:, 1]
    plt.plot(x_values, y_values, label='KDE')
    plt.legend()
    buf = BytesIO()
    fig.savefig(buf, format=format, bbox_inches="tight")
    buf.seek(0)
    return Response(buf, mimetype=f'image/{format}', headers={'Content-Disposition': f'attachment;filename={filename}'})


@app.route('/download', methods=['GET'])
def download_plot():
    format = request.args.get('format', 'png')

    if format == 'png':
        return download_image_from_session(format='png', filename='plot.png')
    elif format == 'svg':
        return download_image_from_session(format='svg', filename='plot.svg')
    else:
        flash('Invalid download format')
        return redirect(url_for('upload_file'))

def kernel_density_estimation(data, sigma, nsteps=1000):
    result = np.zeros((nsteps, 2))
    x = np.linspace(min(data) - 2 * max(sigma),
                    max(data) + 2 * max(sigma),
                    nsteps)
    y = np.zeros(nsteps)
    N = len(data)  # number of data points

    # Check if sigma is a single value and convert it to a list
    sigma = [sigma] if not isinstance(sigma, (list, tuple, np.ndarray)) else sigma

    for i in range(N):
        for s in sigma:
            y = (y + 1.0 / N *
                 (1.0 / (np.sqrt(2 * np.pi) * s)) *
                 np.exp(-(x - data[i]) ** 2 / (2 * s ** 2)))

    result[:, 0] = x
    result[:, 1] = y
    return result



if __name__ == '__main__':
    app.run(port=8000, debug=True)
