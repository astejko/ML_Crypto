import csv
#import urllib2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio

import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.style as mplstyle
import matplotlib.dates as mdates
import matplotlib.cm as cm

from API_exchange import getPriceAll



def getSTF():
    #url = 'https://data.bitcoinity.org/export_data.csv?c=e&currency=USD&data_type=price&t=l&timespan=5y'
    #response = urllib2.urlopen(url)
    resp = open('./Input/stock-to-flow-ratio.csv', 'r')
    bit = csv.reader(resp)

    next(bit)
    
    tHalf = []
    tArr = []
    dateArr = []
    ratio = []

    for line in bit:
        tArr.append(line[0])
        tHalf.append(line[1])
        ratio.append(line[2])

    #------------------------

    
    timeArr = np.empty((len(tArr)))
    dateArr = np.empty((len(tArr),3))

    
    for i in range(len(tArr)):

        dateArr[i-1,0] = tArr[i].strip().split('T')[0].strip().split('-')[0]
        dateArr[i-1,1] = tArr[i].strip().split('T')[0].strip().split('-')[1]
        dateArr[i-1,2] = tArr[i].strip().split('T')[0].strip().split('-')[2]
    
    dateArr = dateArr.astype('int')

    for i in range(np.shape(dateArr)[0]):
        
        timeArr[i] =float(datetime(dateArr[i,0],dateArr[i,1],dateArr[i,2]).strftime('%s'))
    

    #-----------------------

    ratio = np.asarray(ratio[:]).astype('float')

    tHalf = np.asarray(tHalf[:]).astype('float')

    #nameEx = priceEx[0]

    #priceEx[priceEx==''] = 'NaN'

    #priceEx = priceEx.astype('float')

    #bav = np.nanmean(bp, axis = 1)

    #priceKr = priceEx[:,8]

    return timeArr,ratio,tHalf





def calcSTF():


    timeArr, ratArr, tHalf = getSTF()

    timeArrE, priceArr = getPriceAll()

    
    lenArr = np.shape(timeArr)[0]

    lenArrE = np.shape(timeArrE)[0]

    lenArrEE = lenArrE + 365

    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    STFit = np.zeros((lenArrEE))

    sig = np.zeros((lenArrE))

    sigfit = np.zeros((lenArrEE))
    
    xE = np.linspace(1,lenArrEE,lenArrEE)


    #<><><><><><><><><><><><><><><><><><><><><><><> 

        
    timeArrEE = np.empty((lenArrEE))
    
    for i in range(lenArrE):

        timeArrEE[i] = timeArrE[i]

        
    for i in range(lenArrE,lenArrEE):

        timeArrEE[i] = timeArrEE[i-1]+86400
        

    
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    diff = np.empty((lenArrE))

    for i in range(np.shape(timeArr)[0]-1):
        if (timeArrE[0] >= timeArr[i] and timeArrE[0] < timeArr[i+1]):
            sp1 = i


    ep1 = sp1+lenArrE
            
    diff[:] = np.log(priceArr[:]) - np.log(ratArr[sp1:ep1])

    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    x = np.linspace(1,lenArrE,lenArrE)


    pd = 1
    
    STFitV = np.polyfit(x[:],diff[:],pd)


    #<><><><><><><><><><><><><><><><><><><><><><><> 



    # Polynomial Expansion
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    for i in range(lenArrEE):
                
        for f in range(pd+1):
        
            STFit[i] = STFit[i] + STFitV[pd-f]*xE[i]**(f)
    


            

    for i in range(1,lenArrE):

        days = 730 + min(i-730,0)
        
        for ii in range(days):
        
            sig[i] = sig[i] + (diff[i-ii]  - STFit[i-ii])**2

        sig[i] = np.sqrt(sig[i]/days)


    sig[0] = sig[1]
        
    pd = 2
    
    sigfitV = np.polyfit(x[:],sig[:],pd)


    
    for i in range(lenArrEE):
                
        for f in range(pd+1):
        
            sigfit[i] = sigfit[i] + sigfitV[pd-f]*xE[i]**(f)
    



        
                
    return timeArrEE,STFit,sigfit


def plotSTF():

    timeArrEE, STFit,sig = calcSTF()



    
    timeArr, ratArr, tHalf = getSTF()

    timeArrE, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]

    lenArrE = np.shape(timeArrE)[0]

    lenArrEE = np.shape(timeArrEE)[0]

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    diff = np.empty((lenArrE))

    for i in range(np.shape(timeArr)[0]-1):
        if (timeArrE[0] >= timeArr[i] and timeArrE[0] < timeArr[i+1]):
            sp1 = i


    ep1 = sp1+lenArrE
            
    diff[:] = np.log(priceArr[:]) - np.log(ratArr[sp1:ep1])

    #<><><><><><><><><><><><><><><><><><><><><><><> 

    STFit_price = np.empty((lenArrEE))

    sig_p = np.empty((lenArrEE))

    sig_n = np.empty((lenArrEE))

    ep1 = sp1+lenArrEE
            
    STFit_price[:] = np.exp(STFit[:] + np.log(ratArr[sp1:ep1]))

    sig_p[:] = np.exp(2*sig[:]+STFit[:] + np.log(ratArr[sp1:ep1]))


    sig_n[:] = np.exp(STFit[:]-2*sig[:] + np.log(ratArr[sp1:ep1]))


    
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    ep1 = sp1+lenArrE
            

    sp2 = 365
    ep2= sp2+lenArrE+365
    
        
    tdArr=np.empty((lenArr),dtype='datetime64[s]')
    tdArrE=np.empty((lenArrE),dtype='datetime64[s]')
    tdArrEE=np.empty((lenArrEE),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))

    for i in range(lenArrE):
        tdArrE[i] = np.datetime64(datetime.fromtimestamp(timeArrE[i]))

    for i in range(lenArrEE):
        tdArrEE[i] = np.datetime64(datetime.fromtimestamp(timeArrEE[i]))

    

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
    mpl.rcParams['font.size'] = 13

        
    mplstyle.use(['dark_background'])


    kraken_fig = plt.figure(figsize=(9,5))
    spec = gridspec.GridSpec(ncols=1, nrows=3, figure=kraken_fig, left=0.1,right=0.93,top=0.95,bottom=0.1,hspace=0)


    ax_ohlc = kraken_fig.add_subplot(spec[0:2,0])

    ax_ohlc.tick_params(axis='x',which='both',bottom=False,top=False,labelleft=False, labeltop=False,labelright=False, labelbottom=False)
    

    ax_vol = kraken_fig.add_subplot(spec[2,0], sharex=ax_ohlc)


    #kraken_fig.set_tight_layout(tight={'h_pad':-0.5})        


    ax_ohlc.axis('off')            
    ax_vol.axis('off')


    ax_ohlc.cla()
    ax_ohlc.grid(linestyle='-', linewidth='0.2',which="both")

    ax_ohlc.plot(tdArr[sp2:ep2],ratArr[sp2:ep2], 'c-', linewidth=1)

    sc = ax_ohlc.scatter(tdArrE,priceArr,s=5, c=tHalf[sp1:ep1],cmap=cm.GnBu)


    
    ax_ohlc.plot(tdArrEE,sig_p,'w:',linewidth=1)    
    ax_ohlc.plot(tdArrEE,sig_n,'w:',linewidth=1)

    
    ax_ohlc.plot(tdArrEE,STFit_price,'w',linewidth=1)

    

    ax_ohlc.set_yscale('log')



    ax_vol.cla()

    ax_vol.scatter(tdArrE,diff,s=5, c=tHalf[sp1:ep1],cmap=cm.GnBu)


    

    #ax_vol.scatter(tdArrE,diff,s=5, c=tHalf[sp1:ep1],cmap=cm.GnBu)

    ax_vol.plot(tdArrEE,STFit+sig,'w',linewidth=1)
    ax_vol.plot(tdArrEE,STFit-sig,'w',linewidth=1)

    
    ax_vol.plot(tdArrEE,STFit+2*sig,'w:',linewidth=1)    
    ax_vol.plot(tdArrEE,STFit-2*sig,'w:',linewidth=1)

    
    ax_vol.plot(tdArrEE,STFit,'w',linewidth=1)

    
    #ax_vol.fill_between(date,0,vol,alpha=0.5)
    ax_vol.grid(linestyle='-', linewidth='0.2')

    #ax_vol.set_yscale('symlog')

    ax_vol.axhline(0,linestyle = '--',lw=0.5)



    cax = kraken_fig.add_axes([0.075,0.16,0.008,0.76])
    cbar = kraken_fig.colorbar(sc, cax = cax, ticklocation='left')#, extend='both', spacing='uniform',ticks=[370,380,390,400,410,420,430,440,450])
    
    #ax_vol.set_xlim(np.datetime64(datetime(2013,1,1)),np.datetime64(datetime(2023,1,1)))
    
    #ax_vol.set_xticklabels(date_hr)


    kraken_fig.autofmt_xdate()

    #ax_vol.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    #plt.draw()

    
    plt.show()

    




def plotlySTF():

    timeArrEE, STFit,sig = calcSTF()



    
    timeArr, ratArr, tHalf = getSTF()

    timeArrE, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]

    lenArrE = np.shape(timeArrE)[0]

    lenArrEE = np.shape(timeArrEE)[0]

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    diff = np.empty((lenArrE))

    for i in range(np.shape(timeArr)[0]-1):
        if (timeArrE[0] >= timeArr[i] and timeArrE[0] < timeArr[i+1]):
            sp1 = i


    ep1 = sp1+lenArrE
            
    diff[:] = np.log(priceArr[:]) - np.log(ratArr[sp1:ep1])

    #<><><><><><><><><><><><><><><><><><><><><><><> 

    STFit_price = np.empty((lenArrEE))

    sig_p = np.empty((lenArrEE))

    sig_n = np.empty((lenArrEE))

    ep1 = sp1+lenArrEE
            
    STFit_price[:] = np.exp(STFit[:] + np.log(ratArr[sp1:ep1]))

    sig_p[:] = np.exp(2*sig[:]+STFit[:] + np.log(ratArr[sp1:ep1]))


    sig_n[:] = np.exp(STFit[:]-2*sig[:] + np.log(ratArr[sp1:ep1]))


    
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    ep1 = sp1+lenArrE
            

    sp2 = 365
    ep2= sp2+lenArrE+365
    
        
    tdArr=np.empty((lenArr),dtype='datetime64[s]')
    tdArrE=np.empty((lenArrE),dtype='datetime64[s]')
    tdArrEE=np.empty((lenArrEE),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))

    for i in range(lenArrE):
        tdArrE[i] = np.datetime64(datetime.fromtimestamp(timeArrE[i]))

    for i in range(lenArrEE):
        tdArrEE[i] = np.datetime64(datetime.fromtimestamp(timeArrEE[i]))

    

    dateDict = {
            '1m' : '%b %d\n%H UTC',
            '3m' : '%b %d\n%H UTC',
            '1w' : '%b %d',
            '1y' : '%b %d \'%y',
            '2y' : '%b %d \'%y'
            }


    
    pio.templates.default = "plotly_dark"
    

    
    kraken_fig = make_subplots(rows=3, cols=1, specs=[[{"rowspan": 2}], [None],[{}]],shared_xaxes=True, vertical_spacing=0.1)

    


    
    kraken_fig.add_trace(go.Scatter(x=tdArrE,y=priceArr,mode='markers',name='Price',marker_color = tHalf[sp1:ep1], marker=dict(colorbar=dict(thickness=15),colorscale="GnBu"),marker_size=3), row=1,col=1)


    kraken_fig.add_trace(go.Scatter(x=tdArr[sp2:ep2],y=ratArr[sp2:ep2],name = 'STF',mode='lines',line=dict(color='cyan', width=1)), row=1,col=1)

    
    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=sig_p,name='+2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')), row=1,col=1)

                         
    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=sig_n,name='-2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')), row=1,col=1)

                         
    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=STFit_price,name='refit STF',mode='lines',line=dict(color='white', width=1)), row=1,col=1)

    
    
    kraken_fig.update_yaxes(type="log",row=1,col=1)
    






    

    
    kraken_fig.add_trace(go.Scatter(x=tdArrE,y=diff,mode='markers',name='Price',marker_color = tHalf[sp1:ep1], marker=dict(colorscale="GnBu"),marker_size=3), row=3,col=1)


        
    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=STFit+2*sig,name='+2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')), row=3,col=1)
        
    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=STFit+sig,name='+1 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')), row=3,col=1)
                         
    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=STFit-sig,name='-1 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')), row=3,col=1)

    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=STFit-2*sig,name='-2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')), row=3,col=1)

    

    kraken_fig.add_trace(go.Scatter(x=tdArrEE,y=STFit,name='refit STF',mode='lines',line=dict(color='white', width=1)), row=3,col=1)




    
    kraken_fig.update_yaxes(row=3,col=1)
    
    #kraken_fig.add_hline(y=0,fillcolor='cyan',row=3,col=1)


    
    
    kraken_fig.update_layout(showlegend=False,font=dict(size=15),autosize=False,width=1000,height=500, margin=dict(l=50,r=50,b=50,t=50,pad=4))
    
    kraken_fig.show()
    
    return kraken_fig
                                   

    

    
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
