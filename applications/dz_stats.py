from utils import files, kde, cdf
from flask import render_template, request


def run(args=""):
    for arg in args.rsplit("-"):
        arg.strip()
        if arg.startswith("i "):
            print(None)


def display(all_data, kde_graph, kde_stacked, cdf_graph, similarity_matrix, likeness_matrix, ks_matrix, kuiper_matrix, cross_correlation_matrix):
    kde_bandwidth = request.form.get("kde_bandwidth", 10)
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
