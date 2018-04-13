# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


class orderBook:
    def __init__(self, stock_code=None):
        self.stock_code = stock_code
        self.order_detail = pd.DataFrame (
            columns=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left',
                     'volume_total', 'direction', 'status', 'order_ref'])

    def update_order_detail(self):
        self.order_detail = context.order_detail.ix[(context.order_detail.stock_code == self.stock_code) and (context.order_detail.status in ['1', '3']), :]
        print "return update order detail"
        print self.order_detail

    def get_order_book(self, side):
        level2_price = context.level2_price.ix[context.level2_price.index == self.stock_code, :]
        level2_vol = context.level2_vol.ix[context.level2_vol.index == self.stock_code, :]
        our_order_book = self.order_detail.groupby ('order_price').sum ('volume_left')
        if side == 'bid':
            total_order_book = pd.Series (level2_vol[5:], index=level2_price[5:])
        if side == 'ask':
            total_order_book = pd.Series (level2_vol[:5], index=level2_price[:5])
        self.order_book = pd.concat ([total_order_book, our_order_book], axis=1, join='left', keys=['total', 'our'])
        self.order_book['other'] = self.order_book['total'] - self.order_book['our']
        print self.order_book



    def calculate_total_order_vol(self):
        vol = self.order_detial['vol_left'].sum ()
        print "pending total volumn:", vol
        return vol



    def calculate_Y(self, side):
        level2_vol = context.level2_vol.ix[context.level2_vol.index == self.stock_code, :]
        if side == 'bid':
            return np.array (level2_vol[:5]).sum () * Y_RATIO
        if side == 'ask':
            return np.array (level2_vol[5:]).sum () * Y_RATIO

    def Y_versus_orderbook(self, y, side):
        order_book_series = self.order_book['other']
        if side == 'bid':
            order_book_series = order_book_series.sort_index (ascending=False)
            accumulation_series = order_book_series.cumsum ()
            try:
                target_price = accumulation_series.index[accumulation_series > y][0]
            except:
                target_price = accumulation_series.index[5] - 0.01
        if side == 'ask':
            order_book_series = order_book_series.sort_index (ascending=True)
            accumulation_series = order_book_series.cumsum ()
            try:
                target_price = accumulation_series.index[accumulation_series > y][0]
            except:
                target_price = accumulation_series.index[5] + 0.01
        return target_price
