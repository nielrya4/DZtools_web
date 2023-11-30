from io import BytesIO
from flask import Response, session
from matplotlib.figure import Figure
import pdp


def download_image_from_session(format, filename):
    data = session.get('data', [])
    sigma = session.get('sigma', 1)

    fig = Figure(figsize=(8, 6), dpi=300)
    plt = fig.subplots()
    kde_result = pdp.probability_density_plot(data, sigma)  # Calculate the (x,y) points from our data and uncertainty
    x_values = kde_result[:, 0]  # Separate x and y values
    y_values = kde_result[:, 1]
    plt.plot(x_values, y_values, label='KDE')  # Plot our graph
    plt.legend()

    buf = BytesIO()

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