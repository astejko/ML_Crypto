import csv
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.style as mplstyle
import matplotlib.dates as mdates

import codecs

def getPriceAll():
    url = 'https://data.bitcoinity.org/export_data.csv?c=e&currency=USD&data_type=price&t=l&timespan=all'
    response = urllib.request.urlopen(url)
    bit = csv.reader(codecs.iterdecode(response, 'utf-8'))

    next(bit)
    
    a = []
    tArr = []
    dateArr = []
    priceEx = []

    for line in bit:
        a.append(line)
        tArr.append(line[0])
        priceEx.append(line[1::])

    
    #------------------------
    
    timeArr = np.empty((len(tArr)-1))
    dateArr = np.empty((len(tArr)-1,3))

    price = np.zeros((len(tArr)-1))
    
    for i in range(1,len(tArr)):

        dateArr[i-1,0] = tArr[i].strip().split()[0].strip().split('-')[0]
        dateArr[i-1,1] = tArr[i].strip().split()[0].strip().split('-')[1]
        dateArr[i-1,2] = tArr[i].strip().split()[0].strip().split('-')[2]
    
    dateArr = dateArr.astype('int')

    for i in range(np.shape(dateArr)[0]):
        
        timeArr[i] =float(datetime(dateArr[i,0],dateArr[i,1],dateArr[i,2]).strftime('%s'))
    

    #-----------------------

    priceEx = np.asarray(priceEx[1::])

    nameEx = priceEx[0]

    priceEx[priceEx==''] = np.nan

    priceEx = priceEx.astype('float')

    #bav = np.nanmean(bp, axis = 1)

    priceKr = priceEx[:,8]

    for i in range(np.shape(timeArr)[0]):
        for ii in range(10):
            if (np.isnan(priceEx[i,ii]) == False):
                price[i] = priceEx[i,ii]


    for i in range(np.shape(timeArr)[0]):
        if (price[i] == 0):
                price[i] = price[i-1]

            

    return timeArr,price




def getPrice():
    url = 'https://data.bitcoinity.org/export_data.csv?c=e&currency=USD&data_type=price&t=l&timespan=5y'
    response = urllib2.urlopen(url)
    bit = csv.reader(response)

    a = []
    tArr = []
    dateArr = []
    priceEx = []

    for line in bit:
        a.append(line)
        tArr.append(line[0])
        priceEx.append(line[1::])

    #------------------------
    
    timeArr = np.empty((len(tArr)-1))
    dateArr = np.empty((len(tArr)-1,3))

    
    for i in range(1,len(tArr)):

        dateArr[i-1,0] = tArr[i].strip().split()[0].strip().split('-')[0]
        dateArr[i-1,1] = tArr[i].strip().split()[0].strip().split('-')[1]
        dateArr[i-1,2] = tArr[i].strip().split()[0].strip().split('-')[2]
    
    dateArr = dateArr.astype('int')

    for i in range(np.shape(dateArr)[0]):
        
        timeArr[i] =float(datetime(dateArr[i,0],dateArr[i,1],dateArr[i,2]).strftime('%s'))
    

    #-----------------------

    priceEx = np.asarray(priceEx[1::])

    nameEx = priceEx[0]

    priceEx[priceEx==''] = 'NaN'

    priceEx = priceEx.astype('float')

    #bav = np.nanmean(bp, axis = 1)

    priceKr = priceEx[:,8]

    return timeArr,priceKr





def calcRSI(numDays):

    
    timeArr, priceArr = getPrice()

    lenArr = np.shape(timeArr)[0]
    
    RSI = np.empty((lenArr))
    priceDel = np.empty((lenArr))

    priceDel[0] = 0
    
    priceDel[1:] = (priceArr[1:] - priceArr[:-1])/priceArr[:-1]


    for i in range(lenArr):
        gain = 0
        loss  = 0
        for ii in range(max(i-(numDays-1),0),i+1):
        
            if (priceDel[ii] > 0):
                gain = gain + priceDel[ii]
            if (priceDel[ii] < 0):
                loss = loss + priceDel[ii]

        if (gain ==0 or loss == 0):
            RSI[i] = np.nan
        else:
            RSI[i] = 100. - ( 100. / (1.0+ float(abs(gain)/abs(loss)) ))
                
                
    return RSI


def plotRSI(numDays):

    timeArr, priceArr = getPrice()

    RSI = calcRSI(numDays)

    lenArr = np.shape(timeArr)[0]
    
    tdArr=np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))


    

    dateDict = {
            '1m' : '%b %d\n%H UTC',
            '3m' : '%b %d\n%H UTC',
            '1w' : '%b %d',
            '1y' : '%b %d \'%y',
            '2y' : '%b %d \'%y'
            }


    
    mpl.rcParams['axes.spines.left'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = False
    mpl.rcParams['ytick.right'] = True
    mpl.rcParams['ytick.left'] = False
    mpl.rcParams['ytick.labelright'] = True
    mpl.rcParams['ytick.labelleft'] = False
    mpl.rcParams['font.size'] = 12

        
    mplstyle.use(['dark_background'])


    kraken_fig = plt.figure()
    spec = gridspec.GridSpec(ncols=1, nrows=5, figure=kraken_fig)


    ax_ohlc = kraken_fig.add_subplot(spec[0:4,0])
    ax_ohlc.tick_params(axis='x',which='both',bottom=False,top=False,labelleft=False, labeltop=False,labelright=False, labelbottom=False)
    

    ax_vol = kraken_fig.add_subplot(spec[4,0], sharex=ax_ohlc)


    kraken_fig.set_tight_layout(tight={'h_pad':-0.5})        
    ax_ohlc.axis('off')            
    ax_vol.axis('off')


    ax_ohlc.cla()
    ax_ohlc.grid(linestyle='-', linewidth='0.2')

    ax_ohlc.plot(tdArr,priceArr, 'w:', linewidth=1)




    ax_vol.cla()

    ax_vol.plot(tdArr,RSI)
    #ax_vol.fill_between(date,0,vol,alpha=0.5)
    ax_vol.grid(linestyle='-', linewidth='0.2')



    
    #ax_vol.set_xticklabels(date_hr)


    kraken_fig.autofmt_xdate()

    #ax_vol.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    #plt.draw()
    
    plt.show()

    



    
def preRSI(numDays):

    
    timeArr, priceArr = getPrice()

    RSI = calcRSI(numDays)

    lenArr = np.shape(timeArr)[0]
    
    numDays = 2*numDays

    
    pRSI = np.zeros((100,numDays))

    
    iRSI = np.zeros((100,numDays))
    



    for i in range(lenArr):
        c = 0

        if (np.isnan(RSI[i]) == False):
        
            ci = int(RSI[i])
            
            for ii in range(i,min(i+numDays,lenArr)):

                pRSI[ci,c] = pRSI[ci,c] + (priceArr[ii] - priceArr[i])/priceArr[i]

                iRSI[ci,c] = iRSI[ci,c] + 1

            
                c+=1



    for i in range(100):
        for ii in range(numDays):

            if (iRSI[i,ii] == 0):

                pRSI[i,ii] = np.nan
            else:
                pRSI[i,ii] = pRSI[i,ii]/iRSI[i,ii]
                
                
    return pRSI














def calcEMA(numShort=50,numLong=200):

    
    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    EMA_S = np.zeros((lenArr))

    EMA_L = np.zeros((lenArr))

    
    priceDel = np.empty((lenArr))

    priceDel[0] = 0
    
    priceDel[1:] = (priceArr[1:] - priceArr[:-1])/priceArr[:-1]


    MS = (2./float(numShort+1))

    ML = (2./float(numLong+1))
            

    
    for i in range(numLong-numShort,numLong):
        EMA_S[numLong] = EMA_S[numLong] + priceArr[i]
    EMA_S[numLong] = EMA_S[numLong]/float(numShort)


    for i in range(0,numLong):
        EMA_L[numLong] = EMA_L[numLong] + priceArr[i]
    EMA_L[numLong] = EMA_L[numLong]/float(numLong)

        

    for i in range(numLong,lenArr):

        EMA_S[i] = MS*(priceArr[i] - EMA_S[i-1]) + EMA_S[i-1]

        EMA_L[i] = ML*(priceArr[i] - EMA_L[i-1]) + EMA_L[i-1]
             

                
                
    return EMA_S, EMA_L






def calcSMA(numShort=50,numLong=200):

    
    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    SMA_S = np.zeros((lenArr))

    SMA_L = np.zeros((lenArr))

    
             

    
    for i in range(numLong,lenArr):

        for ii in range(max(i-(numShort-1),0),i+1):

            SMA_S[i] = SMA_S[i] + priceArr[ii]

        for ii in range(max(i-(numLong-1),0),i+1):

            SMA_L[i] = SMA_L[i] + priceArr[ii]



               
    SMA_S[:] = SMA_S[:]/float(numShort)
    SMA_L[:] = SMA_L[:]/float(numLong)
        


                
                
    return SMA_S, SMA_L




def plotEMA(numShort=50,numLong=200):

    timeArr, priceArr = getPriceAll()

    EMA_S, EMA_L = calcEMA(numShort,numLong)

    lenArr = np.shape(timeArr)[0]
    
    tdArr=np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))



    
    Gcross = []

    Dcross = []

    for i in range(lenArr-1):
        if (EMA_S[i] > EMA_L[i] and EMA_S[i+1] < EMA_L[i+1]):
            Dcross.append(i)


        if (EMA_S[i] < EMA_L[i] and EMA_S[i+1] > EMA_L[i+1]):
            Gcross.append(i)
        

    Dprice = np.empty((len(Dcross)))
    Dtime = np.empty((len(Dcross)),dtype='datetime64[s]')

    Gprice = np.empty((len(Gcross)))
    Gtime = np.empty((len(Gcross)),dtype='datetime64[s]')

    c = 0
    for i in Gcross:
        Gprice[c] = priceArr[i]
        Gtime[c] = tdArr[i]
        c+=1
    c = 0
    for i in Dcross:
        Dprice[c] = priceArr[i]
        Dtime[c] = tdArr[i]
        c+=1
    

    dateDict = {
            '1m' : '%b %d\n%H UTC',
            '3m' : '%b %d\n%H UTC',
            '1w' : '%b %d',
            '1y' : '%b %d \'%y',
            '2y' : '%b %d \'%y'
            }


    
    mpl.rcParams['axes.spines.left'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = False
    mpl.rcParams['ytick.right'] = True
    mpl.rcParams['ytick.left'] = False
    mpl.rcParams['ytick.labelright'] = True
    mpl.rcParams['ytick.labelleft'] = False
    mpl.rcParams['font.size'] = 12

        
    mplstyle.use(['dark_background'])


    kraken_fig = plt.figure()
    spec = gridspec.GridSpec(ncols=1, nrows=5, figure=kraken_fig)


    ax_ohlc = kraken_fig.add_subplot(spec[0:4,0])
    ax_ohlc.tick_params(axis='x',which='both',bottom=False,top=False,labelleft=False, labeltop=False,labelright=False, labelbottom=False)
    

    ax_vol = kraken_fig.add_subplot(spec[4,0], sharex=ax_ohlc)


    kraken_fig.set_tight_layout(tight={'h_pad':-0.5})        
    ax_ohlc.axis('off')            
    ax_vol.axis('off')


    ax_ohlc.cla()
    ax_ohlc.grid(linestyle='-', linewidth='0.2')

    ax_ohlc.plot(tdArr,priceArr, 'w', linewidth=1)

    ax_ohlc.plot(tdArr,EMA_S, 'b', linewidth=1)

    ax_ohlc.plot(tdArr,EMA_L, 'r', linewidth=1)


    ax_ohlc.scatter(Gtime,Gprice,s=500,c='g',alpha=0.5)

    ax_ohlc.scatter(Dtime,Dprice,s=500,c='r',alpha=0.5)


    

    ax_vol.cla()

    #ax_vol.plot(tdArr,RSI)
    #ax_vol.fill_between(date,0,vol,alpha=0.5)
    ax_vol.grid(linestyle='-', linewidth='0.2')



    
    #ax_vol.set_xticklabels(date_hr)


    kraken_fig.autofmt_xdate()

    #ax_vol.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    #plt.draw()
    
    plt.show()

    




    
def preEMA(numShort=50,numLong=200):

    
    timeArr, priceArr = getPriceAll()


    EMA_S, EMA_L = calcEMA(numShort,numLong)

    
    lenArr = np.shape(timeArr)[0]
    
    #numDays = 2*numDays


    Gcross = []

    Dcross = []
    

    for i in range(lenArr-1):
        if (EMA_S[i] > EMA_L[i] and EMA_S[i+1] < EMA_L[i+1]):
            Dcross.append(i)


        if (EMA_S[i] < EMA_L[i] and EMA_S[i+1] > EMA_L[i+1]):
            Gcross.append(i)
        
    

    
    
    gEMAi = np.zeros((100,len(Gcross)))
    

    dEMAi = np.zeros((100,len(Dcross)))


    
    gEMA = np.zeros((100))
    

    dEMA = np.zeros((100))



    c = 0
    
    for i in Gcross:

        for ii in range(100):
        
            gEMAi[ii,c] =  priceArr[i+ii] - priceArr[i]


        c =c +1


    c = 0
    
    for i in Dcross:

        for ii in range(100):
        
            dEMAi[ii,c] =  priceArr[i+ii] - priceArr[i]

        c = c+1



    gEMA = np.mean(gEMAi,1)

    dEMA = np.mean(dEMAi,1)


    
    plt.plot(dEMA,'r')

    plt.plot(gEMA,'g')

    plt.show()
    
                    
    return gEMA, dEMA







    
