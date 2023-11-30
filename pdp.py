import numpy as np
from io import BytesIO
from matplotlib.figure import Figure
def probability_density_plot(data, sigma, nsteps=1000):        #Get x and y points from a kernel density calculation
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


def plot_pdp(data, sigma):
    fig = Figure(figsize=(8, 6), dpi=100)                       #Build the graph based on matplotlib's Figure
    plt = fig.subplots()
    kde_result = probability_density_plot(data, sigma)         #Calculate the (x,y) points from our data and uncertainty
    x_values = kde_result[:, 0]                                 #Separate x and y values
    y_values = kde_result[:, 1]
    plt.plot(x_values, y_values, label='KDE')                   #Plot our graph
    plt.legend()                                                #Make it have a legend
    buf = BytesIO()                                             #Declare a temporary buffer
    fig.savefig(buf, format="svg", bbox_inches="tight")         #Save the figure as SVG
    data = buf.getvalue().decode("utf-8")
    return f"<div>{data}</div>"                                 #Decode the svg on the webpage
