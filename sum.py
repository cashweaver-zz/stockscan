#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook, configparser, os, re
import matplotlib.pyplot as plt
import sqlite3 as sql

config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")

log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

def get_all_table_names():
    con = sql.connect("data/ysdb.sql")
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    tables = cursor.fetchall()
    hist_tables = [re.sub('_HIST', '', table[0])
                    for table in tables
                    if not re.search('_TA', table[0])]
    return hist_tables

with log_handler.applicationbound():
    con = sql.connect("data/ysdb.sql")
    cur = con.cursor()
    tablePrefixes = get_all_table_names()
    rsis = []
    nTables = len(tablePrefixes)
    for i, tp in enumerate(tablePrefixes):
        #print "(%04d/%d)" % (i, nTables)
        cur.execute("SELECT AdjClose FROM %s_HIST" % (tp))
        gAC = cur.fetchall()
        cur.execute("SELECT Rsi14 FROM %s_TA" % (tp))
        gRsi = list(zip(*cur.fetchall())[0])
        if len(gRsi) > 600:
            offset = 15

            numNullTAValues = 14
            for i in range(numNullTAValues):
                gRsi.pop(0)
                gAC.pop(0)
            data = list(zip(*gAC)[0])
            for i in range(offset):
                gRsi.pop(0)
            try:
                diff = [((b-a)/a) for a,b in zip(data[:-offset], data[offset:])]

                xMostRecent = 500
                diff = diff[-xMostRecent:]
                gRsi = gRsi[-xMostRecent:]

                for i in range(xMostRecent - offset):
                    if diff[i] and diff[i + offset]:
                        if ((diff[i + offset] - diff[i]) / diff[i]) > 0.1:
                            rsis.append(gRsi[i])
            except:
                pass #fail silently

    print len(rsis)
    plt.hist(rsis)
    plt.show()
