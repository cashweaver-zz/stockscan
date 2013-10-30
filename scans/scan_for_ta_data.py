#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook
import configparser
import os
import re
import sqlite3 as sql
import random
#import numpy as np
#import matplotlib.pyplot as plt

def is_dip(yesterday_close, today_close, tomorrow_close, i):
    if today_close < yesterday_close and \
       today_close > tomorrow_close:
        return True
    else:
        return False

def perc_change(a, b):
    return ((b - a) / a)


config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")

log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

with log_handler.applicationbound():
    # Create connection to database
    # =========================================================================
    con = sql.connect("data/ysdb.sql")
    cur = con.cursor()

    # Configuration variables
    # =========================================================================
    offsetMax = 40
    rsiMax = 40
    offset = 35
    sto1 = 14
    sto2 = 3
    sto3 = 3
    macd_h1 = 12
    macd_h2 = 26
    macd_h3 = 9
    num_symbols = 2

    # Get all symbols from our symbol_list file
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # We have all table names [ ... , 'GOOG_TA', 'GOOG_HIST', ... ]
    # We want a single "GOOG"
    all_symbols = list(zip(*cur.fetchall())[0])
    regex = re.compile('.*_HIST$')
    # Get list like [ ... , 'GOOG', 'MSFT', 'YHOO', ... ]
    all_symbols = [s.replace('_HIST', '') for s in all_symbols if
                   regex.match(s)]
    # Randomly order the symbols
    random.shuffle(all_symbols)
    # Create new array of a manageable size
    some_symbols = all_symbols[:num_symbols]

    # Iterate over each symbol and:
    #   1. Find all places where the filters match
    #   2. Collect data
    #   3. Print data
    # =========================================================================
    for symbol in some_symbols:
        # Get data from database
        cur.execute("SELECT AdjClose FROM %s_HIST" % (symbol))
        gAC = list(zip(*cur.fetchall())[0])
        cur.execute("SELECT StoK_%d_%d_%d FROM %s_TA" % (sto1, sto2, sto3, symbol))
        gStoK = list(zip(*cur.fetchall())[0])
        cur.execute("SELECT StoD_%d_%d_%d FROM %s_TA" % (sto1, sto2, sto3, symbol))
        gStoD = list(zip(*cur.fetchall())[0])
        cur.execute("SELECT MacdH%d_%d_%d FROM %s_TA" % (macd_h1, macd_h2, macd_h3, symbol))
        gMacdH = list(zip(*cur.fetchall())[0])

        # Only consider stocks that have been in existance for at least 3
        # years. There are roughly 250 points of data for a stock per year.
        if len(gStoD) > 750:
            try:
                # Only worry about data from the last two years.
                xMostRecent = 500
                gAC = gAC[-xMostRecent:]
                gStoD = gStoD[-xMostRecent:]
                gStoK = gStoK[-xMostRecent:]
                gMacdH = gMacdH[-xMostRecent:]

                # Start from the second item (1 in the following list) [0, 1, 2]
                # Do this because most filters need at least one day of previous
                # close data.
                for i in range(1, xMostRecent):
                    # Filters go here
                    if is_dip(gAC[i-1], gAC[i], gAC[i+1], i):
                        # Found one!
                        #print "Hit: %s" % symbol

                        # Collect data
                        cross_msg = "crossed!" if (gStoK[i-1] < gStoD[i-1] and
                                                   gStoK[i] > gStoD[i]) else ""
                        print "K[%f] D[%f] %s" % (
                            gStoK[i],
                            gStoD[i],
                            cross_msg)
                        #print gStoK[i]
                        #print gStoD[i]

            except:
                pass #fail silently
