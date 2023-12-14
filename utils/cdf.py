from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from utils import format
from flask import (Flask, render_template, request, redirect, url_for, flash, Response, session)

import utils.format


def plot_cdf(all_data, nsteps=1000):
    try:
        # Set the image size and DPI
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

        for i, data_set in enumerate(all_data):
            header, data = data_set[0], data_set[1]

            filtered_data = format.trim_none(data)

            # Check if there are any valid values left
            if not filtered_data:
                print(f"No valid data for {header}")
                continue

            count, bins_count = np.histogram(filtered_data, bins=nsteps, density=True)
            pdf = count / sum(count)
            cdf_values = np.cumsum(pdf)
            ax.plot(bins_count[1:], cdf_values, label=header)

        # Add title and labels
        ax.set_title("Cumulative Distribution Function (CDF)")

        # Move the legend outside of the graph
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Save the plot as SVG in a buffer
        buf = BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        buf.seek(0)
        graph_data = buf.getvalue().decode("utf-8")

    except ValueError as e:
        print(f"{e}")
        # Handle the exception as needed
        return None
    return f"<div>{graph_data}</div>"