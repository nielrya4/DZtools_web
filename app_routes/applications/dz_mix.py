import os
from flask import render_template, request, session, flash
from utils import files, kde_utils
import app as APP


def register(app):
    @app.route('/dz_mix/', methods=['GET', 'POST'])
    def dz_mix():
        # Set defaults to render the page
        results = render_template("dz_mix/dz_mix.html",
                                  kde_bandwidth=10,
                                  als_graph=True,
                                  fs_graph=True)

        try:
            kde_bandwidth = int(request.form.get('kde_bandwidth', 10))
            als_graph = request.form.get('als_graph') == "true"
            fs_graph = request.form.get('fs_graph') == "true"
            rs_graph = request.form.get('rs_graph') == "true"
            fr_graph = request.form.get('fr_graph') == "true"
            ssr_graph = request.form.get('ssr_graph') == "true"
            test_matrix = request.form.get('test_matrix') == "true"

            if session.get("last_uploaded_file") is not None:
                last_uploaded_file = session.get("last_uploaded_file")
                file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)

                all_data = files.read_excel(file)
                all_data = kde_utils.replace_bandwidth(all_data, bandwidth=kde_bandwidth)
                all_data.reverse()

                # Save data to the file system
                session_key = session.get('SECRET_KEY', APP.SECRET_KEY)
                filename = f"{session_key}all_data.pkl"
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                files.save_data_to_file(all_data, filepath)
                results = display(all_data,
                                      als_graph=als_graph,
                                      fs_graph=fs_graph,
                                      rs_graph=rs_graph,
                                      fr_graph=fr_graph,
                                      ssr_graph=ssr_graph,
                                      test_matrix=test_matrix,
                                      kde_bandwidth=kde_bandwidth)
        except ValueError as e:
            flash(str(e))
            print(f"DZnmf Error: {e}")

        return results


def run(args=""):
    return


def display(all_data, als_graph, fs_graph, rs_graph, fr_graph, ssr_graph, test_matrix, kde_bandwidth=10):
    return render_template("dz_mix/dz_mix.html",
                           kde_bandwidth=10,
                           als_graph=True,
                           fs_graph=True)
