# pdp.py
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


def probability_density_plot(data, sigma, nsteps=1000):
    x = np.linspace((min(min(row) for row in data)) - (2 * max(max(row) for row in sigma)),
                    (max(max(row) for row in data)) + (2 * max(max(row) for row in sigma)),
                    nsteps)
    y = np.zeros(nsteps)
    N = len(data)

    if not isinstance(sigma[0], (list, tuple, np.ndarray)):
        sigma = [sigma] * len(data)

    for i in range(N):
        for s in sigma[i]:
            y = (y + 1.0 / N *
                 (1.0 / (np.sqrt(2 * np.pi) * s)) *
                 np.exp(-(x - float(data[i][0])) ** 2 / (2 * float(s) ** 2)))
    return x, y


def plot_pdp(all_data):
    all_data.reverse()
    subplots = len(all_data)
    fig, axes = plt.subplots(subplots, figsize=(8, 6), dpi=100)  # Create subplots

    for i, data_set in enumerate(all_data):
        header, data, sigma = data_set[0], data_set[1], data_set[2]
        x, y = probability_density_plot(data, sigma)  # Calculate the (x,y) points from our data and uncertainty
        axes[i].plot(x, y, label=header)  # Plot on the i-th subplot
        axes[i].legend()  # Make it have a legend

    buf = BytesIO()  # Declare a temporary buffer
    fig.savefig(buf, format="svg", bbox_inches="tight")  # Save the figure as SVG
    data = buf.getvalue().decode("utf-8")
    return f"<div>{data}</div>"  # Decode the SVG on the webpage

