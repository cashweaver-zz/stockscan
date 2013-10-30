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

    bestMeanDiffs = []

    offsetMax = 40
    rsiMax = 40
    tp = "GOOG"
    for rsiSuf in range(5, (rsiMax + 1)):
        print "Rsi%d" % rsiSuf
        rsis = []
        mDiffs = []
        for offset in range(1, (offsetMax + 1)):
            posRsis = []
            negRsis = []
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
                            posRsis.append(gRsi[i])
                        else:
                            negRsis.append(gRsi[i])
                    mPos = np.mean(posRsis)
                    mNeg = np.mean(negRsis)
                    stdDevPos = np.std(posRsis)
                    mDiffs.append([abs(mPos - mNeg), stdDevPos, offset])
                except:
                    pass #fail silently
        mDiffs.sort()
        maxDiff = mDiffs.pop()
        bestMeanDiffs.append([maxDiff[0], maxDiff[1], maxDiff[2], rsiSuf])


    bestMeanDiffs.sort()
    print "mean diff, std dev of positive outcomes, offset, RsiSuffix"
    for vals in bestMeanDiffs:
        print vals

