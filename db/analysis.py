#!/usr/bin/python
# -*- coding: utf-8 -*-

#import numpy as np
import yahoostockdb
import pylab
import configparser, os, re
from sqlite3 import dbapi2 as lite

max_walk_range = 10
min_acceptable_price_perc = 1.10
min_years_of_data = 4
data_points_per_year = 250

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__))+"/config.ini")
symbol_list = config['DATABASE']['symbol_list_path']
db_path = config['DATABASE']['db_path']

class Analysis(object):
    def __init__(self):
        pass

    def scan(self, symbols):
        days_after = []
        ysdb = yahoostockdb.Database()
        for symbol in symbols:
            ac = [x[0] for x in ysdb._get_adj_close(symbol)]

            # for all AdjCloses that both have a price before them (ie, not ac[0])
            # and have at least max_walk_range days after them
            for i in range(1, len(ac)-1-max_walk_range):
                if ac[i] <= ac[i-1] and ac[i] <= ac[i+1]:
                    #print "%d > %d < %d" % (ac[i-1], ac[i], ac[i+1])
                    min_acceptable_price = ac[i] * min_acceptable_price_perc
                    for j in range(1, max_walk_range+1):
                        if ac[i+j] >= min_acceptable_price:
                            #print "ac[%d] == %f  |  ac[%d] == %f  | minprice == %f  |  n == %d" % (i, ac[i], (i+j), ac[i+j], min_acceptable_price, j)
                            days_after.append(j)
                            break

        pylab.hist(days_after, max_walk_range)
        pylab.show()

    def scan_all(self):
        days_after = []
        ysdb = yahoostockdb.Database()

        con = lite.connect(config['DATABASE']['db_path'])
        cursor = con.cursor()
        cursor.execute(
            "SELECT sm.name AS TableName \
            FROM sqlite_master AS sm\
            WHERE type = 'table' \
                AND name LIKE '%_HIST'")
        tables = cursor.fetchall()
        hist_tables = [re.sub('_HIST', '', table[0]) for table in tables]
        all_syms = hist_tables[2:3]

        for k, symbol in enumerate(all_syms):
            print "(%04d/%04d) %s" % ((k+1), len(all_syms), symbol)
            ac = [x[0] for x in ysdb._get_adj_close(symbol)]
            if len(ac) >= (min_years_of_data * data_points_per_year):
                ac = ac[-1000:]

                # for all AdjCloses that both have a price before them (ie, not ac[0])
                # and have at least max_walk_range days after them
                for i in range(1, len(ac)-1-max_walk_range):
                    if ac[i] <= ac[i-1] and ac[i] <= ac[i+1]:
                        #print "%d > %d < %d" % (ac[i-1], ac[i], ac[i+1])
                        min_acceptable_price = ac[i] * min_acceptable_price_perc
                        for j in range(1, max_walk_range+1):
                            if ac[i+j] >= min_acceptable_price:
                                print "ac[%d] == %f  |  ac[%d] == %f  | minprice == %f  |  n == %d" % (i, ac[i], (i+j), ac[i+j], min_acceptable_price, j)
                                days_after.append(j)
                                break

        if len(days_after):
            pylab.hist(days_after, max_walk_range)
            #pylab.show()
