#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook
import configparser
import os
import re
import sqlite3 as sql
import random
import numpy as np
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
    # Add some top padding to output for readability
    print ""

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
    x_most_recent = 500
    day_range = 20
    filename_prefix = "generated_plot"
    # There are 7237 total symbols in our list
    # For a confidence interval of 98-100%, the following number of samples is
    # required...
    num_symbols = 4200

    # Containers for all data we find
    # =========================================================================
    overall_line_of_best_fit_slopes = []
    overall_max_future_price_percs = []
    overall_min_future_price_percs = []

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
            # Only worry about data from the last two years.
            gAC = gAC[-x_most_recent:]
            gStoD = gStoD[-x_most_recent:]
            gStoK = gStoK[-x_most_recent:]
            gMacdH = gMacdH[-x_most_recent:]
            x = np.array(range(0, day_range))
            perc_price_diff = np.zeros(len(x))

            min_future_price_percs = []
            max_future_price_percs = []
            line_of_best_fit_slopes = []

            # Start from the second item (1 in the following list) [0, 1, 2]
            # Do this because most filters need at least one day of previous
            # close data.
            for i in range(3, (x_most_recent - day_range)):
                futurePricePercs = []

                # if MACD broke a downward trend today, and the stoch crossed
                # up
                if gMacdH[i] < 0 and \
                   gStoK[i] < 20 and \
                   gMacdH[i - 3] > gMacdH[i - 2] and \
                   gMacdH[i - 2] > gMacdH[i - 1] and \
                   gMacdH[i - 1] < gMacdH[i] and \
                   gStoK[i - 1] < gStoD[i - 1] and \
                   gStoK[i] > gStoD[i]:
                    # Found one!
                    #print "Hit: %s" % (symbol)

                    # Get the future price percentages
                    for j in range(1, day_range):
                        pricePerc = (gAC[i + j] - gAC[i])/gAC[i]
                        futurePricePercs.append(pricePerc)

                    # Calculate a line of best fit for out scatter plot
                    for j in x:
                        perc_price_diff[j] = perc_change(gAC[i], gAC[i+j])
                    A = np.vstack([x, np.ones(len(x))]).T
                    m, c = np.linalg.lstsq(A, perc_price_diff)[0]
                    line_of_best_fit_slopes.append(m)

                    # Capture a plot of the next 20 day's closes as a
                    # percent of today's close.
                    dayRange = day_range if (i < (x_most_recent - day_range + 1)) else (x_most_recent - i)
                    max_future_price_percs.append(max(futurePricePercs))
                    min_future_price_percs.append(min(futurePricePercs))
                    #plt.cla()
                    #plt.plot(x, perc_price_diff, 'o')
                    #plt.plot(x, m*x + c, 'r')
                    #plt.scatter(range(1, dayRange), futurePricePercs, c=futurePricePercs, cmap=plt.cm.BrBG, vmin=-0.005, vmax=0.005)
                    #plt.title("This is the title")
                    #plt.xlim(0, dayRange)
                    #plt.ylim(-0.2, 0.3)
                    #plt.savefig('plots/%s-%s-%03d.png' % (filename_prefix,
                                                            #symbol, i))

            #print "%s | Mean slope for line-of-best-fit: %f" % (symbol,
                                                                #np.mean(np.array(line_of_best_fit_slopes)))
            #print "%s | Mean maximum future price perc: %f" % (symbol,
                                                               #np.mean(np.array(max_future_price_percs)))
            #print ""

            # Save data for final print out
            overall_line_of_best_fit_slopes += line_of_best_fit_slopes
            overall_max_future_price_percs += max_future_price_percs
            overall_min_future_price_percs += min_future_price_percs

    print "Combined data"
    print "--------------------------------"
    print "Mean slope for line-of-best-fit: %f" % np.mean(np.array(overall_line_of_best_fit_slopes))
    print "Mean maximum future price perc: %f" % np.mean(np.array(overall_max_future_price_percs))
    print "Mean minimum future price perc: %f" % np.mean(np.array(overall_min_future_price_percs))
    print "Total hits: %d" % len(overall_line_of_best_fit_slopes)
    print "Mean hits per day: %f" % (len(overall_line_of_best_fit_slopes)/float(x_most_recent))
    print ""
    #plt.cla()
    #plt.hist(overall_max_future_price_percs, range=(-0.2, 0.4), bins=20)
    #plt.savefig('plots/%s-max.png' % (filename_prefix))
    #plt.cla()
    #plt.hist(overall_min_future_price_percs, range=(-0.4, 0.2), bins=20)
    #plt.savefig('plots/%s-min.png' % (filename_prefix))
