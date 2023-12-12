from io import BytesIO
from flask import Response, session
import matplotlib.pyplot as plt
from utils import pdp


def download_image_from_session(format, filename):
    all_data = session.get('all_data', [])

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
        x, y = pdp.probability_density_plot(data, sigma)  # Calculate the (x,y) points from our data and uncertainty

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