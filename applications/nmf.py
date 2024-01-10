import app
from flask import render_template


def run(args=""):
    return


def display(all_data, als_graph, fs_graph, rs_graph, fr_graph, ssr_graph, test_matrix, kde_bandwidth=10):
    return render_template("dz_nmf/dz_nmf.html",
                           kde_bandwidth=10,
                           als_graph=True,
                           fs_graph=True)
