#!/usr/bin/python
# -*- coding: utf-8 -*-

import yahoostockdb
import logbook, configparser, os

config = configparser.ConfigParser()
config.read(os.getcwd()+"/config.ini")

log_handler = logbook.FileHandler(config['DEBUG']['log_fpath'])

with log_handler.applicationbound():
    ysdb = yahoostockdb.Database()
    ysdb.init_db()
    #ysdb.update_db()
    #scan = yahoostockdb.analysis.Analysis()
    #scan.scan(["GOOG"])
    #scan.scan_all()
