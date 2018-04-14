import order_operation
import numpy as np
import pandas as pd
n = 10000
STOCK_LIST = ['000001']
ASK_BID_RATIO = 1.01
MININAL_UNIT = 1000
def initialize(context):
    context.add_md(source=SOURCE.XTP)
    context.ticker = '000001'
    context.exchange_id = EXCHANGE.SZE
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=STOCK_LIST, source=SOURCE.XTP)
    context.lastprice = pd.Series (np.nan, index=STOCK_LIST)
    context.level2_price = pd.DataFrame (np.nan,columns=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.level2_vol = pd.DataFrame (np.nan,columns=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.order_detail = pd.DataFrame (columns=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left', 'volume_total','direction', 'status', 'order_ref'])
    context.trade = True
    context.cancel = False
    print "----initialization down----"

def on_pos(context, pos_handler, request_id, source, rcv_time):
    print "----running on_pos-----"
    if request_id == -1:
        if pos_handler is not None:
            context.print_pos(pos_handler)
        else:
            context.set_pos(context.new_pos(source=SOURCE.XTP))
    else:
        print '----request pos handler----'
        context.print_pos(pos_handler)

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    print "+++++++++++++on_rtn_order+++++++++++++++++"
    if order_id in context.order_detail['order_id'].values:
        context.order_detail.ix[context.order_detail.order_id == order_id, 'volume_trade'] = rtn_order.VolumeTraded
        context.order_detail.ix[context.order_detail.order_id == order_id, 'volume_left'] = rtn_order.VolumeTotal
        context.order_detail.ix[context.order_detail.order_id == order_id, 'status'] = rtn_order.OrderStatus
        context.order_detail.ix[context.order_detail.order_id == order_id, 'order_ref'] = rtn_order.OrderRef
        print context.order_detail
    if order_id not in context.order_detail['order_id']:
        order = pd.Series ([order_id, rtn_order.InstrumentID, rtn_order.LimitPrice, context.parse_nano (rcv_time), \
                            rtn_order.VolumeTraded, rtn_order.VolumeTotal, rtn_order.VolumeTotalOriginal, \
                            rtn_order.Direction, rtn_order.OrderStatus, rtn_order.OrderRef], \
                           index=['order_id', 'stock_code', 'order_price', 'order_time', 'volume_trade', 'volume_left',\
                                'volume_total', 'direction', 'status', 'order_ref'])
        context.order_detail = context.order_detail.append (order, ignore_index=True)
        print context.order_detail



def on_tick(context, market_data, source, rcv_time):
    if md.InstrumentID in STOCK_LIST:
        context.lastprice.ix[md.InstrumentID] = md.LastPrice
        context.level2_price.ix[context.level2_price.index == md.InstrumentID, :] = [md.AskPrice5, md.AskPrice4, \
                                                                                 md.AskPrice3, md.AskPrice2, \
                                                                                 md.AskPrice1, md.BidPrice5, \
                                                                                 md.BidPrice4, md.BidPrice3, \
                                                                                 md.BidPrice2, md.BidPrice1]
        context.level2_vol.ix[context.level2_vol.index == md.InstrumentID, :] = [md.AskVolume5, md.AskVolume4, \
                                                                             md.AskVolume3, md.AskVolume2, \
                                                                             md.AskVolume1, md.BidVolume5, \
                                                                             md.BidVolume4, md.BidVolume3, \
     
    if md.InstrumnetID in STOCK_LIST and context.trade:
       put_limit_order(md.InstrumentID,n,md.BidPrice1,DIRECTION.Buy,OFFSET.Open)
       put_limit_order(md.InstrumentID,n,md.BidPrice2,DIRECTION.Buy,OFFSET.Open)
       put_limit_order(md.InstrumentID,n,md.BidPrice3,DIRECTION.Buy,OFFSET.Open)
       context.cancel_target = md.BidPrice3
       put_limit_order(md.InstrumentID,100,md.BidPrice3,DIRECTION.Buy,OFFSET.Open)                                                                      
       put_limit_order(md.InstrumentID,n,md.BidPrice4,DIRECTION.Buy,OFFSET.Open)
       put_limit_order(md.InstrumentID,n,md.BidPrice5,DIRECTION.Buy,OFFSET.Open)
       put_opposite_order(md.InstrumentID,n,DIRECTION.Buy,OFFSET.Open)
       context.trade = False
       context.cancel = True
    if md.InstrumnetID in STOCK_LIST context.cancel:
       cancel_beyond_limit(md.InstrumentID,context.cancel_target_price,DIRECTION.Buy)
       cancel_all(md.InstrumentID)
                                                                                 
                                                                                 
                                                                                 
                                                                                 
                                                                                 
                                                                                 
                                                                                 
                                                                                 
                                                                                 
                                                                                 
