#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook, configparser, os
import matplotlib.pyplot as plt
import sqlite3 as sql
import numpy as np

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

    cur.execute("SELECT AdjClose FROM %s_HIST" % (tp))
    gAC = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT Sto%d_%d_%dK FROM %s_TA" % (sto1, sto2, sto3, tp))
    gStoK = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT Sto%d_%d_%dD FROM %s_TA" % (sto1, sto2, sto3, tp))
    gStoD = list(zip(*cur.fetchall())[0])
    #print gStoD
    #print gStoK
    if len(gStoD) > 600:
        #numNullTAValues = 14
        for i in gStoD:
            if i == 0:
                gStoD.pop(0)
                gStoD.pop(0)
                gAC.pop(0)

        try:
            #diff = [((b-a)/a) for a,b in zip(data[:-offset], data[offset:])]
            #for i in range(offset):
                #gRsi.pop()

            xMostRecent = 500
            gAC = gAC[-xMostRecent:]
            gStoD = gStoD[-xMostRecent:]
            gStoK = gStoK[-xMostRecent:]

            maxFuturePricePercs = []
            for i in range(1, xMostRecent):
                futurePricePercs = []
                if gStoK[i] < 20 and \
                   gStoK[i] > gStoD[i] and \
                   gStoK[i - 1] < gStoD[i - 1]:
                #if gStoK[i] > gStoD[i] and \
                   #gStoK[i - 1] < gStoD[i - 1]:
                #if gStoK[i] > 20 and \
                   #gStoK[i - 1] < 20:
                #if gStoD[i] > 20 and \
                   #gStoD[i - 1] < 20:
                    print "cross up!"
                    desiredDayRange = 20
                    dayRange = desiredDayRange if (i < (xMostRecent - desiredDayRange + 1)) else (xMostRecent - i)
                    if dayRange:
                        for j in range(1, dayRange):
                            pricePerc = (gAC[i + j] - gAC[i])/gAC[i]
                            futurePricePercs.append(pricePerc)
                        maxFuturePricePercs.append(max(futurePricePercs))
                        plt.cla()
                        plt.scatter(range(1, dayRange), futurePricePercs, c=futurePricePercs, cmap=plt.cm.BrBG, vmin=-0.005, vmax=0.005)
                        plt.title("This is the title")
                        plt.xlim(0, dayRange)
                        plt.ylim(-0.2, 0.3)
                        plt.savefig('plots/sto%03d.png' % i)
            print np.mean(np.array(maxFuturePricePercs))
        except:
            pass #fail silently

