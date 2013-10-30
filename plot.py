#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook, configparser, os
import matplotlib.pyplot as plt
import sqlite3 as sql

config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")

log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

with log_handler.applicationbound():
    con = sql.connect("data/ysdb.sql")
    cur = con.cursor()
    count = 100
    tp = "GOOG"
    for offset in range(1, (count + 1)):
        cur.execute("SELECT AdjClose FROM %s_HIST" % tp)
        gAC = cur.fetchall()
        cur.execute("SELECT Rsi20 FROM %s_TA" % tp)
        gRsi = list(zip(*cur.fetchall())[0])

        numNullTAValues = 20
        for i in range(numNullTAValues):
            gRsi.pop(0)
            gAC.pop(0)
        data = list(zip(*gAC)[0])
        for i in range(offset):
            gRsi.pop()
        diff = [((b-a)/a) for a,b in zip(data[:-offset], data[offset:])]

        xMostRecent = 500
        diff = diff[-xMostRecent:]
        gRsi = gRsi[-xMostRecent:]
        #print zip(diff, gRsi)
        plt.cla()
        #plt.scatter(gRsi, diff, c=["#ffffff", "#ff0000"], cmap=plt.cm.RdBu)
        plt.scatter(gRsi, diff, c=diff, cmap=plt.cm.BrBG, vmin=-0.005, vmax=0.005)
        plt.title("This is the title")
        plt.xlim(0, 100)
        plt.ylim(-0.2, 0.3)
        #plt.show()
        plt.savefig('plots/rsi_ac_%02d.png' % (offset))
        print 'plots/rsi_ac_%02d.png' % (offset)
    print "\n"
