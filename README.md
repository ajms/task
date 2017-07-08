Tech choices:
------
I have chosen to load the data.csv file into a sqlite database to easily extract information from the data.
For the main part of my analysis of the data set, I have used Python 3 as it is easy to use and has libraries for plotting and using sqlite database that I am familiar with
I have also used a few lines of code in R for fitting some linear models.

Usage:
The analysis_data.py uses the libraries sqlite, pandas, numpy and matplotlib.pyplot. The input data file data.csv should be in the same directory as the program. The program runs with Python 3 by e.g. entering
python analysis_data.py in a terminal.

Details and Output:
The program loads the dataset data.csv into a sqlite3 database data.db, prints out the results of my analyses and generates six plots: isp_normalised.png, browser_normalised.png, isp_normalised2.png, browser_normalised2.png, isp_boxplots.png and browser_boxplots.png.


Approach to the exploration:
------
My first goal was to familiarise myself with the dataset.
The results of preliminary analysis:
Remark: I have omitted the last element from the csv file from my analysis, since it was missing a cdn-value.

* The dataset consists of 534,953 rows.
* 9 streams: 1-9, between 25,000 and 100,000 views, size between 10499.972076 and 104999917.46590701.
I use the simplifying assumption that the size of a stream is the maximum of cdn + p2p.
* 5 Isps = Fro, Arange, BTP, Datch Telecam, Olga.
* 4 Browsers = Iron, EarthWolf, Vectrice, Swamp.
* Connected = 485,752/534,953.

After the initial analysis, I was interested in reducing the dimensions of the data.

Since I computed the sizes of the streams, I could normalise the p2p and cdn-data by dividing p2p and cdn by the size of its stream, assuming that all streams "perform" equally well. This eliminates the variable stream.

To get a further understanding of the data, I plotted for every browser and every isp the normalised cdn against the normalised p2p, colouring the connected = true green and connected = false blue. The plots are isp_normalised.png and browser_normalised.png.

They indicate that without a connection to the backend, the p2p-trafic is 0, which I then checked to be true.
Hence, assuming that we are mainly interested in the p2p-traffic, I could also omit data points without a backend connection from my analysis, since they don't have any influence on the p2p traffic. This eliminates the variable connected.

Furthermore, the plots indicate a linear proportionality of the normalised p2p and cdn.
This I investigated in R: Indeed, there appears to be a linear proportionality between the normalised p2p and cdn. Both the plot and the regression indicate that almost all users stream the entire stream (the sum of cdn and p2p is close to 1 for all data points). 

So now we are down to investigating the influence of the browser choice and the isp on the downloaded data through p2p.
First I made the same plots of browsers and isp's as before, just without the data points without backend connection and colouring the ips's in the browser plots and vice versa. The plots are isp_normalised2.png, browser_normalised2.png. This did not give me the impression of dependence between browser and isp. 
To investigate this further, I made two linear models in R: the normalised p2p as independent variable with browser and isp as dependent variables, the first one with all combinations of browser and isp, the second one without. This was not so successful and did not give me any further inside, since
* most of the variables appear to be significant,
* the assumption of a linear model might be questioned (the data looks rather generated uniformly within some intervals, or I am missing an input),
* on the plots, the values are clustered in blocks, so a mean value does not represent the data very well.

So instead I decided to make the box plots of the normalised p2p for all browsers and isp's. This gives more interesting results, indicating which browsers and isp's perform worse wrt. the p2p-traffic. The plots are isp_boxplot.png and browser_boxplot.png
Among the browsers, Vectrice and Swap seem to be performing badly. The first one having median, first and third quartile around 0 whereas Swamp has the median around 0.
Among the isp's, Arange and Olga don't perform very well. Arange has its median around 0 and Olga has its median below 0.2. 


Data driven recommendations to improve the service:
------
I am assuming that we would like to maximise the amount of p2p-traffic (and minimise the cdn-traffic), since this is more cost effective.

* The service / p2p-functionality should be optimised for the browsers Vectrice and Swap.
* The isp's Olga and Arange might have a net neutrality problem (and have not been paid enough) or might have some security measures or have other hurdles, limiting the p2p-traffic. The service should be optimised specifically for these internet providers.
* The p2p-service should be implemented also for outside users without any backend access.


What would I have done, if I had more time?
------
* I would investigate more thoroughly the badly performing browsers / isp's. There seems to be more structure in the distribution of the data points, since they appear in clusters.
* I would investigate the dependence of the choice of browser for a given isp. But I would not expect a very strong correlation between those two.