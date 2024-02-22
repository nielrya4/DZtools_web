import os
import secrets
from utils import cleanup, routes
from flask import Flask, render_template


UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
SECRET_KEY = secrets.token_hex(16)
app.config['SECRET_KEY'] = SECRET_KEY
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

routes.register(app)
cleanup.start_cleanup()


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/home/')
def main2():
    return render_template('new_interface/new_interface.html')


if __name__ == '__main__':
    cleanup.cleanup_job()
    app.run(port=8000, debug=True)
