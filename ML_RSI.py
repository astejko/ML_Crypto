import csv
import urllib2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.style as mplstyle
import matplotlib.dates as mdates
from matplotlib import cm

from API_exchange import calcRSI, plotRSI, preRSI


numDays =30

#plotRSI(numDays)



pRSI = preRSI(numDays)



fig = plt.figure()

ax = fig.add_subplot(111)

ax.contourf(pRSI, levels = np.linspace(-0.5,0.5,20),cmap=cm.bwr)

plt.show()
