import openpyxl
import numpy as np
import secrets
import pdp
import downloads
import files
from flask import (Flask, render_template, request, redirect, url_for, flash, Response, session)


UPLOAD_FOLDER = 'uploads'                           #Set up some global standards



app = Flask(__name__)                               #Configure the app to use...
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER         #   the upload folder
app.config['SECRET_KEY'] = secrets.token_hex(16)    #   and a new secret key for each session


@app.route('/', methods=['GET', 'POST'])       #Our main loop
def main():
    graph_data = None                               #Set up a place for our eventual graph data

    if request.method == 'POST':                    #If the front end sends us information...
        if 'file' not in request.files:             #Check if it sent us a file
            flash('No file part')                   #If not, say so.
            return redirect(request.url)            #Reload

        file = request.files['file']                #Otherwise, set file equal to all the files uploaded

        if file.filename == '':                     #If the filename is blank,
            flash('No selected file')               #Say so
            return redirect(request.url)            #And reload

        if file and files.allowed_file(file.filename):    #If we got a file AND it is allowed,
            try:                                    #Let's try to...
                data, sigma = files.read_excel(file)      #Read the excell file into data and sigma (uncertainty)
                session['data'] = data              #Store data in the session
                session['sigma'] = sigma            #Store sigma in the session
                graph_data = pdp.plot_pdp(data, sigma)   #Get our x and y coordinates and store them in graph_data
            except ValueError as e:                 #If it fails,
                flash(str(e))                       #Send an error
                return redirect(request.url)        #Reload

    return render_template('index.html', graph_data=graph_data) #If it passes, add our graph data to index.html






@app.route('/download', methods=['GET'])                   #Handles when we tell the backend to download something to the user
def download_plot():
    format = request.args.get('format', 'png')

    if format in {'png', 'svg', 'pdf', 'eps'}:
        return downloads.download_image_from_session(format=format, filename=f'plot.{format}')
    else:
        flash('Invalid download format')
        return redirect(url_for('main'))



if __name__ == '__main__':                                      #If we are the program being called,
    app.run(port=8000, debug=True)                              #Then run on port 8000 in debugging mode.
