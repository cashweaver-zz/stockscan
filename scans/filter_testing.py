#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook, configparser, os
import matplotlib.pyplot as plt
import sqlite3 as sql
#import numpy as np

config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")

log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

with log_handler.applicationbound():
    con = sql.connect("data/ysdb.sql")
    cur = con.cursor()

    bestRsis = []
    rsis = []

    offsetMax = 40
    rsiMax = 40
    tp = "GOOG"
    offset = 35
    sto1 = 14
    sto2 = 3
    sto3 = 3
    macd_h1 = 12
    macd_h2 = 26
    macd_h3 = 9

    cur.execute("SELECT AdjClose FROM %s_HIST" % (tp))
    gAC = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT StoK_%d_%d_%d FROM %s_TA" % (sto1, sto2, sto3, tp))
    gStoK = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT StoD_%d_%d_%d FROM %s_TA" % (sto1, sto2, sto3, tp))
    gStoD = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT MacdH%d_%d_%d FROM %s_TA" % (macd_h1, macd_h2, macd_h3, tp))
    gMacdH = list(zip(*cur.fetchall())[0])
    if len(gStoD) > 600:
        for i in gStoD:
            if i == 0:
                gStoD.pop(0)
                gStoD.pop(0)
                gAC.pop(0)
        try:
            xMostRecent = 500
            gAC = gAC[-xMostRecent:]
            gStoD = gStoD[-xMostRecent:]
            gStoK = gStoK[-xMostRecent:]
            gMacdH = gMacdH[-xMostRecent:]

            maxFuturePricePercs = []
            for i in range(1, xMostRecent):
                # Filters:
                #   MACD Hist broke downward trend today
                #   Stochastic K crossed up across D today
                if i > 1 and \
                   gMacdH[i] < 0 and \
                   gMacdH[i - 2] > gMacdH[i - 1] and \
                   gMacdH[i - 1] < gMacdH[i] and \
                   gStoK[i - 1] < gStoD[i - 1] and \
                   gStoK[i] > gStoD[i]:

                    print "Hit!"
                    futurePricePercs = []
                    desiredDayRange = 20
                    dayRange = desiredDayRange if (i < (xMostRecent - desiredDayRange + 1)) else (xMostRecent - i)
                    for j in range(1, dayRange):
                        pricePerc = (gAC[i + j] - gAC[i])/gAC[i]
                        futurePricePercs.append(pricePerc)
                    #maxFuturePricePercs.append(max(futurePricePercs))
                    plt.cla()
                    plt.scatter(range(1, dayRange), futurePricePercs, c=futurePricePercs, cmap=plt.cm.BrBG, vmin=-0.005, vmax=0.005)
                    plt.title("This is the title")
                    plt.xlim(0, dayRange)
                    plt.ylim(-0.2, 0.3)
                    plt.savefig('plots/MACD_Hist_12_26_9_cross_upward_through_0-%03d.png' % i)
                #print np.mean(np.array(maxFuturePricePercs))
        except:
            pass #fail silently

