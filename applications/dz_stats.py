from utils import files, kde, cdf
from flask import render_template, request, session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

import app
import os


def run(args=""):           # Not even close to being finished. This is for terminal-like functionality
    filename = ""
    all_data = ""

    kde_graph = False
    kde_stacked = False
    kde_bandwidth = 10
    cdf_graph = False
    similarity_matrix = False
    likeness_matrix = False
    ks_matrix = False
    kuiper_matrix = False
    cross_correlation_matrix = False

    if args != "":
        for arg in args.split("-"):
            arg = arg.strip()
            print(arg)
            if arg.startswith("i "):
                filename = arg.split("i ")[1].strip()
                if os.path.exists(filename):
                    session_key = session.get('SECRET_KEY', app.SECRET_KEY)
                    with open(filename, 'rb') as file:
                        file_storage = FileStorage(file, filename=secure_filename(file.name))
                        uploaded_file = files.upload_file(file_storage, session_key)

                    session['last_uploaded_file'] = os.path.basename(uploaded_file)
                    all_data = files.read_excel(uploaded_file)
                    all_data = kde.replace_bandwidth(all_data, bandwidth=kde_bandwidth)
                    all_data.reverse()
                else:
                    return render_template(template_name_or_list="cmd.html",
                                           output=request.form.get("output", 0) + "File not found\n")

            elif arg == "kde":
                kde_graph = True
            elif arg == "stacked":
                kde_stacked = True
            elif arg.startswith("bandwidth "):
                kde_bandwidth = int(arg.split("bandwidth ")[1])
            elif arg == "cdf":
                cdf_graph = True
            elif arg == "similarity":
                similarity_matrix = True
            elif arg == "likeness":
                likeness_matrix = True
            elif arg == "ks":
                ks_matrix = True
            elif arg == "kuiper":
                kuiper_matrix = True
            elif arg == "cross_correlation":
                cross_correlation_matrix = True

        return display(all_data=all_data,
                       kde_graph=kde_graph,
                       kde_stacked=kde_stacked,
                       kde_bandwidth=kde_bandwidth,
                       cdf_graph=cdf_graph,
                       similarity_matrix=similarity_matrix,
                       likeness_matrix=likeness_matrix,
                       ks_matrix=ks_matrix,
                       kuiper_matrix=kuiper_matrix,
                       cross_correlation_matrix=cross_correlation_matrix)


def display(all_data, kde_graph, kde_stacked, cdf_graph, similarity_matrix, likeness_matrix, ks_matrix, kuiper_matrix, cross_correlation_matrix, kde_bandwidth=10):
    kde_bandwidth = request.form.get("kde_bandwidth", kde_bandwidth)
    graph_data = kde.kde_plot(all_data, stacked=kde_stacked) if kde_graph else None
    cdf_data = cdf.plot_cdf(all_data) if cdf_graph else None

    row_labels = kde.get_headers(all_data)
    col_labels = kde.get_headers(all_data)
    col_labels.reverse()

    y_values = kde.get_y_values(all_data)

    if similarity_matrix:
        similarity_data = files.generate_matrix(y_values,
                                                row_labels=row_labels,
                                                col_labels=col_labels,
                                                matrix_type="similarity")
    else:
        similarity_data = None

    if likeness_matrix:
        likeness_data = files.generate_matrix(y_values,
                                              row_labels=row_labels,
                                              col_labels=col_labels,
                                              matrix_type="likeness")
    else:
        likeness_data = None

    if ks_matrix:
        ks_data = files.generate_matrix(y_values,
                                        row_labels=row_labels,
                                        col_labels=col_labels,
                                        matrix_type="ks")
    else:
        ks_data = None

    if kuiper_matrix:
        kuiper_data = files.generate_matrix(y_values,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="kuiper")
    else:
        kuiper_data = None

    if cross_correlation_matrix:
        cross_correlation_data = files.generate_matrix(y_values,
                                                       row_labels=row_labels,
                                                       col_labels=col_labels,
                                                       matrix_type="cross_correlation")
    else:
        cross_correlation_data = None

    return render_template('dz_stats.html',
                           graph_data=graph_data,
                           kde_bandwidth=kde_bandwidth,
                           kde_stacked=kde_stacked,
                           cdf_data=cdf_data,
                           similarity_data=similarity_data,
                           likeness_data=likeness_data,
                           ks_data=ks_data,
                           kuiper_data=kuiper_data,
                           cross_correlation_data=cross_correlation_data,
                           kde_graph=kde_graph,
                           cdf_graph=cdf_graph,
                           similarity_matrix=similarity_matrix,
                           likeness_matrix=likeness_matrix,
                           ks_matrix=ks_matrix,
                           kuiper_matrix=kuiper_matrix,
                           cross_correlation_matrix=cross_correlation_matrix)
