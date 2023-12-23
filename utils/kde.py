from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from utils import format
from flask import (request, redirect)


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


def kernel_density_estimate(data, bandwidth, num_steps=4000, x_min=0, x_max=4000):
    data = format.trim_none(data)
    x = np.linspace(x_min, x_max, num_steps)
    y = np.zeros(num_steps)
    n = len(data)

    for i in range(n):
        kernel_sum = np.zeros(num_steps)
        for s in bandwidth[i]:
            kernel_sum += (1.0 / (np.sqrt(2 * np.pi) * s)) * np.exp(-(x - float(data[i][0])) ** 2 / (2 * float(s) ** 2))

        # Normalize the kernel_sum for the current data point
        kernel_sum /= np.sum(kernel_sum)
        # Add the normalized kernel_sum to the overall y
        y += kernel_sum

    # Normalize the final y to make the area under the curve equal to 1
    y /= np.sum(y)
    return x, y


def plot_kde(all_data):
    try:
        all_data.reverse()
        subplots = len(all_data)
        x_max = get_x_max(all_data)
        x_min = get_x_min(all_data)
        # Check if there's only one subplot, if so, convert it to a list to avoid the issue
        if subplots == 1:
            subplots = [1]
            fig, axes = plt.subplots(subplots[0], figsize=(8, 6), dpi=100, squeeze=False)  # Create subplots
        else:
            fig, axes = plt.subplots(subplots, figsize=(8, 6), dpi=100, squeeze=False)  # Create subplots

        # If there's only one subplot, axes will be a 2D numpy array, so use axes[0] instead of axes[i]
        for i, data_set in enumerate(all_data):
            header, data, sigma = data_set[0], data_set[1], data_set[2]
            x, y = kernel_density_estimate(data, sigma, x_max=x_max, x_min=x_min)  # Calculate the (x,y) points from our data and uncertainty

            if subplots == 1:
                axes[0, 0].plot(x, y, label=header)
                axes[0, 0].legend()
            else:
                axes[i, 0].plot(x, y, label=header)  # Plot on the i-th subplot
                axes[i, 0].legend()  # Make it have a legend
        buf = BytesIO()  # Declare a temporary buffer
        fig.savefig(buf, format="svg", bbox_inches="tight")  # Save the figure as SVG
        graph_data = buf.getvalue().decode("utf-8")
    except ValueError as e:  # If it fails,
        print(f"{e}")
        return redirect(request.url)  # Reload
    return f"<div>{graph_data}</div>"  # Decode the SVG on the webpage


def plot_kde_unido(all_data):
    try:
        all_data.reverse()
        subplots = len(all_data)

        x_max = get_x_max(all_data) + get_x_max(all_data)/10
        x_min = get_x_min(all_data) - get_x_max(all_data)/10

        # Check if there's only one subplot, if so, convert it to a list to avoid the issue
        if subplots == 1:
            subplots = [1]
            fig, ax = plt.subplots(subplots[0], figsize=(8, 6), dpi=100)  # Create a single subplot
        else:
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)  # Create a single subplot
        sigma = []
        # Plot all lines on the same subplot
        for i, data_set in enumerate(all_data):
            header, data, sigma = data_set[0], data_set[1], data_set[2]
            x, y = kernel_density_estimate(data, sigma, x_max=x_max, x_min=x_min)  # Calculate the (x,y) points from our data and uncertainty
            ax.plot(x, y, label=header)

        # Add title and labels
        ax.set_title(f"Kernel Density Estimate (Bandwidth: {sigma[0][0]})")

        # Move the legend outside of the graph
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        buf = BytesIO()  # Declare a temporary buffer
        fig.savefig(buf, format="svg", bbox_inches="tight")  # Save the figure as SVG
        buf.seek(0)
        graph_data = buf.getvalue().decode("utf-8")

    except ValueError as e:  # If it fails,
        print(f"KDE error: {e}")
        return None  # Handle the exception as needed

    return f"<div>{graph_data}</div>"  # Decode the SVG on the webpage


def get_y_values(all_data):
    all_y_values = []
    try:
        all_data.reverse()
        for i, data_set in enumerate(all_data):
            header, data, sigma = data_set[0], data_set[1], data_set[2]
            x, y = kernel_density_estimate(data, sigma)  # Calculate the (x,y) points from our data and uncertainty
            all_y_values.append(y)
    except ValueError as e:  # If it fails,
        print(f"{e}")
    return all_y_values


def get_headers(all_data):
    all_headers = []
    all_data.reverse()
    for i, data_set in enumerate(all_data):
        header = data_set[0]
        all_headers.append(header)
    return all_headers
