import base64
import numpy as np
from io import BytesIO
from flask import Flask, render_template, request
from matplotlib.figure import Figure

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    # Your data and bandwidth (sigma)
    data = [1,1,2,3,4,5,6,7,8,9]    # Replace with your actual data
    sigma = 1                       # Replace with your desired bandwidth
    result = plotKDE(data, sigma)
    return result

def plotKDE(data, sigma):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    plt = fig.subplots()
    # Call the kernel_density_estimation function to get the KDE result
    kde_result = kernel_density_estimation(data, sigma)
    # Extract X and Y values from the result
    x_values = kde_result[:, 0]
    y_values = kde_result[:, 1]
#
    # Create a KDE plot using Matplotlib
    plt.plot(x_values, y_values, label='KDE')
    #plt.xlabel('X')
    #plt.ylabel('Density')
    #plt.title('Kernel Density Estimation (KDE) Plot')
    plt.legend()
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

def kernel_density_estimation(data, sigma, nsteps=100):
    result = np.zeros((nsteps, 2))
    x = np.zeros(nsteps)
    y = np.zeros(nsteps)

    MAX = float('-inf')
    MIN = float('inf')
    N = len(data)  # number of data points

    # Find MIN MAX values in data
    for i in range(N):
        if MAX < data[i]:
            MAX = data[i]
        if MIN > data[i]:
            MIN = data[i]

    # Like MATLAB linspace(MIN, MAX, nsteps);
    x[0] = MIN
    for i in range(1, nsteps):
        x[i] = x[i - 1] + ((MAX - MIN) / nsteps)

    # Kernel density estimation
    c = 1.0 / (np.sqrt(2 * np.pi * sigma**2))
    for i in range(N):
        for j in range(nsteps):
            y[j] = y[j] + 1.0 / N * c * np.exp(-((data[i] - x[j])**2) / (2 * sigma**2))

    # Compilation of the X,Y to result. Good for creating plot(x, y)
    for i in range(nsteps):
        result[i, 0] = x[i]
        result[i, 1] = y[i]
    return result

