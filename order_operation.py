import numpy as np
import pandas as pd

def cancel_all(stock_code):
    order_list = context.order_detail.ix[(context.order_detail.stock_code == stock_code) and (context.order_detail.status in ['1','3']),'order_id'].values
    for order_id in order_list:
        context.cancel_rid = context.cancel_order (source=SOURCE.XTP, order_id=order_id)

def cancel_beyond_limit(stock_code,price,direction):
    if direction == DIRECTION.Buy:
        order_list = context.order_detail.ix[(context.order_detail.stock_code == stock_code) \
                                            and (context.order_detail.status in ['1', '3'])\
                                            and (context.order_detail.volume_left > MINIMAL_UNIT)\
                                            and (context.order_detail.price < price), 'order_id'].values
    if direction == DIRECTION.Sell:
        order_list = context.order_detail.ix[(context.order_detail.stock_code == stock_code) \
                                             and (context.order_detail.status in ['1', '3']) \
                                             and (context.order_detail.volume_left > MINIMAL_UNIT) \
                                             and (context.order_detail.price > price), 'order_id'].values
    for order_id in order_list:
        context.cancel_rid = context.cancel_order (source=SOURCE.XTP, order_id=order_id)

def put_limit_order(stock_code,n,price,direction,offset):
    context.rid = context.insert_limit_order (source=SOURCE.XTP,\
                                              ticker=stock_code,\
                                              exchange_id=EXCHANGE.SHE if str(stock_code)[0] == '6' else EXCHANGE.SZE,\
                                              price=price,\
                                              volume=n,\
                                              direction=direction,\
                                              offset=offset)


def put_opposite_order(stock_code,n,direction,offset):
    vol_series = context.level2_vol.ix[context.level2_vol.index == stock_code,:]
    price_series = context.level2_price.ix[context.level2_price.index == stock_code,:]
    if float(level2_price[5]  / float(level2_price[5] ) < ASK_BID_RATIO:
        if direction == DIRECTION.Buy:
            vol = np.min(n,vol_series[4])
            context.rid = context.insert_fak_order (source=SOURCE.XTP, \
                                                    ticker=stock_code, \
                                                    exchange_id=EXCHANGE.SHE if str (stock_code)[0] == '6' else EXCHANGE.SZE, \
                                                    price=level2_price[5] , \
                                                    volume=vol, \
                                                    direction=direction, \
                                                    offset=offset)
        if direction == DIRECTION.Sell:
            vol = np.min (n, vol_series[5])
            context.rid = context.insert_fak_order (source=SOURCE.XTP, \
                                                    ticker=stock_code, \
                                                    exchange_id=EXCHANGE.SHE if str (stock_code)[0] == '6' else EXCHANGE.SZE, \
                                                    price=level2_price[4], \
                                                    volume=vol, \
                                                    direction=direction, \
                                                    offset=offset)

def cancel_last_unfavorable():
    for i in context.unfavor_orderid:
        context.unfavor_orderid.pop (i)
        if context.order_detail.ix[context.order_detail['order_id'] == i,'status'] in ['1','3']:
            context.cancel_rid = context.cancel_order (source=SOURCE.XTP, order_id=i)


def cancel_one_by_one(stock,target_vol,side):
    order_detail = context.order_detail.ix[(context.order_detail['stock_code'] == stock) and (context.order_detail['status'] in ['1','3']),:]
    if side == 'bid':
        order_detail = order_detail.sort_value(by = ['order_price','order_time'],ascending = [True,True])
    else:
        order_detail = order_detail.sort_value(by=['order_price','order_time'],ascending =[False,True])
    for i in order_detail.index:
        target_vol = target_vol - order_detail.ix[i,'volume_left']
        context.cancel_rid = context.cancel_order (source=SOURCE.XTP, order_id=order_detail.ix[i,'order_id'])
        if target_vol <= 0:
            break
