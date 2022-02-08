import requests
import sys
from datetime import datetime
import hmac
import hashlib
import base64
import time
import urllib
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
#from mpl_finance import candlestick_ohlc as mplcandle

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio


import API_key

from API_exchange import getPriceAll



#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Get BTC Price
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 


def calcPrice():


    timeArrE, priceArr = getPriceAll()

    lenArrE = np.shape(timeArrE)[0]

    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    Fit = np.zeros((lenArrE))

    sig = np.zeros((lenArrE))

    sigfit = np.zeros((lenArrE))
    
    xE = np.linspace(1,lenArrE,lenArrE)


    #<><><><><><><><><><><><><><><><><><><><><><><> 

    diff = np.empty((lenArrE))
            
    diff[:] = np.log(priceArr[:])

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Polynomial Expansion
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    
    x = np.linspace(1,lenArrE,lenArrE)

    pd = 2
    
    FitV = np.polyfit(x[:],diff[:],pd)

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    
    for i in range(lenArrE):
                
        for f in range(pd+1):
        
            Fit[i] = Fit[i] + FitV[pd-f]*x[i]**(f)

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Price Derivatives (D,W,M)
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    
    D_F0 = np.zeros((lenArrE))
    W_F0 = np.zeros((lenArrE))
    M_F0 = np.zeros((lenArrE))
    
    D_F1 = np.zeros((lenArrE))
    W_F1 = np.zeros((lenArrE))
    M_F1 = np.zeros((lenArrE))

    D_F2 = np.zeros((lenArrE))
    W_F2 = np.zeros((lenArrE))
    M_F2 = np.zeros((lenArrE))

    
    Pnorm = np.log(priceArr)-Fit
    

    #for i in range(1,lenArrE-1):
    #    D_F0[i] = Pnorm[i]
    #    D_F1[i] = (Pnorm[i+1] - Pnorm[i-1])/2.0
    #
    #for i in range(10,lenArrE-10):
    #    W_F0[i] = np.mean(Pnorm[i-3:i+3])
    #    W_F1[i] = (np.mean(Pnorm[i+3:i+10]) - np.mean(Pnorm[i-10:i-3]))/(7.0)
    #
    #for i in range(45,lenArrE-45):
    #    M_F0[i] = np.mean(Pnorm[i-15:i+15])
    #    M_F1[i] = (np.mean(Pnorm[i+15:i+45]) - np.mean(Pnorm[i-45:i-15]))/(30.0)


    for i in range(lenArrE):
        D_F0[i] = Pnorm[i]
        W_F0[i] = np.mean(Pnorm[max(0,i-3):min(lenArrE,i+4)])
        M_F0[i] = np.mean(Pnorm[max(0,i-15):min(lenArrE,i+15)])


        
    for i in range(lenArrE):

        D_F1[i] = (D_F0[min(lenArrE-1,i+1)] - D_F0[max(0,i-1)])/2.0
        D_F2[i] = D_F0[min(lenArrE-1,i+1)] - 2.0*D_F0[i] + D_F0[max(0,i-1)]


        W_F1[i] = (W_F0[min(lenArrE-1,i+7)] - W_F0[max(0,i-7)])/(14.0)
        W_F2[i] = (W_F0[min(lenArrE-1,i+7)] - (2.0*W_F0[i]) + W_F0[max(0,i-7)])/((7.0)**2)


        M_F1[i] = (M_F0[min(lenArrE-1,i+30)] - M_F0[max(0,i-30)])/(60.0)
        M_F2[i] = (M_F0[min(lenArrE-1,i+30)] - (2.0*M_F0[i]) + M_F0[max(0,i-30)])/((30.0)**2)


        
        
    #print(np.mean(D_F1))
    #print(np.mean(W_F1))
    #print(np.mean(M_F1))

        
    #plt.plot(timeArrE,M_F0)
    #plt.show()
                
    return D_F0,W_F0,M_F0,D_F1,W_F1,M_F1,D_F2,W_F2,M_F2



#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Exchange Inflow Mean (EIM)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  The Exchange Inflow Mean (EIM) is defined as the average amount of BTC per trans-
#  action of all inflows over a period of 24 hours.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 


def getEIM(limit = 100,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'exchange' : 'all_exchange',
              'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }
            
    url = 'https://api.cryptoquant.com/v1/btc/exchange-flows/inflow' 

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveEIM():

    EIM = getEIM(limit=100000)

    
    with open("EIM.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(EIM, f, indent=2) 

    with open("EIM.json", 'r') as f:
        EIMr = json.load(f)

            
    return EIMr
    



def loadEIM():
    
    with open("../Input/JSON/EIM.json", 'r') as f:
        EIMr = json.load(f)

    EIMd = np.empty((len(EIMr)))
    tdEIM = np.empty((len(EIMr)),dtype='datetime64[s]')
    timeEIM = np.empty((len(EIMr)),dtype=np.int)
        
    for i in range(len(EIMr)):
        EIMd[i] = EIMr[len(EIMr)-i-1]['inflow_mean']
        tdEIM[i] = datetime.strptime(EIMr[len(EIMr)-i-1]['date'], '%Y-%m-%d')
        timeEIM[i] = tdEIM[i].astype(np.int)

    for i in range(len(EIMd)):
        if (EIMd[i]>100):
            EIMd[i] = (EIMd[i+1]+EIMd[i-1])/2.0


    D_F0,W_F0,M_F0,D_F1,W_F1,M_F1,D_F2,W_F2,M_F2 = calcPrice()

    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    tdArr =np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))



    for t in range(lenArr):
        if (tdArr[t] == tdEIM[0]):
            tt = t

    EIMd[:] = EIMd[:]*priceArr[tt:tt+len(EIMd)]
            
            
    return EIMd,tdEIM,timeEIM
    


def plotEIM():

    EIMd,tdEIM,timeEIM = loadEIM()

    plt.plot(tdEIM,EIMd)
    plt.show()

        
    return None
    


#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Exchange WHale Ratio (EWR)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  The Exchange Whale Ratio (EWR) is the sum of the top ten exchange inflows divided
#  by all of the inflows in a period of 72 h.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 




def getEWR(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'exchange' : 'all_exchange',
              'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }

    url = 'https://api.cryptoquant.com/v1/btc/flow-indicator/exchange-whale-ratio'
    
    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveEWR():

    EWR = getEWR(limit=100000)

    
    with open("EWR.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(EWR, f, indent=2) 

    with open("EWR.json", 'r') as f:
        EWRr = json.load(f)

            
    return EWRr
    


def loadEWR():

    
    with open("../Input/JSON/EWR.json", 'r') as f:
        EWRr = json.load(f)

    EWRd = np.empty((len(EWRr)))
    tdEWR = np.empty((len(EWRr)),dtype='datetime64[s]')
    timeEWR = np.empty((len(EWRr)),dtype=np.int)
        
    for i in range(len(EWRr)):
        EWRd[i] = EWRr[len(EWRr)-i-1]['exchange_whale_ratio']
        tdEWR[i] = datetime.strptime(EWRr[len(EWRr)-i-1]['date'], '%Y-%m-%d')
        timeEWR[i] = tdEWR[i].astype(np.int)
 
            
    return EWRd,tdEWR,timeEWR
    


def plotEWR():

    EWRd,tdEWR,timeEWR = loadEWR()

    plt.plot(tdEWR,EWRd)
    plt.show()

        
    return None
    



#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Coinbase Premium Index (CPI)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
# The Coinbase Premium Index (CPI) follows the difference in price for BTC on coinbase
# over the price of BTC on binance. While binance hosts mostly non-US retail investors,
# many large investors in the USA use Coinbase to purchase BTC. A large buying mismatch
# can dramatically drive up the premium for BTC on Coinbase.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 




def getCPI(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }

    url = 'https://api.cryptoquant.com/v1/btc/market-data/coinbase-premium-index'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveCPI():

    CPI = getCPI(limit=100000)

    
    with open("CPI.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(CPI, f, indent=2) 

    with open("CPI.json", 'r') as f:
        CPIr = json.load(f)

            
    return CPIr
    




#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Grayscale Bitcoin Trust (GBT)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  The Grayscale Bitcoin Trust (GBTC) is passive long-term BTC holdings, attractive
#  to large unsavvy institutional investors. An increase in holdings indicates bullish
#  interest by large investors. The value of Grayscale will trade at a small premium
#  as compared to BTC price when there is a high institutional demand for long BTC
#  positions.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 


def getGBT(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'symbol' : 'gbtc',
              'window' : 'day',
              'limit' : limit,
              'to' : Edate
              }

    url = 'https://api.cryptoquant.com/v1/btc/fund-data/market-price-usd'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveGBT():

    GBT = getGBT(limit=100000)

    
    with open("GBT.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(GBT, f, indent=2) 

    with open("GBT.json", 'r') as f:
        GBTr = json.load(f)

            
    return GBTr
    






#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Stablecoin Inflow (SCI)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  Large and continuous spikes in stablecoin inflow can often be a sign that investors
#  are interested in purchasing BTC, which is indicative of bullish sentiment.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 



def getSCI(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'token' : 'all_token',
              'exchange' : 'all_exchange',
              'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }

    url = 'https://api.cryptoquant.com/v1/stablecoin/exchange-flows/inflow'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveSCI():

    SCI = getSCI(limit=100000)

    
    with open("SCI.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(SCI, f, indent=2) 

    with open("SCI.json", 'r') as f:
        SCIr = json.load(f)

            
    return SCIr
    

def loadSCI():
    
    with open("../Input/JSON/SCI.json", 'r') as f:
        SCIr = json.load(f)

    SCId = np.empty((len(SCIr)))
    tdSCI = np.empty((len(SCIr)),dtype='datetime64[s]')
    timeSCI = np.empty((len(SCIr)),dtype=np.int)
        
    for i in range(len(SCIr)):
        SCId[i] = SCIr[len(SCIr)-i-1]['inflow_mean']
        tdSCI[i] = datetime.strptime(SCIr[len(SCIr)-i-1]['date'], '%Y-%m-%d')
        timeSCI[i] = tdSCI[i].astype(np.int)

    
    for i in range(len(SCId)):
        if (SCId[i]>500000):
            SCId[i] = (SCId[i+1]+SCId[i-1])/2.0


        
    return SCId,tdSCI,timeSCI


def plotSCI():

    SCId,tdSCI,timeSCI = loadSCI()

    plt.plot(tdSCI,SCId)
    plt.show()

        
    return None


#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Stablecoin Ratio (SCR)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  The Stablecoin ratio is defined as the USD cost of bitcoins in an exchange divided
#  by stablecoin holdings. This ratio can be used as a gauge of investor interest in
#  either buying or selling BTC.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 



def getSCR(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'exchange' : 'all_exchange',
              'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }


    url = 'https://api.cryptoquant.com/v1/btc/exchange-flows/reserve'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    


    params = {'token' : 'all_token',
              'exchange' : 'all_exchange',
              'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }


    url = 'https://api.cryptoquant.com/v1/stablecoin/exchange-flows/reserve'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res2 = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
        out2 = res2.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()


    SCres = out2['result']['data']

    BTCres = out['result']['data']

    SCR = []    
    for i in range(len(SCres)):
        SCR.append(BTCres[i]['reserve_usd']/SCres[i]['reserve'])
    

        
    return SCres,BTCres
    


def saveSCR():

    SCres,BTCres = getSCR(limit=100000)

    
    with open("SCres.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(SCres, f, indent=2) 

        
    with open("BTCres.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(BTCres, f, indent=2) 

    #with open("SCR.json", 'r') as f:
    #    SCRr = json.load(f)

            
    return True
    

def loadSCR():
    
    with open("../Input/JSON/SCres.json", 'r') as f:
        SCres = json.load(f)
    
    with open("../Input/JSON/BTCres.json", 'r') as f:
        BTCres = json.load(f)

        
    SCRd = np.empty((len(SCres)))
    tdSCR = np.empty((len(SCres)),dtype='datetime64[s]')
    timeSCR = np.empty((len(SCres)),dtype=np.int)
        
    for i in range(len(SCres)):
        SCRd[i] = BTCres[len(BTCres)-i-1]['reserve_usd']/SCres[len(SCres)-i-1]['reserve']
        tdSCR[i] = datetime.strptime(SCres[len(SCres)-i-1]['date'], '%Y-%m-%d')
        timeSCR[i] = tdSCR[i].astype(np.int)
 

    return SCRd,tdSCR,timeSCR





def plotSCR():

    SCRd,tdSCR,timeSCR = loadSCR()

    plt.plot(tdSCR,SCRd)
    plt.show()

        
    return None




#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Bitcoin Netflow (BCN)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  The Netflow of BTC on an exchange can be indicative of bullish sentiment when it is
#  negative, signifying investor desire for long-term holding in private wallets, and
#  bearish sentiment when it is positive, signifying a general sell-off potential.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 





def getBCN(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'exchange' : 'all_exchange',
              'window' : 'day',
              'branch' : 'dynamic',
              'limit' : limit,
              'to' : Edate
              }

    url = 'https://api.cryptoquant.com/v1/btc/exchange-flows/netflow'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveBCN():

    BCN = getBCN(limit=100000)

    
    with open("BCN.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(BCN, f, indent=2) 

    with open("BCN.json", 'r') as f:
        BCNr = json.load(f)

            
    return BCNr
    



def loadBCN():
    
    # Load BCN and Date
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    with open("../Input/JSON/BCN.json", 'r') as f:
        BCNr = json.load(f)
    
        
    BCNd = np.empty((len(BCNr)))
    tdBCN = np.empty((len(BCNr)),dtype='datetime64[s]')
    timeBCN = np.empty((len(BCNr)),dtype=np.int)
        
    for i in range(len(BCNr)):
        BCNd[i] = BCNr[len(BCNr)-i-1]['netflow_total']
        tdBCN[i] = datetime.strptime(BCNr[len(BCNr)-i-1]['date'], '%Y-%m-%d')
        timeBCN[i] = tdBCN[i].astype(np.int)
 

    return BCNd,tdBCN,timeBCN



def plotBCN():

    BCNd,tdBCN,timeBCN = loadBCN()

    plt.plot(tdBCN,BCNd)
    plt.show()

        
    return None



#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Aggregated Funding Rate (AFR)
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  The Aggregated Funding Rate (AFR) is the sum of periodic payments made on per-
#  petual swaps. A positive funding rate shows large numbers of long traders paying
#  short traders and indicates a bullish market outlook, while negative funding rates
#  indicate short traders expecting a bearish market.
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 





def getAFR(limit = 100000,Edatev=int(time.time())):

    API_Key = API_key.CQ
        
    nonce = int(1000*time.time())

    tt = float(datetime(2012,4,1,0,0,0).strftime('%s'))

    dps = 24*3600

    Edate = datetime.fromtimestamp(Edatev).strftime('%Y%m%dT%H%M%S')

    Sdate = datetime.fromtimestamp(Edatev-limit*dps).strftime('%Y%m%dT%H%M%S')

    
    params = {'exchange' : 'all_exchange',
              'window' : 'day',
              'limit' : limit,
              'to' : Edate
              }

    url = 'https://api.cryptoquant.com/v1/btc/market-data/funding-rates'

    
    header = {'Authorization': 'Bearer ' + API_Key}
    
    res = requests.get(url,params=params,headers=header)
    
    
    if (res.status_code == 200):
        out = res.json()
    else:
        out = 'error getting balance from server'
        print(out)
        print(res.text)
        print(res.status_code)
        sys.exit()
            
    return out['result']['data']
    


def saveAFR():

    AFR = getAFR(limit=100000)

    
    with open("AFR.json", 'w') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(AFR, f, indent=2) 

    with open("AFR.json", 'r') as f:
        AFRr = json.load(f)

            
    return AFRr
    



def loadAFR():
    

    # Load AFR and Date
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    with open("../Input/JSON/AFR.json", 'r') as f:
        AFRr = json.load(f)
    
        
    AFRd = np.empty((len(AFRr)))
    tdAFR = np.empty((len(AFRr)),dtype='datetime64[s]')
    timeAFR = np.empty((len(AFRr)),dtype=np.int)
        
    for i in range(len(AFRr)):
        AFRd[i] = AFRr[len(AFRr)-i-1]['funding_rates']
        tdAFR[i] = datetime.strptime(AFRr[len(AFRr)-i-1]['date'], '%Y-%m-%d')
        timeAFR[i] = tdAFR[i].astype(np.int)
 

    return AFRd,tdAFR,timeAFR



def plotAFR():

    AFRd,tdAFR,timeAFR = loadAFR()

    plt.plot(tdAFR,AFRd)
    plt.show()

        
    return None


#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Correlate Standard Deviation
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  This section takes the standard deviation of an asset and correlates it to price
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 



def corrSTD(signal,ma=1,sa=365,co=0):

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Load Variables
    #<><><><><><><><><><><><><><><><><><><><><><><> 


    # Load Signal Data
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    if (signal == 'SCR'):
        VARd, tdVAR, timeVAR = loadSCR()
    elif (signal == 'SCI'):
        VARd, tdVAR, timeVAR = loadSCI()
    elif (signal == 'EIM'):
        VARd, tdVAR, timeVAR = loadEIM()
    elif (signal == 'EWR'):
        VARd, tdVAR, timeVAR = loadEWR()
    elif (signal == 'BCN'):
        VARd, tdVAR, timeVAR = loadBCN()
    elif (signal == 'AFR'):
        VARd, tdVAR, timeVAR = loadAFR()
    else:
        print,'Wrong Signal Name'
        sys.exit()
    
    lenVAR = np.shape(timeVAR)[0]
    
    for i in range(lenVAR):
        VARd[i] = np.mean(VARd[max(0,i-ma+1):i+1])
                    
    # Load Price and Date
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    
    D_F0,W_F0,M_F0,D_F1,W_F1,M_F1,D_F2,W_F2,M_F2 = calcPrice()

    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    tdArr =np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))



    #for t in range(lenArr):
    #    if (tdArr[t] == tdVAR[0]):
    #        tt = t
    #
    #
    #VARd[:] = VARd[:]*priceArr[tt:tt+lenVAR]
    

        
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Calculate Standard Deviation of VAR
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Calculate the STD for the last year of prices
    #

            
    date = np.empty((lenVAR-co),dtype='datetime64[s]')
        
    VAR_sig = np.empty((lenVAR-co))
   
    
    for i in range(lenVAR-co):

        date[i] = tdVAR[i+co]
   
        #sig = np.sqrt(np.mean((VARd[i:i+365]-np.mean(VARd[i:i+365]))**2))
        #VAR_sig[i] = (VARd[i+365]-np.mean(VARd[i:i+365]))/sig

        sp1 = co+max(0,i-sa)
        ep1 =  sp1 + sa
        
        sig = np.sqrt(np.mean((VARd[sp1:ep1]-np.mean(VARd[sp1:ep1]))**2))
             
        VAR_sig[i] = (VARd[i+co]-np.mean(VARd[sp1:ep1]))/sig

        
   
    VAR_gt_2s = [] 
    VAR_1_5s_2s = [] 
    VAR_1s_1_5s = []
    VAR_0_5s_1s = []
    VAR_0s_0_5s = []

    VAR_0s_m0_5s = []
    VAR_m0_5s_m1s = []
    VAR_m1s_m1_5s = []
    VAR_m1_5s_m2s = [] 
    VAR_lt_m2s = [] 


    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Correlate to Standard Deviation of Price
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    for t in range(lenArr):
        if (tdArr[t] == date[0]):
            tt = t
    #print(tt)

    
    VAR_bin = np.empty((lenVAR-co),dtype='int')
   
    
    
    for t in range(len(VAR_sig)):
        if (tdArr[tt+t] == date[t]):

            if (VAR_sig[t] < -2.0):
                VAR_lt_m2s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 0
            elif (VAR_sig[t]< -1.5):
                VAR_m1_5s_m2s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 1
            elif (VAR_sig[t]< -1.0):
                VAR_m1s_m1_5s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 2
            elif (VAR_sig[t]< -0.5):
                VAR_m0_5s_m1s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 3
            elif (VAR_sig[t]< 0.0):
                VAR_0s_m0_5s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 4
            elif (VAR_sig[t] < 0.5):
                VAR_0s_0_5s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 5
            elif (VAR_sig[t]< 1.0):
                VAR_0_5s_1s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 6
            elif (VAR_sig[t]< 1.5):
                VAR_1s_1_5s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 7
            elif (VAR_sig[t]< 2.0):
                VAR_1_5s_2s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 8
            else:
                VAR_gt_2s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 9

        else:
            print("Date Mismatch on Correlation")
            sys.exit()        



    VAR_c_m2s_2s = np.empty((10,6,2))

    
    VAR_gt_2s = np.asarray(VAR_gt_2s)
    VAR_1_5s_2s = np.asarray(VAR_1_5s_2s) 
    VAR_1s_1_5s = np.asarray(VAR_1s_1_5s)
    VAR_0_5s_1s = np.asarray(VAR_0_5s_1s)
    VAR_0s_0_5s = np.asarray(VAR_0s_0_5s)

    VAR_0s_m0_5s = np.asarray(VAR_0s_m0_5s)
    VAR_m0_5s_m1s = np.asarray(VAR_m0_5s_m1s)
    VAR_m1s_m1_5s = np.asarray(VAR_m1s_m1_5s)
    VAR_m1_5s_m2s = np.asarray(VAR_m1_5s_m2s)
    VAR_lt_m2s = np.asarray(VAR_lt_m2s)


    for i in range(6):
    
        VAR_c_m2s_2s[0,i,0] = np.mean(VAR_lt_m2s[:,i])
        VAR_c_m2s_2s[0,i,1] = np.sqrt(np.mean((VAR_lt_m2s[:,i]-VAR_c_m2s_2s[0,i,0])**2))
        
        VAR_c_m2s_2s[1,i,0] = np.mean(VAR_m1_5s_m2s[:,i])
        VAR_c_m2s_2s[1,i,1] = np.sqrt(np.mean((VAR_m1_5s_m2s[:,i]-VAR_c_m2s_2s[1,i,0])**2))
        
        VAR_c_m2s_2s[2,i,0] = np.mean(VAR_m1s_m1_5s[:,i])
        VAR_c_m2s_2s[2,i,1] = np.sqrt(np.mean((VAR_m1s_m1_5s[:,i]-VAR_c_m2s_2s[2,i,0])**2))
        
        VAR_c_m2s_2s[3,i,0] = np.mean(VAR_m0_5s_m1s[:,i])
        VAR_c_m2s_2s[3,i,1] = np.sqrt(np.mean((VAR_m0_5s_m1s[:,i]-VAR_c_m2s_2s[3,i,0])**2))
    
        VAR_c_m2s_2s[4,i,0] = np.mean(VAR_0s_m0_5s[:,i])
        VAR_c_m2s_2s[4,i,1] = np.sqrt(np.mean((VAR_0s_m0_5s[:,i]-VAR_c_m2s_2s[4,i,0])**2))
        
    
        
        VAR_c_m2s_2s[5,i,0] = np.mean(VAR_0s_0_5s[:,i])
        VAR_c_m2s_2s[5,i,1] = np.sqrt(np.mean((VAR_0s_0_5s[:,i]-VAR_c_m2s_2s[5,i,0])**2))
        
        VAR_c_m2s_2s[6,i,0] = np.mean(VAR_0_5s_1s[:,i])
        VAR_c_m2s_2s[6,i,1] = np.sqrt(np.mean((VAR_0_5s_1s[:,i]-VAR_c_m2s_2s[6,i,0])**2))
        
        VAR_c_m2s_2s[7,i,0] = np.mean(VAR_1s_1_5s[:,i])
        VAR_c_m2s_2s[7,i,1] = np.sqrt(np.mean((VAR_1s_1_5s[:,i]-VAR_c_m2s_2s[7,i,0])**2))
        
        VAR_c_m2s_2s[8,i,0] = np.mean(VAR_1_5s_2s[:,i])
        VAR_c_m2s_2s[8,i,1] = np.sqrt(np.mean((VAR_1_5s_2s[:,i]-VAR_c_m2s_2s[8,i,0])**2))
    
        VAR_c_m2s_2s[9,i,0] = np.mean(VAR_gt_2s[:,i])
        VAR_c_m2s_2s[9,i,1] = np.sqrt(np.mean((VAR_gt_2s[:,i]-VAR_c_m2s_2s[9,i,0])**2))


   
    
    #print(lenArr-len(VARr))
            
    #plt.plot(date,VARs)
    #plt.contourf(VARis)
    #plt.show()


        
    return tdVAR,VARd,VAR_sig,VAR_c_m2s_2s,VAR_bin
    




#\/\/\ Correlate positive signals
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 



def corrSTDp(signal,ma=1,sa=365,co=0):

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Load Variables
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    # Load Signal Data
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    if (signal == 'EIM'):
        VARd, tdVAR, timeVAR = loadEIM()
    elif (signal == 'EWR'):
        VARd, tdVAR, timeVAR = loadEWR()
    elif (signal == 'SCI'):
        VARd, tdVAR, timeVAR = loadSCI()
    elif (signal == 'SCR'):
        VARd, tdVAR, timeVAR = loadSCR()
    else:
        print,'Wrong Signal Name'
        sys.exit()
    
    lenVAR = np.shape(timeVAR)[0]

    for i in range(lenVAR):
        VARd[i] = np.mean(VARd[max(0,i-ma+1):i+1])
        
    
    # Load Price and Date
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    D_F0,W_F0,M_F0,D_F1,W_F1,M_F1,D_F2,W_F2,M_F2 = calcPrice()

    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    tdArr =np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))



    #for t in range(lenArr):
    #    if (tdArr[t] == tdVAR[0]):
    #        tt = t
    #
    #VARd[:] = VARd[:]*priceArr[tt:tt+lenVAR]
    
        
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Calculate Standard Deviation of VAR
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Calculate the STD for the last year of prices
    #
    
    date = np.empty((lenVAR-co),dtype='datetime64[s]')
        
    VAR_sig = np.empty((lenVAR-co))
   
    
    for i in range(lenVAR-co):

        date[i] = tdVAR[i+co]

        sp1 = co+max(0,i-sa)
        ep1 =  sp1 + sa
        
        sig = np.sqrt(np.mean(VARd[sp1:ep1]**2))
        VAR_sig[i] = VARd[i+co]/sig

        
        #sig = np.sqrt(np.mean(VARd[i:i+365]**2))
        #VAR_sig[i] = VARd[i+365]/sig

        
   
    VAR_gt_2s = [] 
    VAR_1_5s_2s = [] 
    VAR_1s_1_5s = []
    VAR_0_5s_1s = []
    VAR_0s_0_5s = []

    #<><><><><><><><><><><><><><><><><><><><><><><> 
    # Correlate to Standard Deviation of Price
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    for t in range(lenArr):
        if (tdArr[t] == date[0]):
            tt = t
    #print(tt)

    
    VAR_bin = np.empty((lenVAR-co),dtype='int')
   
    
    
    for t in range(len(VAR_sig)):
        if (tdArr[tt+t] == date[t]):
        
            if (VAR_sig[t] < 0.5):
                VAR_0s_0_5s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 0
            elif (VAR_sig[t]< 1.0):
                VAR_0_5s_1s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 1
            elif (VAR_sig[t]< 1.5):
                VAR_1s_1_5s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 2
            elif (VAR_sig[t]< 2.0):
                VAR_1_5s_2s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 3
            else:
                VAR_gt_2s.append([D_F1[tt+t],W_F1[tt+t],M_F1[tt+t],D_F2[tt+t],W_F2[tt+t],M_F2[tt+t]])
                VAR_bin[t] = 4

        else:
            print("Date Mismatch on Correlation")
            sys.exit()        



    VAR_c_0s_2s = np.empty((5,6,2))

    
    VAR_gt_2s = np.asarray(VAR_gt_2s)
    VAR_1_5s_2s = np.asarray(VAR_1_5s_2s) 
    VAR_1s_1_5s = np.asarray(VAR_1s_1_5s)
    VAR_0_5s_1s = np.asarray(VAR_0_5s_1s)
    VAR_0s_0_5s = np.asarray(VAR_0s_0_5s)

    for i in range(6):

        VAR_c_0s_2s[0,i,0] = np.mean(VAR_0s_0_5s[:,i])
        VAR_c_0s_2s[0,i,1] = np.sqrt(np.mean((VAR_0s_0_5s[:,i]-VAR_c_0s_2s[0,i,0])**2))
        
        VAR_c_0s_2s[1,i,0] = np.mean(VAR_0_5s_1s[:,i])
        VAR_c_0s_2s[1,i,1] = np.sqrt(np.mean((VAR_0_5s_1s[:,i]-VAR_c_0s_2s[1,i,0])**2))
        
        VAR_c_0s_2s[2,i,0] = np.mean(VAR_1s_1_5s[:,i])
        VAR_c_0s_2s[2,i,1] = np.sqrt(np.mean((VAR_1s_1_5s[:,i]-VAR_c_0s_2s[2,i,0])**2))

        if (VAR_1_5s_2s.size > 0):

            VAR_c_0s_2s[3,i,0] = np.mean(VAR_1_5s_2s[:,i])
            VAR_c_0s_2s[3,i,1] = np.sqrt(np.mean((VAR_1_5s_2s[:,i]-VAR_c_0s_2s[3,i,0])**2))
        else:

            VAR_c_0s_2s[3,i,0] = np.nan
            VAR_c_0s_2s[3,i,1] = np.nan
            
        if (VAR_gt_2s.size > 0):
            VAR_c_0s_2s[4,i,0] = np.mean(VAR_gt_2s[:,i])
            VAR_c_0s_2s[4,i,1] = np.sqrt(np.mean((VAR_gt_2s[:,i]-VAR_c_0s_2s[4,i,0])**2))
        else:
            VAR_c_0s_2s[4,i,0] = np.nan
            VAR_c_0s_2s[4,i,1] = np.nan
        
    
    
    #print(lenArr-len(VARr))
            
    #plt.plot(date,VARs)
    #plt.contourf(VARis)
    #plt.show()


        
    return tdVAR,VARd,VAR_sig,VAR_c_0s_2s,VAR_bin
    





#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#\/\/\ Plotting Code
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 
#  This section holds the template for the plotting code
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/| 



def plotSTD(signal,ma=1,sa=365,co=0):


    # Load Price and Date
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    D_F0,W_F0,M_F0,D_F1,W_F1,M_F1,D_F2,W_F2,M_F2 = calcPrice()

    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    tdArr =np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))


    f_x =np.empty((lenArr))
    f_xp =np.empty((lenArr))
    f_xm =np.empty((lenArr))
        
    # Load VAR
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    tdVAR, VARd, VAR_sig, VAR_c_m2s_2s,VAR_bin = corrSTD(signal,ma,sa,co)
    
    lenVAR = np.shape(tdVAR)[0]

    
    VARs =np.zeros((lenVAR-co))
    
    VARm =np.zeros((lenVAR-co))
    
    for i in range(lenVAR-co):
        
        sp1 = co+max(0,i-sa)
        ep1 =  sp1 + sa

        VARm[i] = np.mean(VARd[sp1:ep1])

        VARs[i] = (VARd[i+co]-VARm[i])

    
    #<><><><><><><><><><><><><><><><><><><><><><><> 


    for t in range(lenArr):
        if (tdArr[t] == tdVAR[0]):
            tt = t
                
    
    pio.templates.default = "plotly_dark"

    
    #kraken_fig = make_subplots(rows=3, cols=1, specs=[[{"rowspan": 2}], [None],[{}]],shared_xaxes=True, vertical_spacing=0.1)

    
    #kraken_fig = make_subplots(specs=[[{"secondary_y": True}]])


    
    kraken_fig = make_subplots(rows=1, cols=2, column_widths=[0.1, 0.9],specs=[[{},{"secondary_y": True}]],horizontal_spacing=0.05)#specs=[[{"rowspan": 2}], [None],[{}]],shared_xaxes=True, horizontal_spacing=0.5)


    
    # Prediction Plot
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    i=0
    
    for b in range(10):
        
        M_F1 = VAR_c_m2s_2s[b,2,0]
        M_F1_sig = VAR_c_m2s_2s[b,2,1]
        
        M_F2 = VAR_c_m2s_2s[b,5,0]
        M_F2_sig = VAR_c_m2s_2s[b,5,1]
        
        for ii in range(i,i+31):
            
            f_xp[ii] = b + (ii-i)*(M_F1+M_F1_sig) + ((ii-i)**2)*(M_F2+M_F2_sig)/2.0
            f_x[ii] = b + (ii-i)*M_F1 + ((ii-i)**2)*M_F2/2.0
            f_xm[ii] = b + (ii-i)*(M_F1-M_F1_sig) + ((ii-i)**2)*(M_F2-M_F2_sig)/2.0
    
        kraken_fig.add_trace(go.Scatter(x=np.arange(31),y=f_xp[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(31),y=f_x[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(31),y=f_xm[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'),row=1,col=1)



    i=0
    
    for b in range(10):

        W_F1 = VAR_c_m2s_2s[b,1,0]
        W_F1_sig = VAR_c_m2s_2s[b,1,1]
        
        W_F2 = VAR_c_m2s_2s[b,4,0]
        W_F2_sig = VAR_c_m2s_2s[b,4,1]
        
        for ii in range(i,i+8):
                
            f_xp[ii] = b + (ii-i)*(W_F1+W_F1_sig) + ((ii-i)**2)*(W_F2+W_F2_sig)/2.0
            f_x[ii] = b + (ii-i)*W_F1 + ((ii-i)**2)*W_F2/2.0
            f_xm[ii] = b + (ii-i)*(W_F1-W_F1_sig) + ((ii-i)**2)*(W_F2-W_F2_sig)/2.0
    
        kraken_fig.add_trace(go.Scatter(x=np.arange(8),y=f_xp[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(8),y=f_x[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(8),y=f_xm[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'),row=1,col=1)
    

                
    kraken_fig.add_trace(go.Scatter(x=[0,0,0,0,0,0,0,0,0,0],y=np.arange(10),mode='markers',name='Price',marker_size=10,marker_color = np.arange(5), marker=dict(colorscale="RdBu")),row=1,col=1)

    
    
    # Daily Predictions
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    
    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #    ii = i+1
    #    
    #    D_F1 = VAR_c_m2s_2s[b,0,0]
    #    D_F1_sig = VAR_c_m2s_2s[b,0,1]
    #    
    #    D_F2 = VAR_c_m2s_2s[b,3,0]
    #    D_F2_sig = VAR_c_m2s_2s[b,3,1]
    #
    #    f_xp[ii] = D_F0[tt+i] + (ii-i)*(D_F1+D_F1_sig) +((ii-i)**2)*(D_F2+D_F2_sig)/2.0
    #    f_x[ii] = D_F0[tt+i] + (ii-i)*D_F1 + ((ii-i)**2)*D_F2/2.0
    #    f_xm[ii] = D_F0[tt+i] + (ii-i)*(D_F1-D_F1_sig) + ((ii-i)**2)*(D_F2-D_F2_sig)/2.0
    #       
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xp[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xm[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    


    # Weekly Predictions
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #
    #    if (b==4):
    #    
    #        W_F1 = VAR_c_m2s_2s[b,1,0]
    #        W_F1_sig = VAR_c_m2s_2s[b,1,1]
    #    
    #        W_F2 = VAR_c_m2s_2s[b,4,0]
    #        W_F2_sig = VAR_c_m2s_2s[b,4,1]
    #    
    #        for ii in range(i,i+8):
    #            
    #            f_xp[ii] = W_F0[tt+i] + (ii-i)*(W_F1+W_F1_sig) + ((ii-i)**2)*(W_F2+W_F2_sig)/2.0            
    #            f_x[ii] = W_F0[tt+i] + (ii-i)*W_F1 + ((ii-i)**2)*W_F2/2.0
    #            f_xm[ii] = W_F0[tt+i] + (ii-i)*(W_F1-W_F1_sig) + ((ii-i)**2)*(W_F2-W_F2_sig)/2.0
    #
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+8],y=f_xp[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+8],y=f_x[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+8],y=f_xm[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    

        
    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #    ii = i+7
    #    
    #    W_F1 = VAR_c_m2s_2s[b,1,0]
    #    W_F1_sig = VAR_c_m2s_2s[b,1,1]
    #    
    #    W_F2 = VAR_c_m2s_2s[b,4,0]
    #    W_F2_sig = VAR_c_m2s_2s[b,4,1]
    #
    #    f_xp[ii] = W_F0[tt+i] + (ii-i)*(W_F1+W_F1_sig) +((ii-i)**2)*(W_F2+W_F2_sig)/2.0
    #    f_x[ii] = W_F0[tt+i] + (ii-i)*W_F1 + ((ii-i)**2)*W_F2/2.0
    #    f_xm[ii] = W_F0[tt+i] + (ii-i)*(W_F1-W_F1_sig) + ((ii-i)**2)*(W_F2-W_F2_sig)/2.0
    #       
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xp[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #    
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xm[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    

   
    # Monthly Predictions
    #<><><><><><><><><><><><><><><><><><><><><><><> 


    #for i in range(lenVAR):
    #    
    #    b = VAR_bin[i-365]
    #
    #    if (b==4):
    #    
    #        M_F1 = VAR_c_m2s_2s[b,2,0]
    #        M_F1_sig = VAR_c_m2s_2s[b,2,1]
    #    
    #        M_F2 = VAR_c_m2s_2s[b,5,0]
    #        M_F2_sig = VAR_c_m2s_2s[b,5,1]
    #    
    #        for ii in range(i,i+31):
    #        
    #            f_xp[ii] = M_F0[tt+i] + (ii-i)*(M_F1+M_F1_sig) + ((ii-i)**2)*(M_F2+M_F2_sig)/2.0            
    #            f_x[ii] = M_F0[tt+i] + (ii-i)*M_F1 + ((ii-i)**2)*M_F2/2.0
    #            f_xm[ii] = M_F0[tt+i] + (ii-i)*(M_F1-M_F1_sig) + ((ii-i)**2)*(M_F2-M_F2_sig)/2.0
    #
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+31],y=f_xp[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+31],y=f_x[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+31],y=f_xm[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    


    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #    ii = i+30
    #    
    #    M_F1 = VAR_c_m2s_2s[b,2,0]
    #    M_F1_sig = VAR_c_m2s_2s[b,2,1]
    #    
    #    M_F2 = VAR_c_m2s_2s[b,5,0]
    #    M_F2_sig = VAR_c_m2s_2s[b,5,1]
    #
    #    f_xp[ii] = M_F0[tt+i] + (ii-i)*(M_F1+M_F1_sig) +((ii-i)**2)*(M_F2+M_F2_sig)/2.0
    #    f_x[ii] = M_F0[tt+i] + (ii-i)*M_F1 + ((ii-i)**2)*M_F2/2.0
    #    f_xm[ii] = M_F0[tt+i] + (ii-i)*(M_F1-M_F1_sig) + ((ii-i)**2)*(M_F2-M_F2_sig)/2.0
    #       
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xp[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xm[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))



    # Plot BTC price
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    if (co != 0):
        kraken_fig.add_trace(go.Scatter(x=tdArr[tt:tt+co],y=D_F0[tt:tt+co],mode='lines',line=dict(color='white', width=1)),row=1,col=2)

    
    #kraken_fig.add_trace(go.Scatter(x=tdArr,y=priceArr,mode='markers',name='Price',marker_color = tHalf[sp1:ep1], marker=dict(colorbar=dict(thickness=15),colorscale="GnBu"),marker_size=3), row=1,col=1)

    
    kraken_fig.add_trace(go.Scatter(x=tdArr[tt+co:],y=D_F0[tt+co:],mode='markers',name='Price',marker_size=5,marker_color = VAR_bin, marker=dict(colorscale="RdBu")),row=1,col=2)


    # Plot VAR
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    kraken_fig.add_trace(go.Scatter(x=tdVAR,y=VARd,mode='lines',name='Price',marker_size=1,marker_color ='rgba(115,210,225,0.75)',line=dict(width=1),fill='tozeroy',fillcolor='rgba(115,210,225,0.5)'),secondary_y=True,row=1,col=2)


    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm+2*(VARs/VAR_sig),name='+2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm+1.5*(VARs/VAR_sig),name='+1.5 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm+(VARs/VAR_sig),name='+1 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm+0.5*(VARs/VAR_sig),name='+0.5 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')),secondary_y=True,row=1,col=2)

    
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm,name='0 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
                                          

    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm-0.5*(VARs/VAR_sig),name='-0.5 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')),secondary_y=True,row=1,col=2)

    
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm-(VARs/VAR_sig),name='-1 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)

    
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm-1.5*(VARs/VAR_sig),name='-1.5 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')),secondary_y=True,row=1,col=2)

    
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=VARm-2*(VARs/VAR_sig),name='-2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
        
        #kraken_fig.update_yaxes(row=3,col=1)    
    #kraken_fig.add_hline(y=0,fillcolor='cyan',row=3,col=1)


    xaxis=dict(
        title="Days",
        linecolor="#BCCCDC",
        showspikes=False,) # Show spike line for X-axis
        # Format spike
        #spikethickness=2,
        #spikedash="dot",
        #spikecolor="#999999",
        #spikemode="across",)

    xaxis2=dict(
        title="Date",
        linecolor="#BCCCDC",
        showspikes=True, # Show spike line for X-axis
        # Format spike
        spikethickness=2,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",)

    
    kraken_fig.update_layout(showlegend=False,font=dict(size=15),autosize=False,width=1500,height=800, margin=dict(l=50,r=25,b=50,t=50,pad=4),xaxis=xaxis,xaxis2=xaxis2)

    
    #kraken_fig.update_layout(showlegend=False,font=dict(size=15),autosize=True, margin=dict(l=50,r=25,b=50,t=50,pad=4),xaxis=xaxis,xaxis2=xaxis2)

    #kraken_fig.write_image("./Figures/fig1.png")
    
    kraken_fig.show()
                                   

    return None
















def plotSTDp(signal,ma=1,sa=365,co=0):


    # Load Price and Date
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    D_F0,W_F0,M_F0,D_F1,W_F1,M_F1,D_F2,W_F2,M_F2 = calcPrice()

    timeArr, priceArr = getPriceAll()

    lenArr = np.shape(timeArr)[0]
    
    tdArr =np.empty((lenArr),dtype='datetime64[s]')
    for i in range(lenArr):
        tdArr[i] = np.datetime64(datetime.fromtimestamp(timeArr[i]))


    f_x =np.empty((lenArr))
    f_xp =np.empty((lenArr))
    f_xm =np.empty((lenArr))
        
    # Load VAR
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    tdVAR, VARd, VAR_sig, VAR_c_0s_2s,VAR_bin = corrSTDp(signal,ma,sa,co)
    
    lenVAR = np.shape(tdVAR)[0]

    #<><><><><><><><><><><><><><><><><><><><><><><> 


    for t in range(lenArr):
        if (tdArr[t] == tdVAR[0]):
            tt = t
                
    
    pio.templates.default = "plotly_dark"

    
    #kraken_fig = make_subplots(rows=3, cols=1, specs=[[{"rowspan": 2}], [None],[{}]],shared_xaxes=True, vertical_spacing=0.1)

    
    kraken_fig = make_subplots(rows=1, cols=2, column_widths=[0.1, 0.9],specs=[[{},{"secondary_y": True}]],horizontal_spacing=0.05)#specs=[[{"rowspan": 2}], [None],[{}]],shared_xaxes=True, horizontal_spacing=0.5)

    
    #kraken_fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    
    #kraken_fig.add_trace(go.Scatter(x=tdArr,y=priceArr,mode='markers',name='Price',marker_color = tHalf[sp1:ep1], marker=dict(colorbar=dict(thickness=15),colorscale="GnBu"),marker_size=3), row=1,col=1)

    
    # Prediction Plot
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    
    i=0
    
    for b in range(5):
        
        M_F1 = VAR_c_0s_2s[b,2,0]
        M_F1_sig = VAR_c_0s_2s[b,2,1]
        
        M_F2 = VAR_c_0s_2s[b,5,0]
        M_F2_sig = VAR_c_0s_2s[b,5,1]
        
        for ii in range(i,i+31):
            
            f_xp[ii] = b + (ii-i)*(M_F1+M_F1_sig) + ((ii-i)**2)*(M_F2+M_F2_sig)/2.0
            f_x[ii] = b + (ii-i)*M_F1 + ((ii-i)**2)*M_F2/2.0
            f_xm[ii] = b + (ii-i)*(M_F1-M_F1_sig) + ((ii-i)**2)*(M_F2-M_F2_sig)/2.0
    
        kraken_fig.add_trace(go.Scatter(x=np.arange(31),y=f_xp[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(31),y=f_x[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(31),y=f_xm[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'),row=1,col=1)



    i=0
    
    for b in range(5):

        W_F1 = VAR_c_0s_2s[b,1,0]
        W_F1_sig = VAR_c_0s_2s[b,1,1]
        
        W_F2 = VAR_c_0s_2s[b,4,0]
        W_F2_sig = VAR_c_0s_2s[b,4,1]
        
        for ii in range(i,i+8):
                
            f_xp[ii] = b + (ii-i)*(W_F1+W_F1_sig) + ((ii-i)**2)*(W_F2+W_F2_sig)/2.0
            f_x[ii] = b + (ii-i)*W_F1 + ((ii-i)**2)*W_F2/2.0
            f_xm[ii] = b + (ii-i)*(W_F1-W_F1_sig) + ((ii-i)**2)*(W_F2-W_F2_sig)/2.0
    
        kraken_fig.add_trace(go.Scatter(x=np.arange(8),y=f_xp[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(8),y=f_x[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'),row=1,col=1)
        kraken_fig.add_trace(go.Scatter(x=np.arange(8),y=f_xm[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'),row=1,col=1)
    

                
    kraken_fig.add_trace(go.Scatter(x=[0,0,0,0,0],y=np.arange(5),mode='markers',name='Price',marker_size=10,marker_color = np.arange(5), marker=dict(colorscale="RdBu")),row=1,col=1)

    
    
    # Daily Predictions
    #<><><><><><><><><><><><><><><><><><><><><><><> 
    
    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #    ii = i+1
    #    
    #    D_F1 = VAR_c_0s_2s[b,0,0]
    #    D_F1_sig = VAR_c_0s_2s[b,0,1]
    #    
    #    D_F2 = VAR_c_0s_2s[b,3,0]
    #    D_F2_sig = VAR_c_0s_2s[b,3,1]
    #
    #    f_xp[ii] = D_F0[tt+i] + (ii-i)*(D_F1+D_F1_sig) +((ii-i)**2)*(D_F2+D_F2_sig)/2.0
    #    f_x[ii] = D_F0[tt+i] + (ii-i)*D_F1 + ((ii-i)**2)*D_F2/2.0
    #    f_xm[ii] = D_F0[tt+i] + (ii-i)*(D_F1-D_F1_sig) + ((ii-i)**2)*(D_F2-D_F2_sig)/2.0
    #       
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xp[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xm[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    


    # Weekly Predictions
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #
    #    if (b==4):
    #    
    #        W_F1 = VAR_c_0s_2s[b,1,0]
    #        W_F1_sig = VAR_c_0s_2s[b,1,1]
    #    
    #        W_F2 = VAR_c_0s_2s[b,4,0]
    #        W_F2_sig = VAR_c_0s_2s[b,4,1]
    #    
    #        for ii in range(i,i+8):
    #            
    #            f_xp[ii] = W_F0[tt+i] + (ii-i)*(W_F1+W_F1_sig) + ((ii-i)**2)*(W_F2+W_F2_sig)/2.0            
    #            f_x[ii] = W_F0[tt+i] + (ii-i)*W_F1 + ((ii-i)**2)*W_F2/2.0
    #            f_xm[ii] = W_F0[tt+i] + (ii-i)*(W_F1-W_F1_sig) + ((ii-i)**2)*(W_F2-W_F2_sig)/2.0
    #
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+8],y=f_xp[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+8],y=f_x[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+8],y=f_xm[i:i+8],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    

        
    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #    ii = i+7
    #    
    #    W_F1 = VAR_c_0s_2s[b,1,0]
    #    W_F1_sig = VAR_c_0s_2s[b,1,1]
    #    
    #    W_F2 = VAR_c_0s_2s[b,4,0]
    #    W_F2_sig = VAR_c_0s_2s[b,4,1]
    #
    #    f_xp[ii] = W_F0[tt+i] + (ii-i)*(W_F1+W_F1_sig) +((ii-i)**2)*(W_F2+W_F2_sig)/2.0
    #    f_x[ii] = W_F0[tt+i] + (ii-i)*W_F1 + ((ii-i)**2)*W_F2/2.0
    #    f_xm[ii] = W_F0[tt+i] + (ii-i)*(W_F1-W_F1_sig) + ((ii-i)**2)*(W_F2-W_F2_sig)/2.0
    #       
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xp[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #    
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xm[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    

   
    # Monthly Predictions
    #<><><><><><><><><><><><><><><><><><><><><><><> 


    #for i in range(lenVAR):
    #    
    #    b = VAR_bin[i-365]
    #
    #    if (b==4):
    #    
    #        M_F1 = VAR_c_0s_2s[b,2,0]
    #        M_F1_sig = VAR_c_0s_2s[b,2,1]
    #    
    #        M_F2 = VAR_c_0s_2s[b,5,0]
    #        M_F2_sig = VAR_c_0s_2s[b,5,1]
    #    
    #        for ii in range(i,i+31):
    #        
    #            f_xp[ii] = M_F0[tt+i] + (ii-i)*(M_F1+M_F1_sig) + ((ii-i)**2)*(M_F2+M_F2_sig)/2.0            
    #            f_x[ii] = M_F0[tt+i] + (ii-i)*M_F1 + ((ii-i)**2)*M_F2/2.0
    #            f_xm[ii] = M_F0[tt+i] + (ii-i)*(M_F1-M_F1_sig) + ((ii-i)**2)*(M_F2-M_F2_sig)/2.0
    #
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+31],y=f_xp[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+31],y=f_x[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(115,210,225,1)',fill='tonexty'))
    #        kraken_fig.add_trace(go.Scatter(x=tdVAR[i:i+31],y=f_xm[i:i+31],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))
    


    #for i in range(lenVAR):
    #
    #    b = VAR_bin[i-365]
    #    ii = i+30
    #    
    #    M_F1 = VAR_c_0s_2s[b,2,0]
    #    M_F1_sig = VAR_c_0s_2s[b,2,1]
    #    
    #    M_F2 = VAR_c_0s_2s[b,5,0]
    #    M_F2_sig = VAR_c_0s_2s[b,5,1]
    #
    #    f_xp[ii] = M_F0[tt+i] + (ii-i)*(M_F1+M_F1_sig) +((ii-i)**2)*(M_F2+M_F2_sig)/2.0
    #    f_x[ii] = M_F0[tt+i] + (ii-i)*M_F1 + ((ii-i)**2)*M_F2/2.0
    #    f_xm[ii] = M_F0[tt+i] + (ii-i)*(M_F1-M_F1_sig) + ((ii-i)**2)*(M_F2-M_F2_sig)/2.0
    #       
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xp[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)'))
    #
    #kraken_fig.add_trace(go.Scatter(x=tdVAR[:],y=f_xm[:],mode='lines',name='Price',marker_size=3,marker_color ='rgba(75,215,75,1)',fill='tonexty'))



    # Plot BTC price
    #<><><><><><><><><><><><><><><><><><><><><><><> 
        

    if (co != 0):
        kraken_fig.add_trace(go.Scatter(x=tdArr[tt:tt+co],y=D_F0[tt:tt+co],mode='lines',line=dict(color='white', width=1)),row=1,col=2)

    
    #kraken_fig.add_trace(go.Scatter(x=tdArr,y=priceArr,mode='markers',name='Price',marker_color = tHalf[sp1:ep1], marker=dict(colorbar=dict(thickness=15),colorscale="GnBu"),marker_size=3), row=1,col=1)

    
    #kraken_fig.add_trace(go.Scatter(x=tdArr[tt+365:],y=D_F0[tt+365:],mode='markers',name='Price',marker_size=5,marker_color = VAR_bin, marker=dict(colorbar=dict(thickness=15),colorscale="RdBu")),row=1,col=2)

    
    kraken_fig.add_trace(go.Scatter(x=tdArr[tt+co:],y=D_F0[tt+co:],mode='markers',name='Price',marker_size=5,marker_color = VAR_bin, marker=dict(colorscale="RdBu")),row=1,col=2)


    # Plot VAR
    #<><><><><><><><><><><><><><><><><><><><><><><> 

    kraken_fig.add_trace(go.Scatter(x=tdVAR,y=VARd,mode='lines',name='Price',marker_size=1,marker_color ='rgba(115,210,225,0.75)',line=dict(width=1),fill='tozeroy',fillcolor='rgba(115,210,225,0.5)'),secondary_y=True,row=1,col=2)


    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=2*(VARd[co:]/VAR_sig),name='+2 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=1.5*(VARd[co:]/VAR_sig),name='+1.5 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=(VARd[co:]/VAR_sig),name='+1 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=0.5*(VARd[co:]/VAR_sig),name='+0.5 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dot')),secondary_y=True,row=1,col=2)
        
    kraken_fig.add_trace(go.Scatter(x=tdVAR[co:],y=0*(VARd[co:]/VAR_sig),name='0 STD Dev',mode='lines',line=dict(color='white', width=1, dash='dash')),secondary_y=True,row=1,col=2)
                                          

        #kraken_fig.update_yaxes(row=3,col=1)    
    #kraken_fig.add_hline(y=0,fillcolor='cyan',row=3,col=1)


    xaxis=dict(
        title="Days",
        linecolor="#BCCCDC",
        showspikes=False,) # Show spike line for X-axis
        # Format spike
        #spikethickness=2,
        #spikedash="dot",
        #spikecolor="#999999",
        #spikemode="across",)

    xaxis2=dict(
        title="Date",
        linecolor="#BCCCDC",
        showspikes=True, # Show spike line for X-axis
        # Format spike
        spikethickness=2,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",)

    
    kraken_fig.update_layout(showlegend=False,font=dict(size=15),autosize=False,width=1500,height=800, margin=dict(l=50,r=25,b=50,t=50,pad=4),xaxis=xaxis,xaxis2=xaxis2)

    
    #kraken_fig.update_layout(showlegend=False,font=dict(size=15),autosize=True, margin=dict(l=50,r=25,b=50,t=50,pad=4),xaxis=xaxis,xaxis2=xaxis2)
    
    kraken_fig.show()
                                   

