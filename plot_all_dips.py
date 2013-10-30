#!/usr/bin/python
# -*- coding: utf-8 -*-

import logbook, configparser, os
import matplotlib.pyplot as plt
import sqlite3 as sql
import numpy as np

def is_dip(closes, i):
    if closes[i] < closes[i - 1] and \
       closes[i] < closes[i + 1]:
        return True
    else:
        return False

def perc_change(a, b):
    return ((b - a) / a)

config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")
log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

with log_handler.applicationbound():
    con = sql.connect("data/ysdb.sql")
    cur = con.cursor()
    tp = "MSFT"
    day_range = 20
    min_perc_incr = 0.07
    ta_offset = 33
    dip_data = []

    cur.execute("SELECT AdjClose FROM %s_HIST" % (tp))
    ac = list(zip(*cur.fetchall())[0])

    cur.execute("SELECT Rsi14 FROM %s_TA" % (tp))
    rsi14 = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT Rsi20 FROM %s_TA" % (tp))
    rsi20 = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT Rsi25 FROM %s_TA" % (tp))
    rsi25 = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT Rsi30 FROM %s_TA" % (tp))
    rsi30 = list(zip(*cur.fetchall())[0])

    cur.execute("SELECT MacdH12_26_9 FROM %s_TA" % (tp))
    macdh = list(zip(*cur.fetchall())[0])

    cur.execute("SELECT StoK_14_3_3 FROM %s_TA" % (tp))
    stok_14_3_3 = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT StoD_14_3_3 FROM %s_TA" % (tp))
    stod_14_3_3 = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT StoK_26_6_6 FROM %s_TA" % (tp))
    stok_26_6_6 = list(zip(*cur.fetchall())[0])
    cur.execute("SELECT StoD_26_6_6 FROM %s_TA" % (tp))
    stod_26_6_6 = list(zip(*cur.fetchall())[0])

    if len(ac) > 600:
        xMostRecent = 500
        for i in range(ta_offset):
            ac.pop(0)
            rsi14.pop(0)
            rsi20.pop(0)
            rsi25.pop(0)
            rsi30.pop(0)
            macdh.pop(0)
            stok_14_3_3.pop(0)
            stod_14_3_3.pop(0)
            stok_26_6_6.pop(0)
            stod_26_6_6.pop(0)

        ac = ac[-xMostRecent:]
        rsi14 = rsi14[-xMostRecent:]
        rsi20 = rsi20[-xMostRecent:]
        rsi25 = rsi25[-xMostRecent:]
        rsi30 = rsi30[-xMostRecent:]
        macdh = macdh[-xMostRecent:]
        stok_14_3_3 = stok_14_3_3[-xMostRecent:]
        stod_14_3_3 = stod_14_3_3[-xMostRecent:]
        stok_26_6_6 = stok_26_6_6[-xMostRecent:]
        stod_26_6_6 = stod_26_6_6[-xMostRecent:]

        num_dips = 0
        num_pos_m = 0
        x = np.array(range(0, day_range))
        for i in range(1, (xMostRecent - day_range)):
            y = np.zeros(len(x))
            if is_dip(ac, i):
                num_dips += 1
                for j in x:
                    y[j] = perc_change(ac[i], ac[i+j])
                A = np.vstack([x, np.ones(len(x))]).T
                m, c = np.linalg.lstsq(A, y)[0]
                if perc_change(ac[i], max(ac[i:i+day_range])) >= min_perc_incr:
                    num_pos_m += 1
                    # capture data about i
                    dip_data.append(
                        [
                            [i],
                            [
                                rsi14[i-1],
                                rsi20[i-1],
                                rsi25[i-1],
                                rsi30[i-1],
                                macdh[i-1],
                                stok_14_3_3[i-1],
                                stod_14_3_3[i-1],
                                stok_26_6_6[i-1],
                                stod_26_6_6[i-1]
                            ], # i - 1
                            [
                                rsi14[i],
                                rsi20[i],
                                rsi25[i],
                                rsi30[i],
                                macdh[i],
                                stok_14_3_3[i],
                                stod_14_3_3[i],
                                stok_26_6_6[i],
                                stod_26_6_6[i]
                            ], # i
                            [
                                rsi14[i+1],
                                rsi20[i+1],
                                rsi25[i+1],
                                rsi30[i+1],
                                macdh[i+1],
                                stok_14_3_3[i+1],
                                stod_14_3_3[i+1],
                                stok_26_6_6[i+1],
                                stod_26_6_6[i+1]
                            ] # i + 1
                        ]
                    )

                    #plt.cla()
                    #plt.plot(x, y, 'o')
                    #plt.plot(x, m*x + c, 'r')
                    #plt.xlim(0, day_range)
                    #plt.ylim(-0.2, 0.2)
                    #plt.savefig('plots/dip_%03d.png' % i)
        #print num_dips
        #print num_pos_m
        #print (num_pos_m/float(num_dips))

        stos = []
        stos_hist = []
        for data in dip_data:
            stos.append([
                [data[1][5], data[1][6]],
                [data[2][5], data[2][6]],
                [data[3][5], data[3][6]]
            ])
            stos_hist.append([
                [data[1][5] - data[1][6]],
                [data[2][5] - data[2][6]],
                [data[3][5] - data[3][6]]
            ])
        stos = np.array(stos)
        stos_hist = np.array(stos_hist)
        z = []
        for sto_data in stos_hist:
            if sto_data[0] < 0 and \
               sto_data[1] > 0:
                print "v^"
            else:
                print "."
        #plt.cla()
        #plt.hist(z, range=(-1, 1), bins=20)
        #plt.savefig('plots/z1.png')
