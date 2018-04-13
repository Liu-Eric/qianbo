import numpy as np
import pandas as pd

STOCK_LIST = ['000776', '600398', '601800', '600137', '600163']
TARGET_NUM = 5
TARGET_MKTVAL = 1000000
MINIMAL_UNIT = 1000
FAST_HOLDING = 3
SLOW_HOLDING = 9
Y_RATIO = 0.5
ASK_BID_RATIO = 1.01
TARGET_HOLDING_RATIO = 1.2

from tushare import get_hist_data

def get_position(stock):
    pos_handler = context.get_pos(SOURCE.XTP)
    if stock in pos_handler.get_tickers():
        vol = pos_handler.get_net_tot(stock)
        vol_available = pos_handler.get_net_yd(stock)
        return (vol,vol_available)
    else:
        return (0,0)

def initialize(context):
    context.add_md(source=SOURCE.XTP)
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=STOCK_LIST, source=SOURCE.XTP)
    context.register_bar(source=SOURCE.CTP, min_interval=1, start_time='09:30:00', end_time='15:00:00')
    hist_mean = {'short_mean': {}, 'long_mean': {}}
    for i in STOCK_LIST:
        hist = get_hist_data (i)
        short_mean = np.mean (hist.ix[:22, 'close'].values)
        long_mean = np.mean (hist.ix[:44, 'close'].values)
        hist_mean['short_mean'][i] = short_mean
        hist_mean['long_mean'][i] = long_mean
    context.data = pd.DataFrame (hist_mean, index=STOCK_LIST, columns=['short_mean', 'long_mean'])
    context.data['last_price'] = np.nan
    context.data['vol'] = np.nan
    context.data['vol_available'] = np.nan
    context.data['target_mktval'] = TARGET_MKTVAL
    context.stock_list = ['000776', '600398', '601800', '600137', '600163']
    context.lastprice = pd.Series (np.nan, index=STOCK_LIST)
    context.status = pd.Series (True, index=STOCK_LIST)
    context.level2_price = pd.DataFrame (np.nan,columns=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.level2_vol = pd.DataFrame (np.nan,columns=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.holding_ratios = []
    context.order_detail = pd.DataFrame (columns=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left', 'volume_total','direction', 'status', 'order_ref'])



def on_tick(context, md, source, rcv_time):
    if md.InstrumentID in STOCK_LIST:
        context.lastprice.ix[md.InstrumentID] = md.LastPrice
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
    if context.lastprice.notnull ().sum () == 5:
        context.data['last_price'] = context.lastprice.values
        context.data['status'] = context.status
        context.data['vol'] = context.data['stock_code'].map (lambda x: get_position (x)[0])
        context.data['vol_available'] = context.data['stock_code'].map (lambda x: get_position (x)[1])
        context.data['mktval'] = context.data['vol'] * context.data['last_price']
        context.data['mktval_available'] = context.data['vol_available'] * context.data['last_price']
        context.data['trade_available'] = context.data['target_mktval'] - context.data['mktval']
        context.data['trade_available'] = context.data['trade_available'].map(lambda x:np.where(x>MINIMAL_UNIT,x,0))
        context.data['fast'] = context.data['last_price'] / context.data['short_mean']
        context.data['slow'] = context.data['last_price'] / context.data['long_mean']
        context.data['fast_base'] = context.data.ix[context.data['trade_available'] > 0, 'fast'].min ()
        context.data['slow_base'] = context.data.ix[context.data['trade_available'] > 0, 'slow'].min ()
        context.data['fast_relative'] = context.data['fast'] / context.data['fast_base']
        context.data['slow_relative'] = context.data['slow'] / context.data['slow_base']
        context.data['agg'] = context.data['fast_relative'] + context.data['slow_relative']
        agg_base = context.data.ix[context.data['trade_available']>0,'agg'].min()
        context.data['agg_base'] = agg_base
        context.data['agg_relative'] = context.data['agg'] / context.data['agg_base']
        holding_ratio = context.data.ix[context.data['mktval_available'] > 0, 'agg_relative'].max ()
        context.holding_ratios.append (holding_ratio)
        benchmark_stock = context.data.index[context.data.agg_base == agg_base]
        superme_stock = context.data.index[context.data.agg == holding_ratio]
        context.indicator_result = {
            'benchmark': {'stock_code': benchmark_stock, \
                          'trade_available': context.data.ix[context.data.index == benchmark_stock, 'trade_available'], \
                          'level2_vol': context.level2_vol.iloc[context.level2_vol.index == benchmark_stock,:], \
                          'level2_price': context.level2_price.iloc[context.level2_price.index == benchmark_stock, :]}, \
            'superme': {'stock_code': superme_stock, \
                        'mktval_available': context.data.ix[context.data.index == superme_stock, 'mktval_available'], \
                        'level2_vol': context.level2_vol.iloc[context.level2_vol.index == superme_stock, :], \
                        'level2_price': context.level2_price.iloc[context.level2_price.index == superme_stock, :]}}
        if len (context.holding_ratios) >= SLOW_HOLDING:
            holding_ratio_fast = np.array (context.holding_ratios[-3:]).mean ()
            holding_ratio_slow = np.array (context.holding_ratios[-9:]).mean ()
            context.indicator_result['holding_ratio'] = (holding_ratio_fast, holding_ratio_slow)
        else:
            context.indicator_result['holding_ratio'] = (None, None)

    if md.InstrumentID in context.stock_list:
        order_id = context.insert_limit_order(source = SOURCE.XTP,\
                                              ticker = md.InstrumentID,\
                                              exchange_id = EXCHANGE.SSE if str(md.InstrumentID)[0] == '6' else EXCHANGE.SZE,\
                                              price = md.LastPrice,\
                                              volume = 100000,\
                                              direction = DIRECTION.Buy,\
                                              offset = OFFSET.Open)
        print "order id:",order_id,"stock:",md.InstrumentID,"price:",md.LastPrice,"volume:",100000
        context.stock_list.remove(md.InstrumentID)


def on_bar(context, bars, min_interval, source, rcv_time):
    print "++++++++++bar price++++++++++"
    for ticker, bar in bars.items():
        print ticker, 'o', bar.Open, 'h', bar.High, 'l', bar.Low, 'c', bar.Close
    print context.data
    print context.indicator_result

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
        context.data['vol'] = context.data['stock_code'].map(lambda x:get_position(x)[0])
        context.data['vol_available'] = context.data['stock_code'].map(lambda x:get_position(x)[1])
        print "++++++++++initialize pos handler++++++++++++"
        print context.data

        