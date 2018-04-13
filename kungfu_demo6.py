import numpy as np
import pandas as pd
STOCK_LIST = ['603025']

class orderBook:
    def __init__(self, stock_code=None):
        self.stock_code = stock_code
        self.order_detail = pd.DataFrame (
            columns=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left',
                     'volume_total', 'direction', 'status', 'order_ref'])

    def update_order_detail(self):
        self.order_detail = context.order_detail.ix[(context.order_detail.stock_code == self.stock_code) and (context.order_detail.status in ['1', '3']), :]
        print "++++++++++return update order detail++++++++++"
        print self.order_detail

    def get_order_book(self, side):
        print "++++++++++calculating order book++++++++++"
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
        print "++++++++++calculate total vol++++++++++"
        vol = self.order_detial['vol_left'].sum ()
        print "pending total volumn:", vol
        return vol



    def calculate_Y(self, side):
        print "++++++++++calculate y++++++++++"
        level2_vol = context.level2_vol.ix[context.level2_vol.index == self.stock_code, :]
        if side == 'bid':
            return np.array (level2_vol[:5]).sum () * Y_RATIO
        if side == 'ask':
            return np.array (level2_vol[5:]).sum () * Y_RATIO

    def Y_versus_orderbook(self, y, side):
        print "++++++++++calculate target price++++++++++"
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

def initialize(context):
    context.add_md(source=SOURCE.XTP)
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=STOCK_LIST, source=SOURCE.XTP)
    context.register_bar(source=SOURCE.XTP, min_interval=1, start_time='09:30:00', end_time='15:00:00')
    context.trade_status = True
    context.lastprice = pd.Series (np.nan, index=STOCK_LIST)
    context.status = pd.Series (True, index=STOCK_LIST)
    context.level2_price = pd.DataFrame (np.nan,columns=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.level2_vol = pd.DataFrame (np.nan,columns=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.order_detail = pd.DataFrame (columns=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left', 'volume_total','direction', 'status', 'order_ref'])
    context.benchmark = orderBook(STOCK_LIST[0])



def on_tick(context, md, source, rcv_time):
    if md.InstrumentID in STOCK_LIST and context.trade:
        context.lastprice.ix[md.InstrumentID] = md.LastPrice
        print "limit_up:",md.UpperLimitPrice,"limit_down:",md.LowerLimitPrice
        if md.LastPrice == md.UpperLimitPrice or md.LastPrice == md.LowerLimitPrice:
            context.status[md.InstrumentID] = False
        context.level2_price.ix[context.level2_price.index == md.InstrumentID, :] = [md.AskPrice5, md.AskPrice4, \
                                                                                 md.AskPrice3, md.AskPrice2, \
                                                                                 md.AskPrice1, md.BidPrice5, \
                                                                                 md.BidPrice4, md.BidPrice3, \
                                                                                 md.BidPrice2, md.BidPrice1]
        context.level2_vol.ix[context.level2_vol.index == md.InstrumentID, :] = [md.AskVolume5, md.AskVolume4, \
                                                                             md.AskVolume3, md.AskVolume2, \
                                                                             md.AskVolume1, md.BidVolume5, \
                                                                             md.BidVolume4, md.BidVolume3, \
                                                                             md.BidVolume2, md.BidVolume1]
        order_id = context.insert_limit_order(source = SOURCE.XTP,\
                                              ticker = md.InstrumentID,\
                                              exchange_id = EXCHANGE.SSE if str(md.InstrumentID)[0] == '6' else EXCHANGE.SZE,\
                                              price = md.BidPrice3,\
                                              volume = 10000000,\
                                              direction = DIRECTION.Buy,\
                                              offset = OFFSET.Open)
        print "putting limit order: %s" % order_id,"stock:",md.InstrumentID,"price:",md.BidPrice3,"volume:",10000000
        context.trade_status = False


def on_bar(context, bars, min_interval, source, rcv_time):
    print "++++++++++bar price++++++++++"
    for ticker, bar in bars.items():
        print ticker, 'o', bar.Open, 'h', bar.High, 'l', bar.Low, 'c', bar.Close
    context.benchmark.update_order_detail()
    context.benchmark.calculate_total_order_vol(side='bid')
    context.benchmark.get_order_book(side='bid')
    context.benchmark.Y_versus_orderbook(side='bid')
    context.benchmark.calculate_Y(side='bid')

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    print "++++++++++on_rtn_order++++++++++"
    print "order_id:",order_id,"stock:",rtn_order.InstrumentID
    print context.order_detail['order_id']
    if order_id in context.order_detail['order_id'].values:
        print "update order detail"
        context.order_detail.ix[context.order_detail.order_id == order_id, 'volume_trade'] = rtn_order.VolumeTraded
        context.order_detail.ix[context.order_detail.order_id == order_id, 'volume_left'] = rtn_order.VolumeTotal
        context.order_detail.ix[context.order_detail.order_id == order_id, 'status'] = rtn_order.OrderStatus
        context.order_detail.ix[context.order_detail.order_id == order_id, 'order_ref'] = rtn_order.OrderRef
    if order_id not in context.order_detail['order_id'].values:
        print "add order detail"
        order = pd.Series ([order_id, rtn_order.InstrumentID, rtn_order.LimitPrice, context.parse_nano (rcv_time), \
                            rtn_order.VolumeTraded, rtn_order.VolumeTotal, rtn_order.VolumeTotalOriginal, \
                            rtn_order.Direction, rtn_order.OrderStatus, rtn_order.OrderRef], \
                           index=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left',\
                                'volume_total', 'direction', 'status', 'order_ref'])
        context.order_detail = context.order_detail.append (order, ignore_index=True)
    print context.order_detail


def on_pos(context, pos_handler, request_id, source, rcv_time):
    print "++++++++++running on_pos++++++++++"
    if (request_id == -1) and (pos_handler is None):
        context.set_pos(context.new_pos(SOURCE.XTP),SOURCE.XTP)
    else:
        context.print_pos(pos_handler)

        
        
