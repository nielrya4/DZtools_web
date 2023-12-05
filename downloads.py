from io import BytesIO
from flask import Response, session
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pdp


def download_image_from_session(format, filename):
    all_data = session.get('all_data', [])
    #all_data.reverse()
    graph_data = ""
    buf = BytesIO()
    mimetype=""
    subplots = len(all_data)
    fig, axes = plt.subplots(subplots, figsize=(8, 6), dpi=100)  # Create subplots

    for i, data_set in enumerate(all_data):
        header, data, sigma = data_set[0], data_set[1], data_set[2]
        x, y = pdp.probability_density_plot(data, sigma)  # Calculate the (x,y) points from our data and uncertainty
        axes[i].plot(x, y, label=header)  # Plot on the i-th subplot
        axes[i].legend()  # Make it have a legend

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