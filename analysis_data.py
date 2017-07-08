#!/usr/bin/python

#imports
import sqlite3 as sql
import pandas
import numpy as np
import matplotlib.pyplot as plt

__author__ = 'Albert Schulz'
__version__= '1.0'
__modified__='20170708'


# DB-connection and cursor
sqlserver = sql.connect('data.db')
c = sqlserver.cursor()


# put data.csv into a sqlite database
#c.execute('create table data (stream integer, isp text, browser text, connected boolean, p2p real, cdn real);')
c.execute('create table data (stream integer, isp text, browser text, connected boolean, p2p real, cdn real);')
sqlserver.commit()

df = pandas.read_csv('data.csv', names = ['stream', 'isp', 'browser', 'connected', 'p2p', 'cdn'],\
                        dtype={'stream': int, 'isp' : str, 'browser' : str, 'connected' : bool, 'p2p' : float, 'cdn' :float}, header=0)
df.to_sql('data', sqlserver, if_exists='append', index=False)

# delete defect data point.
c.execute('delete from data where cdn is null;')
sqlserver.commit()

# Getting to know the data set
print('The stream ids')
for row in c.execute('select distinct stream from data;'):
    print(row)
print('\nThe isps')
isps = c.execute('select distinct isp from data;').fetchall()
for element in isps:
    print(element)

print('\nThe browsers')
browsers = c.execute('select distinct browser from data;').fetchall()
for element in browsers:
    print(element)

print('\nThe number of connections to backend')
print(c.execute('select count(connected) from data where connected = 1;').fetchone())

print('\nThe number of connections')
print(c.execute('select count(stream) from data;').fetchone())



# Compute the size of the streams
streamsize = [None]*9

for i in range(1,10,1):
    print("\nstream " + str(i))
    print("Number of viewers " + str(c.execute('select count(cdn) from data where stream=?',str(i)).fetchone()[0]))
    print("Maximum p2p " + str(c.execute('select max(p2p) from data where stream=?;',str(i)).fetchone()[0]))
    print("Maximum cdn " + str(c.execute('select max(cdn) from data where stream=?;',str(i)).fetchone()[0]))
    streamsize[i-1] = c.execute('select max(cdn+p2p) from data where stream=?;',str(i)).fetchone()[0]
    print("Maximum p2p+cdn " + str(streamsize[i-1]))

# Create a new table data2 with the normalised p2p and cdn.

#c.execute('drop table data2')
c.execute('create table data2 (isp text, browser text, connected boolean, cdnnorm real, p2pnorm real)')
sqlserver.commit()
for i in range(1,10,1):
    c.execute('insert into data2 (isp, browser, connected, cdnnorm, p2pnorm) select isp, browser, connected, cdn/?, p2p/? from data where stream = ?;',(streamsize[i-1],streamsize[i-1],i))
    sqlserver.commit()

# Colours for plotting    
colours = ['b','g','r','y','k']

# Plots of the different isp's: norm. cdn against p2p
f, axarr = plt.subplots(2,3)
i=0
for isp in isps:
    index0 = int(format(i,'03b')[1])
    index1 = int(format(i,'03b')[2])+2*int(format(i,'03b')[0])
    plotdata1 = np.array(c.execute('select cdnnorm,p2pnorm from data2 where isp = ? and connected=1', isp).fetchall())
    plotdata2 = np.array(c.execute('select cdnnorm,p2pnorm from data2 where isp = ? and connected=0', isp).fetchall())
    axarr[index0,index1].plot(plotdata1[:,0],plotdata1[:,1], 'b.', label = isp[0]+' c', markersize=0.2, alpha=0.5)
    axarr[index0,index1].plot(plotdata2[:,0],plotdata2[:,1], 'g.', label = isp[0]+' unc', markersize=0.2, alpha=0.5)
    axarr[index0,index1].legend(loc=1,prop={'size':5})
    i+=1

f.text(0.5, 0.04, 'normalised cdn', ha='center')
f.text(0.04, 0.5, 'normalised p2p', va='center', rotation='vertical')
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 2]], visible=False)
plt.savefig('isp_normalised.png',dpi=300)
plt.clf()

# Plots of the different browsers: norm. cdn against p2p
f, axarr = plt.subplots(2,2)
i=0
for browser in browsers:
    index0 = int(format(i,'02b')[0])
    index1 = int(format(i,'02b')[1])
    plotdata1 = np.array(c.execute('select cdnnorm,p2pnorm from data2 where browser = ? and connected=1', browser).fetchall())
    plotdata2 = np.array(c.execute('select cdnnorm,p2pnorm from data2 where browser = ? and connected=0', browser).fetchall())
    axarr[index0,index1].plot(plotdata1[:,0],plotdata1[:,1],'b.', label = browser[0]+' c', markersize=0.2, alpha=0.5)
    axarr[index0,index1].plot(plotdata2[:,0],plotdata2[:,1],'g.', label = browser[0]+' unc', markersize=0.2, alpha=0.5) 
    axarr[index0,index1].legend(loc=1,prop={'size':5})
    i+=1

f.text(0.5, 0.04, 'normalised cdn', ha='center')
f.text(0.04, 0.5, 'normalised p2p', va='center', rotation='vertical')
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
plt.savefig('browser_normalised.png',dpi=200)
plt.clf()

# Check whether the p2p is actually 0 without connection to the backend.
print("Number of p2p > 0 with connected = false")
print(c.execute('select count(p2p) from data where connected = 0 and p2p>0').fetchone())

# Ommits the connected = false data points. Plots of the browsers with isp's coloured.
f, axarr = plt.subplots(2,2)
i=0
for browser in browsers:
    index0 = int(format(i,'02b')[0])
    index1 = int(format(i,'02b')[1])
    for colour,isp in zip(colours,isps):
        plotdata1 = np.array(c.execute('select cdnnorm,p2pnorm from data2 where browser = ? and isp = ? and connected=1', (browser[0],isp[0])).fetchall())
        axarr[index0,index1].plot(plotdata1[:,0],plotdata1[:,1], colour+'+', label = isp[0]+' c', markersize=0.2, alpha=0.5)
        axarr[index0,index1].set_title(browser[0],fontsize=7)
    axarr[index0,index1].legend(loc=1,prop={'size':5})
    i+=1
f.text(0.5, 0.04, 'normalised cdn', ha='center')
f.text(0.04, 0.5, 'normalised p2p', va='center', rotation='vertical')
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
plt.savefig('browser_normalised_2.png',dpi=300)
plt.clf()

# Ommits the connected = false data points. Plots of the isp's with browsers coloured.
f, axarr = plt.subplots(2,3)
i=0
for isp in isps:
    index0 = int(format(i,'03b')[1])
    index1 = int(format(i,'03b')[2])+2*int(format(i,'03b')[0])
    for colour, browser in zip(colours,browsers):
        plotdata1 = np.array(c.execute('select cdnnorm,p2pnorm from data2 where isp = ? and browser = ? and connected=1', (isp[0],browser[0])).fetchall())
        axarr[index0,index1].plot(plotdata1[:,0],plotdata1[:,1], colour+'+', label = browser[0]+' c', markersize=0.2, alpha=0.5)
        axarr[index0,index1].set_title(isp[0],fontsize=7)
    axarr[index0,index1].legend(loc=1,prop={'size':5})
    i+=1
f.text(0.5, 0.04, 'normalised cdn', ha='center')
f.text(0.04, 0.5, 'normalised p2p', va='center', rotation='vertical')
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 2]], visible=False)
plt.savefig('isp_normalised_2.png',dpi=300)
plt.clf()

# Boxplots of the browsers
f, axarr = plt.subplots(2,2)
i=0
for browser in browsers:
    index0 = int(format(i,'02b')[0])
    index1 = int(format(i,'02b')[1])
    plotdata1 = np.array(c.execute('select p2pnorm from data2 where browser = ? and connected=1', browser).fetchall())
    axarr[index0,index1].boxplot(plotdata1[:,0])
    axarr[index0,index1].set_title(browser[0],fontsize=7)
    i += 1
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
plt.savefig('browser_boxplots.png',dpi=200)
plt.clf()

#Boxplots of the isp's
f, axarr = plt.subplots(2,3)
i=0
for isp in isps:
    index0 = int(format(i,'03b')[1])
    index1 = int(format(i,'03b')[2])+2*int(format(i,'03b')[0])
    plotdata1 = np.array(c.execute('select p2pnorm from data2 where isp = ? and connected=1', isp).fetchall())
    axarr[index0,index1].boxplot(plotdata1[:,0])
    axarr[index0,index1].set_title(isp[0],fontsize=7)
    i+=1
    
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 2]], visible=False)
plt.savefig('isp_boxplot.png',dpi=300)
plt.clf()


#Closing db
c.close()
sqlserver.close()
