import os
from flask import render_template, request, session, flash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from utils import files, kde_utils
import app as APP
from objects.documents import SampleSheet
from objects.graphs import KDE, CDF, PDP, MDS


def register(app):
    @app.route('/dz_stats/', methods=['GET', 'POST'])
    def dz_stats():
        # Set defaults to render the page
        results = render_template("dz_stats/dz_stats.html",
                                  kde_bandwidth=10,
                                  kde_graph=True,
                                  cdf_graph=True)

        try:
            kde_bandwidth = int(request.form.get('kde_bandwidth', 10))
            kde_stacked = request.form.get('kde_stacked') == "true"

            session["kde_bandwidth"] = kde_bandwidth
            session["kde_stacked"] = kde_stacked

            kde_graph = request.form.get('kde_graph') == "true"
            pdp_graph = request.form.get('pdp_graph') == "true"
            cdf_graph = request.form.get('cdf_graph') == "true"
            mds_graph = request.form.get('mds_graph') == "true"

            similarity_matrix = request.form.get('similarity_matrix') == "true"
            dissimilarity_matrix = request.form.get('dissimilarity_matrix') == "true"
            likeness_matrix = request.form.get('likeness_matrix') == "true"
            ks_matrix = request.form.get('ks_matrix') == "true"
            kuiper_matrix = request.form.get('kuiper_matrix') == "true"
            cross_correlation_matrix = request.form.get('cross_correlation_matrix') == "true"

            if session.get("last_uploaded_file") is not None:
                last_uploaded_file = session.get("last_uploaded_file")
                file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
                sample_sheet = SampleSheet(file)
                samples = sample_sheet.read_samples()
                # samples.append(sample_sheet.create_mixed_sample()) # TODO: Add mixed sample functionality
                session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
                filename = f"{session_key}all_data.pkl"
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(samples, filepath)
                results = display(samples,
                                  kde_graph=kde_graph,
                                  kde_stacked=kde_stacked,
                                  pdp_graph=pdp_graph,
                                  cdf_graph=cdf_graph,
                                  mds_graph=mds_graph,
                                  similarity_matrix=similarity_matrix,
                                  dissimilarity_matrix=dissimilarity_matrix,
                                  likeness_matrix=likeness_matrix,
                                  ks_matrix=ks_matrix,
                                  kuiper_matrix=kuiper_matrix,
                                  cross_correlation_matrix=cross_correlation_matrix)
        except ValueError as e:
            flash(str(e))
            print(f"{e}")
        return results


def run(args=""):           # Not even close to being finished. This is for terminal-like functionality
    all_data = ""

    kde_graph = False
    kde_stacked = False
    kde_bandwidth = 10
    pdp_graph = False
    cdf_graph = False
    mds_graph = False
    similarity_matrix = False
    dissimilarity_matrix = False
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
                    session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
                    with open(filename, 'rb') as file:
                        file_storage = FileStorage(file, filename=secure_filename(file.name))
                        uploaded_file = files.upload_file(file_storage, session_key)

                    session['last_uploaded_file'] = os.path.basename(uploaded_file)
                    all_data = files.read_excel(uploaded_file)
                    all_data = (kde_utils.replace_bandwidth(all_data, bandwidth=kde_bandwidth))
                    all_data.reverse()
                else:
                    return render_template(template_name_or_list="dz_cmd/dz_cmd.html",
                                           output=request.form.get("output", 0) + "File not found\n")

            elif arg == "kde":
                kde_graph = True
            elif arg == "stacked":
                kde_stacked = True
            elif arg.startswith("bandwidth "):
                kde_bandwidth = int(arg.split("bandwidth ")[1])
            elif arg == "pdp":
                pdp_graph = True
            elif arg == "cdf":
                cdf_graph = True
            elif arg == "mds":
                mds_graph = True
            elif arg == "similarity":
                similarity_matrix = True
            elif arg == "dissimilarity":
                dissimilarity_matrix = True
            elif arg == "likeness":
                likeness_matrix = True
            elif arg == "ks":
                ks_matrix = True
            elif arg == "kuiper":
                kuiper_matrix = True
            elif arg == "cross_correlation":
                cross_correlation_matrix = True

        return display(samples=all_data,
                       kde_graph=kde_graph,
                       kde_stacked=kde_stacked,
                       kde_bandwidth=kde_bandwidth,
                       pdp_graph=pdp_graph,
                       cdf_graph=cdf_graph,
                       mds_graph=mds_graph,
                       dissimilarity_matrix=dissimilarity_matrix,
                       similarity_matrix=similarity_matrix,
                       likeness_matrix=likeness_matrix,
                       ks_matrix=ks_matrix,
                       kuiper_matrix=kuiper_matrix,
                       cross_correlation_matrix=cross_correlation_matrix)


def display(samples, kde_graph, kde_stacked, pdp_graph, cdf_graph, mds_graph, similarity_matrix, dissimilarity_matrix, likeness_matrix, ks_matrix, kuiper_matrix, cross_correlation_matrix, kde_bandwidth=10):
    pdp_data = PDP(samples, title=f"Probability Density Plot", stacked=False).plot() if pdp_graph else None
    cdf_data = CDF(samples, "Cumulative Density Function").plot() if cdf_graph else None
    mds_data = MDS(samples, title=f"Multidimensional Scaling Plot").plot() if mds_graph else None
    # Replace uncertainties with our custom bandwidth
    kde_bandwidth = session.get("kde_bandwidth", kde_bandwidth)
    for sample in samples:
        sample.replace_bandwidth(kde_bandwidth)
    graph_data = KDE(samples, f"Kernel Density Estimate (Bandwidth: {kde_bandwidth})", stacked=kde_stacked).plot() if kde_graph else None

    row_labels = [sample.name for sample in samples]
    col_labels = [sample.name for sample in samples]
    # It's worth noting here that the likeness, similarity, dissimilarity, and cross-correlation matrices will run
    # off of the bandwidth used for the KDE plot. TODO: Toggle PDP mode OR KDE mode and form the matrices appropriately.
    # TODO: Implement relative source contribution matrices
    if similarity_matrix:
        similarity_data = files.generate_matrix(samples,
                                                row_labels=row_labels,
                                                col_labels=col_labels,
                                                matrix_type="similarity")
    else:
        similarity_data = None

    if dissimilarity_matrix:
        dissimilarity_data = files.generate_matrix(samples,
                                                row_labels=row_labels,
                                                col_labels=col_labels,
                                                matrix_type="dissimilarity")
    else:
        dissimilarity_data = None

    if likeness_matrix:
        likeness_data = files.generate_matrix(samples,
                                              row_labels=row_labels,
                                              col_labels=col_labels,
                                              matrix_type="likeness")
    else:
        likeness_data = None

    if ks_matrix:
        ks_data = files.generate_matrix(samples,
                                        row_labels=row_labels,
                                        col_labels=col_labels,
                                        matrix_type="ks")
    else:
        ks_data = None

    if kuiper_matrix:
        kuiper_data = files.generate_matrix(samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="kuiper")
    else:
        kuiper_data = None

    if cross_correlation_matrix:
        cross_correlation_data = files.generate_matrix(samples,
                                                       row_labels=row_labels,
                                                       col_labels=col_labels,
                                                       matrix_type="cross_correlation")
    else:
        cross_correlation_data = None

    return render_template('dz_stats/dz_stats.html',
                           graph_data=graph_data,
                           kde_bandwidth=kde_bandwidth,
                           kde_stacked=kde_stacked,
                           pdp_data=pdp_data,
                           cdf_data=cdf_data,
                           mds_data=mds_data,
                           similarity_data=similarity_data,
                           dissimilarity_data=dissimilarity_data,
                           likeness_data=likeness_data,
                           ks_data=ks_data,
                           kuiper_data=kuiper_data,
                           cross_correlation_data=cross_correlation_data,
                           kde_graph=kde_graph,
                           pdp_graph=pdp_graph,
                           cdf_graph=cdf_graph,
                           mds_graph=mds_graph,
                           similarity_matrix=similarity_matrix,
                           dissimilarity_matrix=dissimilarity_matrix,
                           likeness_matrix=likeness_matrix,
                           ks_matrix=ks_matrix,
                           kuiper_matrix=kuiper_matrix,
                           cross_correlation_matrix=cross_correlation_matrix)
