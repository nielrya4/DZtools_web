import openpyxl


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}                #Only accept xlsx and xls files


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
