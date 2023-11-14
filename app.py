import base64
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from io import BytesIO
from matplotlib.figure import Figure
import openpyxl
import numpy as np
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    # Generate the figure without using pyplot.
    fig = Figure()
    plt = fig.subplots()

    # Call the kernel_density_estimation function to get the KDE result
    kde_result = kernel_density_estimation(data, sigma)

    # Extract X and Y values from the result
    x_values = kde_result[:, 0]
    y_values = kde_result[:, 1]

    # Create a KDE plot using Matplotlib
    plt.plot(x_values, y_values, label='KDE')
    plt.legend()

    # Save the plot to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the HTML output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

def kernel_density_estimation(data, sigma, nsteps=100):
    result = np.zeros((nsteps, 2))
    x = np.linspace(min(data) - 2 * max(sigma), max(data) + 2 * max(sigma), nsteps)
    y = np.zeros(nsteps)

    N = len(data)  # number of data points

    # Kernel density estimation
    for i in range(N):
        y = y + 1.0 / N * (1.0 / (np.sqrt(2 * np.pi) * sigma[i])) * np.exp(-(x - data[i])**2 / (2 * sigma[i]**2))

    # Compilation of the X, Y to result. Good for creating plot(x, y)
    result[:, 0] = x
    result[:, 1] = y

    return result
@app.route('/', methods=['GET', 'POST'])
def upload_file():
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
                result = plotKDE(data, sigma)
                return result
            except ValueError as e:
                flash(str(e))
                return redirect(request.url)

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
