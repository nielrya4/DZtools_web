from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from utils import format


def kde_function(data, bandwidth, num_steps=4000, x_min=0, x_max=4000):
    data = format.trim_none(data)
    x = np.linspace(x_min, x_max, num_steps)
    y = np.zeros(num_steps)
    n = len(data)

    for i in range(n):
        kernel_sum = np.zeros(num_steps)
        for s in bandwidth[i]:
            kernel_sum += (1.0 / (np.sqrt(2 * np.pi) * s)) * np.exp(-(x - float(data[i][0])) ** 2 / (2 * float(s) ** 2))

        kernel_sum /= np.sum(kernel_sum)        # Normalize the kernel_sum for the current data point
        y += kernel_sum                         # Add the normalized kernel_sum to the overall y

    y /= np.sum(y)                              # Normalize the final y to make the area under the curve equal to 1
    return x, y


def kde_plot(all_data, stacked=False):
    try:
        if stacked:
            return plot_kde_stacked(all_data)
        else:
            return plot_kde_unido(all_data)

    except ValueError as e:         # If it fails,
        print(f"KDE error: {e}")    # Print to the console for debugging
    return None


def plot_kde_stacked(all_data):
    all_data.reverse()
    subplots = len(all_data)
    x_max = get_x_max(all_data) + get_x_max(all_data)/10
    x_min = get_x_min(all_data) - get_x_max(all_data)/10

    if subplots == 1:        # Check if there's only one subplot, if so, convert it to a list to avoid the issue
        subplots = [1]
        fig, axes = plt.subplots(subplots[0], figsize=(8, 6), dpi=100, squeeze=False)
    else:
        fig, axes = plt.subplots(subplots, figsize=(8, 6), dpi=100, squeeze=False)

    for i, data_set in enumerate(all_data):
        header, data, bandwidth = data_set[0], data_set[1], data_set[2]
        x, y = kde_function(data, bandwidth, x_max=x_max, x_min=x_min)  # Calculate x,y points from data & bandwidth
        if subplots == 1:
            axes[0, 0].plot(x, y, label=header)     # If there's only one subplot, axes will be a 2D numpy array,
            axes[0, 0].legend()                     # so use axes[0] instead of axes[i]
        else:
            axes[i, 0].plot(x, y, label=header)  # Plot on the i-th subplot
            axes[i, 0].legend()  # Make it have a legend

    fig.suptitle(f"Kernel Density Estimate", fontsize=14)  # Add a title to the entire figure
    fig.tight_layout()
    buf = BytesIO()  # Declare a temporary buffer
    fig.savefig(buf, format="svg", bbox_inches="tight")  # Save the figure as SVG
    graph_data = buf.getvalue().decode("utf-8")

    return f"<div>{graph_data}</div>"  # Decode the SVG on the webpage


def plot_kde_unido(all_data):
    all_data.reverse()

    x_max = get_x_max(all_data) + get_x_max(all_data)/10
    x_min = get_x_min(all_data) - get_x_max(all_data)/10

    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)  # Create a figure (fig) containing 1 subplot (ax)

    bandwidth = []

    for i, data_set in enumerate(all_data):
        header, data, bandwidth = data_set[0], data_set[1], data_set[2]
        x, y = kde_function(data, bandwidth, x_max=x_max, x_min=x_min)
        ax.plot(x, y, label=header)

    ax.set_title(f"Kernel Density Estimate (Bandwidth: {bandwidth[0][0]})")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))                          # Move the legend outside the graph

    buf = BytesIO()                                                             # Declare a temporary buffer
    fig.savefig(buf, format="svg", bbox_inches="tight")                         # Save the figure as SVG
    buf.seek(0)
    graph_data = buf.getvalue().decode("utf-8")

    return f"<div>{graph_data}</div>"                                               # Else decode the SVG on the webpage


def get_y_values(all_data):
    all_y_values = []
    try:
        all_data.reverse()
        for i, data_set in enumerate(all_data):
            header, data, sigma = data_set[0], data_set[1], data_set[2]
            x, y = kde_function(data, sigma)
            all_y_values.append(y)
    except ValueError as e:
        print(f"{e}")
    return all_y_values


def get_headers(all_data):
    all_headers = []
    all_data.reverse()
    for i, data_set in enumerate(all_data):
        header = data_set[0]
        all_headers.append(header)
    return all_headers


def get_x_max(all_data):
    data_values = []
    for data_set in all_data:
        data_values += (value for value in data_set[1])
    x_max = np.max(data_values)
    return x_max


def get_x_min(all_data):
    data_values = []
    for data_set in all_data:
        data_values += (value for value in data_set[1])
    x_min = np.min(data_values)
    return x_min


def replace_bandwidth(all_data, bandwidth):
    for i in range(0, len(all_data)):
        for j in range(0, len(all_data[i][2])):
            all_data[i][2][j] = (bandwidth,)
    return all_data
