import openpyxl
import numpy as np
import secrets
from io import BytesIO
from matplotlib.figure import Figure
from flask import (Flask, render_template, request, redirect, url_for, flash, Response, session)


UPLOAD_FOLDER = 'uploads'                           #Set up some global standards
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}                #Only accept xlsx and xls files


app = Flask(__name__)                               #Configure the app to use...
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER         #   the upload folder
app.config['SECRET_KEY'] = secrets.token_hex(16)    #   and a new secret key for each session


@app.route('/', methods=['GET', 'POST'])            #Our main loop
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

        if file and allowed_file(file.filename):    #If we got a file AND it is allowed,
            try:                                    #Let's try to...
                data, sigma = read_excel(file)      #Read the excell file into data and sigma (uncertainty)
                session['data'] = data              #Store data in the session
                session['sigma'] = sigma            #Store sigma in the session
                graph_data = plotKDE(data, sigma)   #Get our x and y coordinates and store them in graph_data
            except ValueError as e:                 #If it fails,
                flash(str(e))                       #Send an error
                return redirect(request.url)        #Reload

    return render_template('index.html', graph_data=graph_data) #If it passes, add our graph data to index.html


def allowed_file(filename):                                     #Checks if the filenames are good or not.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_excel(file):                                           #Read in an Excel file, and output data and sigma
    data = []                                                   #Data is a 1-D array
    sigma = []                                                  #And so is sigma
    try:                                                        #Try to read in the data of an excel file
        wb = openpyxl.load_workbook(file, read_only=True)
        sheet = wb.active                                       #For every row
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(row[0])                                 #Data is the first column
            sigma.append(row[1])                                #And sigma is the second.  TODO: Make data even columns and sigma odd columns
    except Exception as e:                                      #If something goes wrong...
        raise ValueError(f"Error reading Excel file: {e}")      #Throw an error
    return data, sigma                                          #Otherwise return our arrays of data and sigma


def plotKDE(data, sigma):
    fig = Figure(figsize=(8, 6), dpi=100)                       #Build the graph based on matplotlib's Figure
    plt = fig.subplots()
    kde_result = kernel_density_estimation(data, sigma)         #Calculate the (x,y) points from our data and uncertainty
    x_values = kde_result[:, 0]                                 #Separate x and y values
    y_values = kde_result[:, 1]
    plt.plot(x_values, y_values, label='KDE')                   #Plot our graph
    plt.legend()                                                #Make it have a legend
    buf = BytesIO()                                             #Declare a temporary buffer
    fig.savefig(buf, format="svg", bbox_inches="tight")         #Save the figure as SVG
    data = buf.getvalue().decode("utf-8")
    return f"<div>{data}</div>"                                 #Decode the svg on the webpage


def download_image_from_session(format, filename):              #Send an image from the backend to the user
    data = session.get('data', [])                              #Retrieve our data from the current session
    sigma = session.get('sigma', 1)                             #And retrieve our uncertainty too

    fig = Figure(figsize=(8, 6), dpi=300)                       #Set up a figure with extremely high resolution
    plt = fig.subplots()
    kde_result = kernel_density_estimation(data, sigma)         #Run the density estimator again
    x_values = kde_result[:, 0]                                 #Get the x
    y_values = kde_result[:, 1]                                 #And y values
    plt.plot(x_values, y_values, label='KDE')                   #Plot them
    plt.legend()                                                #And add a legend
    buf = BytesIO()                                             #Setup a temporary buffer
    fig.savefig(buf, format=format, bbox_inches="tight")        #Save our image to the buffer in whatever format we passed in
    buf.seek(0)                                                 #And send it to the user.
    return Response(buf, mimetype=f'image/{format}', headers={'Content-Disposition': f'attachment;filename={filename}'})


@app.route('/download', methods=['GET'])                        #Handles when we tell the backend to download something to the user
def download_plot():
    format = request.args.get('format', 'png')                  #Pass in the prefered format

    if format == 'png':                                         #If it's png, download a png.
        return download_image_from_session(format='png', filename='plot.png')
    elif format == 'svg':                                       #Or if it's svg, download an svg
        return download_image_from_session(format='svg', filename='plot.svg')
    else:                                                       #Otherwise,
        flash('Invalid download format')                        #Give an error message
        return redirect(url_for('upload_file'))                 #And try again


def kernel_density_estimation(data, sigma, nsteps=1000):        #Get x and y points from a kernel density calculation
    result = np.zeros((nsteps, 2))                              #Create a new 2-D array of doubles called results
    x = np.linspace(min(data) - 2 * max(sigma),                 #Create an array of doubles called x, whose bounds are
                    max(data) + 2 * max(sigma),                 #   determined by the min and max of the data, along with
                    nsteps)                                     #   our uncertainty (sigma)
    y = np.zeros(nsteps)                                        #Create an array of doubles called y
    N = len(data)                                               #Number of data points
                                                                #Check if sigma is a single value and convert it to a list
    sigma = [sigma] if not isinstance(sigma, (list, tuple, np.ndarray)) else sigma

    for i in range(N):                                          #For every data point...
        for s in sigma:                                         #For every uncertainty...
            y = (y + 1.0 / N *                                  #Turn kernel density into X and Y points
                 (1.0 / (np.sqrt(2 * np.pi) * s)) *
                 np.exp(-(x - data[i]) ** 2 / (2 * s ** 2)))

    result[:, 0] = x                                            #Set half of the 2-D array to x values,
    result[:, 1] = y                                            #And set the other half to y values
    return result                                               #Return the entire array


if __name__ == '__main__':                                      #If we are the program being called,
    app.run(port=8000, debug=True)                              #Then run on port 8000 in debugging mode.
