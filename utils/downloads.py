from io import BytesIO
from flask import Response, request, flash, redirect, url_for
import matplotlib.pyplot as plt
import numpy as np
from utils import pdp, kde

def download_plot(all_data, plot_type):
    format = request.args.get('format', 'png')

    if format in {'png', 'svg', 'pdf', 'eps'}:
        if plot_type == 'pdp':
            return download_pdp_from_data(all_data=all_data, format=format, filename=f'plot.{format}')
        elif plot_type == 'kde':
            return download_kde_from_data(all_data=all_data, format=format, filename=f'plot.{format}')
        elif plot_type == 'cdf':
            return download_cdf_from_data(all_data=all_data, format=format, filename=f'plot.{format}')
        else:
            flash('Invalid plot type')
    else:
        flash('Invalid download format')

    return redirect(url_for('main'))



def download_pdp_from_data(all_data, format, filename):
    buf = BytesIO()
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
        x, y = pdp.pdp_function(data, sigma)  # Calculate the (x,y) points from our data and uncertainty

        if subplots == 1:
            axes[0, 0].plot(x, y, label=header)
            axes[0, 0].legend()
        else:
            axes[i, 0].plot(x, y, label=header)  # Plot on the i-th subplot
            axes[i, 0].legend()  # Make it have a legend
    if format == 'pdf':
        fig.savefig(buf, format='pdf', bbox_inches="tight")
        mimetype = 'application/pdf'
    elif format == 'eps':
        fig.savefig(buf, format='eps', bbox_inches="tight")
        mimetype = 'application/postscript'
    else:  # Handle other formats like 'png' and 'svg'
        fig.savefig(buf, format=format, bbox_inches="tight")
        mimetype = f'image/{format}'

    buf.seek(0)
    return Response(buf, mimetype=mimetype, headers={'Content-Disposition': f'attachment;filename={filename}'})


def download_kde_from_data(all_data, format, filename):
    buf = BytesIO()
    subplots = len(all_data)
    all_data.reverse()
    subplots = len(all_data)
    # Check if there's only one subplot, if so, convert it to a list to avoid the issue
    if subplots == 1:
        subplots = [1]
        fig, ax = plt.subplots(subplots[0], figsize=(8, 6), dpi=100)  # Create a single subplot
    else:
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)  # Create a single subplot
    # Plot all lines on the same subplot
    sigma = []
    for i, data_set in enumerate(all_data):
        header, data, sigma = data_set[0], data_set[1], data_set[2]
        x, y = kde.kde_function(data, sigma)  # Calculate the (x,y) points from our data and uncertainty
        ax.plot(x, y, label=header)

    # Add title and labels

    ax.set_title(f"Kernel Density Estimate ({sigma[0][0]}σ)")

    # Move the legend outside of the graph
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    if format == 'pdf':
        fig.savefig(buf, format='pdf', bbox_inches="tight")
        mimetype = 'application/pdf'
    elif format == 'eps':
        fig.savefig(buf, format='eps', bbox_inches="tight")
        mimetype = 'application/postscript'
    else:  # Handle other formats like 'png' and 'svg'
        fig.savefig(buf, format=format, bbox_inches="tight")
        mimetype = f'image/{format}'

    buf.seek(0)
    return Response(buf, mimetype=mimetype, headers={'Content-Disposition': f'attachment;filename={filename}'})


def download_cdf_from_data(all_data, format, filename, nsteps=1000):
    buf = BytesIO()
    subplots = len(all_data)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

    for i, data_set in enumerate(all_data):
        header, data = data_set[0], data_set[1]
        # Check if there are any valid values left
        if not data:
            print(f"No valid data for {header}")
            continue

        count, bins_count = np.histogram(data, bins=nsteps, density=True)
        pdf = count / sum(count)
        cdf_values = np.cumsum(pdf)
        ax.plot(bins_count[1:], cdf_values, label=header)

    # Add title and labels
    ax.set_title("Cumulative Distribution Function")

    # Move the legend outside of the graph
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    if format == 'pdf':
        fig.savefig(buf, format='pdf', bbox_inches="tight")
        mimetype = 'application/pdf'
    elif format == 'eps':
        fig.savefig(buf, format='eps', bbox_inches="tight")
        mimetype = 'application/postscript'
    else:  # Handle other formats like 'png' and 'svg'
        fig.savefig(buf, format=format, bbox_inches="tight")
        mimetype = f'image/{format}'

    buf.seek(0)
    return Response(buf, mimetype=mimetype, headers={'Content-Disposition': f'attachment;filename={filename}'})


