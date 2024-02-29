from flask import render_template, session
import os
from lib.objects.documents import SampleSheet
from lib.utils import unmixing_utils
import app as APP


def register(app):
    @app.route('/mix/')
    def dz_mix():
        results = render_template('dz_mix/mix.html')
        last_uploaded_file = session.get("last_uploaded_file")
        if last_uploaded_file:
            file = os.path.join(APP.UPLOAD_FOLDER, last_uploaded_file)
            sample_sheet = SampleSheet(file)
            samples = sample_sheet.read_samples()

            data1, data2, data3 = unmixing_utils.do_monte_carlo(samples, num_trials=10000)
            results = render_template('dz_mix/mix.html',
                                      data1=data1)
        return results

    @app.route('/unmix')
    def unmix():
        pass

