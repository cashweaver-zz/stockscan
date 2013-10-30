#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook, configparser, os
#import matplotlib.pyplot as plt
import sqlite3 as sql
import numpy as np

config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")

log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

with log_handler.applicationbound():
    con = sql.connect("data/ysdb.sql")
    cur = con.cursor()

    bestRsis = []

    offsetMax = 40
    rsiMax = 40
    tp = "GOOG"
    for rsiSuf in range(5, (rsiMax + 1)):
        print "Rsi%d" % rsiSuf
        rsis = []
        rsiStdDev = []
        for offset in range(1, (offsetMax + 1)):
            rsis.append([])
            cur.execute("SELECT AdjClose FROM %s_HIST" % (tp))
            gAC = cur.fetchall()
            cur.execute("SELECT Rsi%d FROM %s_TA" % (rsiSuf, tp))
            gRsi = list(zip(*cur.fetchall())[0])
            if len(gRsi) > 600:
                numNullTAValues = 14
                data = list(zip(*gAC)[0])
                for i in range(numNullTAValues):
                    gRsi.pop(0)
                    gAC.pop(0)

                try:
                    diff = [((b-a)/a) for a,b in zip(data[:-offset], data[offset:])]
                    for i in range(offset):
                        gRsi.pop()

                    xMostRecent = 500
                    diff = diff[-xMostRecent:]
                    gRsi = gRsi[-xMostRecent:]

                    for i in range(xMostRecent):
                        if diff[i] > 0:
                            rsis[(offset - 1)].append(gRsi[i])

                except:
                    pass #fail silently

            #plt.cla()
            #plt.scatter(gRsi, diff, c=diff, cmap=plt.cm.BrBG, vmin=-0.005, vmax=0.005)
            #plt.title("This is the title")
            #plt.xlim(0, 100)
            #plt.ylim(-0.2, 0.3)
            #plt.savefig('plots/rsi_ac_%02d.png' % (offset))

        npRsis = np.array(rsis)
        for i, vals in enumerate(npRsis):
            rsiStdDev.append([np.std(vals), i])
        rsiStdDev.sort()
        bestRsis.append([rsiStdDev[0][0], rsiStdDev[0][1], rsiSuf])

    bestRsis.sort()
    print "standard dev, offset, RsiSuffix"
    for vals in bestRsis:
        print vals

