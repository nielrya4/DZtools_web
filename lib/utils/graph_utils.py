import os.path
from io import BytesIO
from flask import Response, url_for
import matplotlib.pyplot as plt

import app


def download_graph(fig, file_name, file_format):
    image_buffer = BytesIO()
    if file_format == 'pdf':
        fig.savefig(image_buffer, format='pdf', bbox_inches="tight")
        mimetype = 'application/pdf'
    elif file_format == 'eps':
        fig.savefig(image_buffer, format='eps', bbox_inches="tight")
        mimetype = 'application/postscript'
    else:  # Handle other formats like 'png' and 'svg'
        fig.savefig(image_buffer, format=file_format, bbox_inches="tight")
        mimetype = f'image/{file_format}'
    image_buffer.seek(0)
    plt.close(fig)
    return Response(image_buffer,
                    mimetype=mimetype,
                    headers={'Content-Disposition': f'attachment;filename={file_name}'})


def plot_graph(fig, filename="graph"):
    image_buffer = BytesIO()
    fig.savefig(image_buffer, format="svg", bbox_inches="tight")
    fig.savefig(os.path.join(app.UPLOAD_FOLDER, filename + ".svg"), format="svg", bbox_inches="tight")
    image_buffer.seek(0)
    plotted_kde = image_buffer.getvalue().decode("utf-8")
    plt.close(fig)
    return f"<div>{plotted_kde}<br /><h6>Download Graph (<a href='/uploads/{filename}.svg' download>{filename}.svg</a>)</h6></div>"


def get_x_max(samples):
    x_max = 0
    for sample in samples:
        for grain in sample.grains:
            if grain.age + grain.uncertainty > x_max:
                x_max = grain.age + grain.uncertainty
    return x_max


def get_x_min(samples):
    x_min = 0
    for sample in samples:
        for grain in sample.grains:
            if grain.age - grain.uncertainty < x_min:
                x_min = grain.age - grain.uncertainty
    return x_min


def get_sample_names(samples):
    all_names = []
    for sample in samples:
        name = sample.name
        all_names.append(name)
    return all_names
