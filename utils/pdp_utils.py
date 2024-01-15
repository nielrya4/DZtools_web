from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from flask import (request, redirect)


def pdp_function(sample, num_steps=4000, x_min=0, x_max=4000):
    x = np.linspace(x_min, x_max, num_steps)
    y = np.zeros_like(x)
    ages = [grain.age for grain in sample.grains]
    bandwidths = [grain.uncertainty for grain in sample.grains]
    for i in range(len(ages)):
        kernel_sum = np.zeros(num_steps)
        s = bandwidths[i]
        kernel_sum += (1.0 / (np.sqrt(2 * np.pi) * s)) * np.exp(-(x - float(ages[i])) ** 2 / (2 * float(s) ** 2))
        y += kernel_sum
    y /= np.sum(y)
    return x, y


def plot_pdp(all_data):
    try:
        all_data.reverse()
        subplots = len(all_data)

        # Check if there's only one subplot, if so, convert it to a list to avoid the issue
        if subplots == 1:
            subplots = [1]
            fig, axes = plt.subplots(subplots[0], figsize=(8, 6), dpi=100, squeeze=False)  # Create subplots
        else:
            fig, axes = plt.subplots(subplots, figsize=(8, 6), dpi=100, squeeze=False)  # Create subplots

        # If there's only one subplot, axes will be a 2D numpy array, so use axes[0] instead of axes[i]
        for i, data_set in enumerate(all_data):
            header, data, sigma = data_set[0], data_set[1], data_set[2]
            x, y = pdp_function(data, sigma)  # Calculate the (x,y) points from our data and uncertainty

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


def get_y_values(all_data):
    all_y_values = []
    try:
        all_data.reverse()
        for i, data_set in enumerate(all_data):
            header, data, sigma = data_set[0], data_set[1], data_set[2]
            x, y = pdp_function(data, sigma)  # Calculate the (x,y) points from our data and uncertainty
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
