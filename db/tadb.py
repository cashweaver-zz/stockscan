#!/usr/bin/python
# -*- coding: utf-8 -*-

import talib
import numpy as np

def get_ta_data(hist_data):
    np_hist_data = np.array(hist_data)
    high = np_hist_data[:,2].astype(np.float)
    low = np_hist_data[:,3].astype(np.float)
    ac = np_hist_data[:,6].astype(np.float)
    rsi_14 = get_rsi(ac, 14)
    rsi_20 = get_rsi(ac, 20)
    rsi_25 = get_rsi(ac, 25)
    rsi_30 = get_rsi(ac, 30)
    stok_14_3_3, stod_14_3_3 = get_sto(high, low, ac, 14, 3, 3)
    stok_26_6_6, stod_26_6_6 = get_sto(high, low, ac, 26, 6, 6)
    macdb_12_26_9, macdr_12_26_9, macdh_12_26_9 = get_macd(ac, 12, 26, 9)

    ta_id = np.array(range(1, len(stok_14_3_3) + 1))
    return np.column_stack((
        ta_id,
        rsi_14,
        rsi_20,
        rsi_25,
        rsi_30,
        macdh_12_26_9,
        stok_14_3_3,
        stod_14_3_3,
        stok_26_6_6,
        stod_26_6_6
        ))

def get_rsi(ac, timeperiod=14):
    return np.nan_to_num(talib.RSI(ac, timeperiod))

def get_sto(high, low, ac, fastk=14, slowk=3, slowd=3):
    return np.nan_to_num(talib.STOCH(high, low, ac, fastk, slowk, slowd))

def get_macd(ac, fperiod=12, speriod=26, tperiod=9):
    return np.nan_to_num(talib.MACD(ac, fperiod, speriod, tperiod))
