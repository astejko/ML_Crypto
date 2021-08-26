import requests
import sys
from datetime import datetime
import hmac
import hashlib
import base64
import time
import urllib
import urllib2
import json
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from enum import Enum


import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.style as mplstyle
from mpl_finance import candlestick_ohlc as mplcandle


def getBalance():

    API_Key = '72XQfVGiXr4E6DNQKqydOv7uSdR5I9LUzXOdaKiWxoqT63wDXOZv3ea9OVH9KRPr'
    Priv_Key = 'fm9Zd3xZFmf3DYjSaqraqYyAygEFD2SRoWgrlr2hiTaAeYmhUNNEwyoVRAkseQFa'
    
    nonce = int(1000*time.time())
    params = {'timestamp' : nonce}
    
    url = 'https://api.cryptoquant.com/v1/' 

    Msig = hmac.new(Priv_Key.encode('utf-8'), urllib.urlencode(params).encode('utf-8'),hashlib.sha256).hexdigest()

    params['signature'] = Msig
    
    #header = {'X-MBX-APIKEY' : API_Key}

    header = {'Authorization' : 'Bearer' + }

    
    res = requests.get(url,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print out
        print res.text
        print res.status_code
        sys.exit()
            
    return out
    



def getOrder(pair = 'ETHBTC',oid = 0):

    API_Key = '72XQfVGiXr4E6DNQKqydOv7uSdR5I9LUzXOdaKiWxoqT63wDXOZv3ea9OVH9KRPr'
    Priv_Key = 'fm9Zd3xZFmf3DYjSaqraqYyAygEFD2SRoWgrlr2hiTaAeYmhUNNEwyoVRAkseQFa'
    
    nonce = int(1000*time.time())
    params = {'symbol': pair,
              'orderId':oid,
              'timestamp' : nonce}
    
    url = 'https://api.binance.com/api/v3/order' 

    Msig = hmac.new(Priv_Key.encode('utf-8'), urllib.urlencode(params).encode('utf-8'),hashlib.sha256).hexdigest()

    params['signature'] = Msig
    
    header = {'X-MBX-APIKEY' : API_Key}

    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print out
        print res.text
        print res.status_code
            
    return out
    



def getOpenOrders():

    API_Key = '72XQfVGiXr4E6DNQKqydOv7uSdR5I9LUzXOdaKiWxoqT63wDXOZv3ea9OVH9KRPr'
    Priv_Key = 'fm9Zd3xZFmf3DYjSaqraqYyAygEFD2SRoWgrlr2hiTaAeYmhUNNEwyoVRAkseQFa'
    
    nonce = int(1000*time.time())
    params = {'timestamp' : nonce}
    
    url = 'https://api.binance.com/api/v3/openOrders' 

    Msig = hmac.new(Priv_Key.encode('utf-8'), urllib.urlencode(params).encode('utf-8'),hashlib.sha256).hexdigest()

    params['signature'] = Msig
    
    header = {'X-MBX-APIKEY' : API_Key}

    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print out
        print res.text
        print res.status_code
        sys.exit()
            
    return out
    




def postMarketTrade(pair = 'ETHBTC',action = 'BUY',qty = None,side='asset', window=5000,cid = None):

    API_Key = '72XQfVGiXr4E6DNQKqydOv7uSdR5I9LUzXOdaKiWxoqT63wDXOZv3ea9OVH9KRPr'

    Priv_Key = 'fm9Zd3xZFmf3DYjSaqraqYyAygEFD2SRoWgrlr2hiTaAeYmhUNNEwyoVRAkseQFa'
    
    nonce = int(1000*time.time())

    if (side == 'asset'):
        Oqty = 'quantity'
    elif (side == 'fiat'):
        Oqty = 'quoteOrderQty'
    else:
        print 'Parameter "side" must be either "asset" or "fiat"'
        raise Exception()
    
    if cid is not None:
        params = {
            'symbol': pair,
            'side': action,
            'type': 'MARKET',
            Oqty : qty,
            'newClientOrderId' : cid,
            'recvWindow': window,
            'timestamp': nonce
        }
    else:
        params = {
            'symbol': pair,
            'side': action,
            'type': 'MARKET',
            Oqty: qty,
            'recvWindow': window,
            'timestamp': nonce
        }
    url = 'https://api.binance.com/api/v3/order'

    Msig = hmac.new(bytes(Priv_Key.encode('utf-8')), urllib.urlencode(params).encode('utf-8'),hashlib.sha256).hexdigest()

    params['signature'] = Msig    
    header = {'X-MBX-APIKEY' : API_Key}

    res = requests.post(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'Error Posting Trade'
        print out
        print res.text
        print res.status_code
        raise Exception()
    
    return out
    




def getTest():
            
    #inp = {'pair':clist}
    
    res = requests.get('https://api.binance.com/api/v3/ping')


    if (res.status_code == 200):
        out = res.json()
        print 'Connection SUccess'
    else:
        out = 'error onnecting to server'
        print out
        sys.exit()
        
    return out



def getTime():
            
    #inp = {'pair':clist}
    
    res = requests.get('https://api.binance.com/api/v3/time')


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out



def getInfo():
            
    #inp = {'pair':clist}
    
    res = requests.get('https://api.binance.com/api/v3/exchangeInfo')


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out


def getSymbols():


    info =  getInfo()

    symbols = []
    
    for i in range(len(info['symbols'])):
        if (info['symbols'][i]["symbol"][-3::] == 'BTC'):
            symbols.append(info['symbols'][i]["symbol"].strip())

        
    return symbols



def getBook(pair = 'PNTBTC'):
            
    inp = {'symbol':pair,
            'limit' : int(1000)}
    
    res = requests.get('https://api.binance.com/api/v3/depth', params = inp)


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out


def getTrades(pair = 'ETHBTC'):
            
    inp = {'symbol':pair,
           'limit' : int(1000)}
    
    res = requests.get('https://api.binance.com/api/v3/trades', params = inp)


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out



def getAgg(pair = 'ETHBTC',start=long(1000*(time.time()-1)),end=long(1000*time.time())):
            
    inp = {'symbol':pair,
           'limit' : int(1000),
           'startTime' : start,
           'endTime' : end
    }
    
    res = requests.get('https://api.binance.com/api/v3/aggTrades', params = inp)


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out



def getTicker(pair = 'ETHBTC'):
            
    
    inp = {'symbol':pair}
           #{'SYMBOL':'PNTBTC'}]
    
    
    res = requests.get('https://api.binance.com/api/v3/ticker/bookTicker', params = inp)


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out


def getTickerAll():
            
    
    #inp = {'symbol':pair}
           #{'SYMBOL':'PNTBTC'}]
    
    
    res = requests.get('https://api.binance.com/api/v3/ticker/bookTicker')


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        sys.exit()
        
    return out




def getOHLC(interval='3m',pair='PNTBTC',start = long(1000*(time.time()-(35*3600))),end =long(1000*(time.time())) ):

    
    INTERVAL_12HOUR = '12h'
    INTERVAL_15MINUTE = '15m'
    INTERVAL_1DAY = '1d'
    INTERVAL_1HOUR = '1h'
    INTERVAL_1MINUTE = '1m'
    INTERVAL_1MONTH = '1M'
    INTERVAL_1WEEK = '1w'
    INTERVAL_2HOUR = '2h'
    INTERVAL_30MINUTE = '30m'
    INTERVAL_3DAY = '3d'
    INTERVAL_3MINUTE = '3m'
    INTERVAL_4HOUR = '4h'
    INTERVAL_5MINUTE = '5m'
    INTERVAL_6HOUR = '6h'
    INTERVAL_8HOUR = '8h'
    
    intDict = {
        '1d' : {'startTime' :long(1000*(time.time()-(35*3600))), 'interval' :'1m'},
        '1w' : {'startTime' :long(1000*(time.time()-(280*3600))), 'interval' :'1h'},
        '1m' : {'startTime' :long(1000*(time.time()-(1680*3600))), 'interval' :'1d'},
        '1y' : {'startTime' :long(1000*(time.time()-(11760*3600))), 'interval' :'1M'}
        #'2y' : {'startTime' :long(time.time()-(25200*3600)), 'interval' :21600}
        }
    
    params ={
        'symbol' : pair,
        'interval' : interval,
        'startTime' : start,
        'endTime' : end
    }

    #params.update(intDict[interval])

#    widthDict = {
#        '1d' : 10*(24*60)/30,
#        '1w' : 10*(168*60)/240,
#        '1m' : 10*(1440*60)/1440,
#        '1y' : 10*(8760*60)/10080,
#        '2y' : 10*(17520*60)/21600
#    }

    widthDict = {
        '1m' : 100*(10*((35*60)/30)),
        '3m' : 100*(10*((35*60)/30)),
        '1h' : 100*(10*((35*60)/30)),
        '1w' : 100*(10*8*((280*60)/240)),
        '1y' : 100*(10*336*((11760*60)/10080)),
        '2y' : 100*(10*720*((25200*60)/21600))
    }

    
    res = requests.get('https://api.binance.com/api/v3/klines', params = params)


    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting time from server'
        print out
        print res.json()
        sys.exit()

    OHLClist = out
    
    #OHLC = np.empty((8,len(OHLClist)))

    OHLC = []#np.empty((len(OHLClist),5))

    av = []

    date = []
    #date_hr = []

    vol = []
    
    #for i in range(len(OHLClist)):
    #    OHLC[0,i] = OHLClist[i][0]
    #    OHLC[1,i] = OHLClist[i][1]
    #    OHLC[2,i] = OHLClist[i][2]
    #    OHLC[3,i] = OHLClist[i][3]
    #    OHLC[4,i] = OHLClist[i][4]
    #    OHLC[5,i] = OHLClist[i][5]
    #    OHLC[6,i] = OHLClist[i][6]
    #    OHLC[7,i] = OHLClist[i][7]

    for i in range(len(OHLClist)):
        for ii in range(12):
            OHLClist[i][ii] = float(OHLClist[i][ii]) 
                        
        OHLC.append(OHLClist[i][0:5])

        date.append(OHLClist[i][0])

        #date_hr.append(datetime.fromtimestamp(date[i]).strftime('%Y-%b-%d'))
        
        av.append(OHLClist[i][1]+((OHLClist[i][4]-OHLClist[i][1])/2))

        vol.append(OHLClist[i][5])
    

    try:
        width = float((end-start))/float(1000*len(date))
    except:
        print 'Error, retry'
        sys.exit()
        
    return OHLC,width,date,av,vol




def plotOHLC(interval='3m',pair='PNTBTC',start = long(1000*(time.time()-(35*3600))),end =long(1000*(time.time()))):


    OHLC,width,date,av,vol = getOHLC(interval,pair,start,end)

   
    fig = plt.figure()
    spec = gridspec.GridSpec(ncols=1, nrows=5, figure=fig)

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

    

    plot_ohlc = fig.add_subplot(spec[0:4,0])
    plot_ohlc.tick_params(axis='x',which='both',bottom=False,top=False,labelleft=False, labeltop=False,labelright=False, labelbottom=False)
    
    plot_vol = fig.add_subplot(spec[4,0], sharex=plot_ohlc)
    
    fig.set_tight_layout(tight={'h_pad':-0.5})
    plot_ohlc.axis('off')
    plot_vol.axis('off')


    plot_ohlc.cla()
    plot_ohlc.grid(linestyle='-', linewidth='0.2')
    plot_ohlc.plot(date,av, 'w:', linewidth=1)

    mplcandle(plot_ohlc,OHLC,width=width,colorup='#22AA22', colordown='#D22222')




    plot_vol.cla()
    
    plot_vol.plot(date,vol)
    plot_vol.fill_between(date,0,vol,alpha=0.5)
    plot_vol.grid(linestyle='-', linewidth='0.2')

    date_hr=[]
    
    for item in plot_vol.get_xticks():
        date_hr.append(datetime.fromtimestamp(item/1000).strftime(dateDict[interval]))

    print date_hr

    plot_vol.set_xticklabels(date_hr)
    
    #plt.plot(OHLC[:,0],OHLC[:,4])

    plt.show()
    
    #fig.savefig('./tmp/plot.png')
    
    return True






def getPNT(interval='1m',pair='PNTBTC',start = long(1000*float(datetime(2021,1,31,15).strftime('%s'))),end =long(1000*float(datetime(2021,1,31,17).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    datet = []
    for i in range(len(date)):
        datet.append(datetime.fromtimestamp(date[i]/1000).strftime('%H:%M:%S UTC'))

    OHLC = np.asarray(OHLC)

    print 'date','\t\t', 'high','\t\t','close','\t\t', 'volume'
    
    print '-------------------------------------------------------'
    
    for i in range(len(datet)):
        print datet[i],'\t', '{0:1.3e}'.format(OHLC[i,2]),'\t', '{0:1.3e}'.format(OHLC[i,4]),'\t',  '{0:1.3g}'.format(OHLC[i,2]*vol[i])
        
    return OHLC,datet,vol


def plotPNT(interval='1m',pair='PNTBTC',start = long(1000*float(datetime(2021,1,31,15).strftime('%s'))),end =long(1000*float(datetime(2021,1,31,17).strftime('%s')))):

    plotOHLC(interval,pair,start,end)
    
    
    return True




def getEVX(interval='1m',pair='EVXBTC',start = long(1000*float(datetime(2021,1,9,15).strftime('%s'))),end =long(1000*float(datetime(2021,1,9,17).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    datet = []
    for i in range(len(date)):
        datet.append(datetime.fromtimestamp(date[i]/1000).strftime('%H:%M:%S UTC'))

    OHLC = np.asarray(OHLC)

    print 'date','\t\t', 'high','\t\t','close','\t\t', 'volume'
    
    print '-------------------------------------------------------'
    
    for i in range(len(datet)):
        print datet[i],'\t', '{0:1.3e}'.format(OHLC[i,2]),'\t', '{0:1.3e}'.format(OHLC[i,4]),'\t', vol[i]
                
    return OHLC,datet,vol


def avEVX(interval='1m',pair='EVXBTC',start = long(1000*float(datetime(2021,1,8).strftime('%s'))),end =long(1000*float(datetime(2021,1,9).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    OHLC = np.asarray(OHLC)
    vol = np.asarray(vol)
        
    print np.mean(vol*OHLC[:,2])

    
    return True

def plotEVX(interval='1m',pair='EVXBTC',start = long(1000*float(datetime(2021,1,9,15).strftime('%s'))),end =long(1000*float(datetime(2021,1,9,17).strftime('%s')))):

    plotOHLC(interval,pair,start,end)
    
    
    return True




def getNEBL(interval='1m',pair='NEBLBTC',start = long(1000*float(datetime(2021,1,2,15).strftime('%s'))),end =long(1000*float(datetime(2021,1,2,17).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    datet = []
    for i in range(len(date)):
        datet.append(datetime.fromtimestamp(date[i]/1000).strftime('%H:%M:%S UTC'))

    OHLC = np.asarray(OHLC)

    
    print 'date','\t\t', 'high','\t\t','close','\t\t', 'volume'
    
    print '-------------------------------------------------------'
    
    for i in range(len(datet)):
        print datet[i],'\t', '{0:1.3e}'.format(OHLC[i,2]),'\t', '{0:1.3e}'.format(OHLC[i,4]),'\t', vol[i]
        
    return OHLC,datet,vol


def avNEBL(interval='1m',pair='NEBLBTC',start = long(1000*float(datetime(2021,1,1).strftime('%s'))),end =long(1000*float(datetime(2021,1,2).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    datet = []
    for i in range(len(date)):
        datet.append(datetime.fromtimestamp(date[i]/1000).strftime('%H:%M:%S UTC'))

    OHLC = np.asarray(OHLC)
    vol = np.asarray(vol)
        
    print np.mean(vol*OHLC[:,2])

    return True

def plotNEBL(interval='1m',pair='NEBLBTC',start = long(1000*float(datetime(2021,1,2,15).strftime('%s'))),end =long(1000*float(datetime(2021,1,2,17).strftime('%s')))):

    plotOHLC(interval,pair,start,end)
    
    
    return True


def getDLT(interval='1m',pair='DLTBTC',start = long(1000*float(datetime(2020,12,26,15).strftime('%s'))),end =long(1000*float(datetime(2020,12,26,17).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    datet = []
    for i in range(len(date)):
        datet.append(datetime.fromtimestamp(date[i]/1000).strftime('%H:%M:%S UTC'))

    OHLC = np.asarray(OHLC)

    
    print 'date','\t\t', 'high','\t\t','close','\t\t', 'volume'
    
    print '-------------------------------------------------------'
    
    for i in range(len(datet)):
        print datet[i],'\t', '{0:1.3e}'.format(OHLC[i,2]),'\t', '{0:1.3e}'.format(OHLC[i,4]),'\t',  '{0:1.3g}'.format(OHLC[i,2]*vol[i])
        
    return OHLC,datet,vol


def plotDLT(interval='1m',pair='DLTBTC',start = long(1000*float(datetime(2020,12,26,15).strftime('%s'))),end =long(1000*float(datetime(2020,12,26,17).strftime('%s')))):

    plotOHLC(interval,pair,start,end)
    
    
    return True




def getPNT2(interval='1m',pair='PNTBTC',start = long(1000*float(datetime(2020,12,4,15).strftime('%s'))),end =long(1000*float(datetime(2020,12,4,17).strftime('%s')))):

    OHLC,width,date,av,vol  = getOHLC(interval,pair,start,end)

    datet = []
    for i in range(len(date)):
        datet.append(datetime.fromtimestamp(date[i]/1000).strftime('%H:%M:%S UTC'))

    OHLC = np.asarray(OHLC)


    print 'date','\t\t', 'high','\t\t','close','\t\t', 'volume'
    
    print '-------------------------------------------------------'
    
    for i in range(len(datet)):
        print datet[i],'\t', '{0:1.3e}'.format(OHLC[i,2]),'\t', '{0:1.3e}'.format(OHLC[i,4]),'\t', vol[i]
        
    
    return OHLC,datet,vol


def plotPNT2(interval='3m',pair='PNTBTC',start = long(1000*float(datetime(2020,12,4).strftime('%s'))),end =long(1000*float(datetime(2020,12,5).strftime('%s')))):

    plotOHLC(interval,pair,start,end)
    
    
    return True





























def trade_price(volume,apair):

    book = get_book(apair)

    ask = 0
    bid = 0
    vola = 0
    volpta = 0
    volb = 0
    volptb = 0
    i = 0
    
    while (vola <= volume):
        volpta = float(book['result'][apair]['asks'][i][1])
        vola = vola + volpta
        ask = ask + (float(book['result'][apair]['asks'][i][0])*volpta)
        i+=1

    i=0
    while (volb <= volume):
        volptb = float(book['result'][apair]['bids'][i][1])
        volb = volb + volptb
        bid = bid + (float(book['result'][apair]['bids'][i][0])*volptb)
        i+=1
        
    ask = ask/vola
    bid = bid/volb

    return ask,bid


def get_ledger():

    req = 'Ledgers'

    out = private(req)
        
    return out#['result']['eb']

                    
    
