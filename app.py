import secrets
import os
from io import BytesIO
from utils import downloads, files, pdp
from flask import (Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file)

UPLOAD_FOLDER = 'uploads'                           #Set up some global standards

app = Flask(__name__)                               #Configure the app to use...
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER         #   the upload folder
app.config['SECRET_KEY'] = secrets.token_hex(16)    #   and a new secret key for each session


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/pdp/', methods=['GET', 'POST'])       #Our main loop
def pdp_page():
    graph_data = None                               #Set up a place for our eventual graph data
    similarity_data = None
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
                all_data = files.read_pdp_excel(file)
                session["all_data"] = all_data
                graph_data = pdp.plot_pdp(all_data)
                row_labels = pdp.get_headers(all_data)
                col_labels = pdp.get_headers(all_data)
                col_labels.reverse()
                similarity_data = files.generate_excel_data(pdp.get_y_values(all_data), row_labels=row_labels, col_labels=col_labels)
            except ValueError as e:                 #If it fails,
                flash(str(e))                       #Send an error
                print(f"{e}")
                return redirect(request.url)        #Reload

    return render_template('pdp.html', graph_data=graph_data, similarity_data=similarity_data) #If it passes, add our graph data to index.html


@app.route('/kde/', methods=['GET', 'POST'])       #Our main loop
def kde_page():
    graph_data = None                               #Set up a place for our eventual graph data
    similarity_data = None
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
                all_data = files.read_pdp_excel(file)
                session["all_data"] = all_data
                graph_data = pdp.plot_pdp(all_data)
            except ValueError as e:                 #If it fails,
                flash(str(e))                       #Send an error
                print(f"{e}")
                return redirect(request.url)        #Reload

    return render_template('kde.html', graph_data=graph_data, excel_data=similarity_data) #If it passes, add our graph data to index.html


@app.route('/download_graph', methods=['GET'])                   #Handles when we tell the backend to download something to the user
def download_plot():
    format = request.args.get('format', 'png')

    if format in {'png', 'svg', 'pdf', 'eps'}:
        return downloads.download_image_from_session(format=format, filename=f'plot.{format}')
    else:
        flash('Invalid download format')
        return redirect(url_for('main'))

@app.route('/download_excel')
def download_excel():
    # Replace this with your logic to generate or fetch dynamic data
    # For demonstration purposes, an example of y-value arrays is provided
    y_value_arrays = pdp.get_y_values(session["all_data"])

    # Generate Excel data
    row_labels = pdp.get_headers(session["all_data"])
    row_labels.reverse()
    col_labels = pdp.get_headers(session["all_data"])
    excel_data = files.generate_excel_data(y_value_arrays, row_labels=row_labels, col_labels=col_labels)

    # Create an Excel writer and save the DataFrame to Excel in-memory
    excel_buffer = BytesIO()

    # Determine the desired format from the request
    download_format = request.args.get('format', 'xlsx')

    if download_format == 'xlsx':
        excel_data.to_excel(excel_buffer, index=True, engine='openpyxl', header=True)
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        download_name = 'similarity_scores.xlsx'
    elif download_format == 'xls':
        excel_data.to_excel(excel_buffer, index=True, engine='xlwt', header=True)
        mimetype = 'application/vnd.ms-excel'
        download_name = 'similarity_scores.xls'
    elif download_format == 'csv':
        excel_data.to_csv(excel_buffer, index=True, header=True)
        mimetype = 'text/csv'
        download_name = 'similarity_scores.csv'
    else:
        return "Invalid format specified", 400

    excel_buffer.seek(0)

    # Serve the in-memory Excel file for download
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=download_name,
        mimetype=mimetype
    )

@app.route('/DZ.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/DZ.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':                                      #If we are the program being called,
    app.run(port=8000, debug=True)                              #Then run on port 8000 in debugging mode.
