import os
from flask import render_template, request, session, flash
from utils import files, kde
from applications import stats
import app as APP


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
            kde_graph = request.form.get('kde_graph') == "true"
            cdf_graph = request.form.get('cdf_graph') == "true"

            similarity_matrix = request.form.get('similarity_matrix') == "true"
            likeness_matrix = request.form.get('likeness_matrix') == "true"
            ks_matrix = request.form.get('ks_matrix') == "true"
            kuiper_matrix = request.form.get('kuiper_matrix') == "true"
            cross_correlation_matrix = request.form.get('cross_correlation_matrix') == "true"

            if session.get("last_uploaded_file") is not None:
                last_uploaded_file = session.get("last_uploaded_file")
                file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)

                all_data = files.read_excel(file)
                all_data = kde.replace_bandwidth(all_data, bandwidth=kde_bandwidth)
                all_data.reverse()

                # Save data to the file system
                session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
                filename = f"{session_key}all_data.pkl"
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(all_data, filepath)

                results = stats.display(all_data,
                                        kde_graph=kde_graph,
                                        kde_stacked=kde_stacked,
                                        cdf_graph=cdf_graph,
                                        similarity_matrix=similarity_matrix,
                                        likeness_matrix=likeness_matrix,
                                        ks_matrix=ks_matrix,
                                        kuiper_matrix=kuiper_matrix,
                                        cross_correlation_matrix=cross_correlation_matrix)
        except ValueError as e:
            flash(str(e))
            print(f"{e}")

        return results
