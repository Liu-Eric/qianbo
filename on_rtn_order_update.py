# -*- coding: utf-8 -*-
"""
构建策略委托记录，记录每一笔委托交易状态，并且在on_rtn_order函数回调时更新
on_rtn_order函数会在拒绝、排队、部分成交、全部成交、撤销时触发
委托策略记录写在一个dataframe里面，命名为context.order_detail
"""
import numpy as np
import pandas as pd

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    if order_id in context.order_detail['order_id'].values:
        context.order_detail.ix[context.order_detail.order_id == order_id,'volume_trade'] = rtn_order.VolumeTraded
        context.order_detail.ix[context.order_detail.order_id == order_id,'volume_left'] = rtn_order.VolumeTotal
        context.order_detail.ix[context.order_detail.order_id == order_id,'status'] = rtn_order.OrderStatus
        context.order_detail.ix[context.order_detail.order_id == order_id,'order_ref'] = rtn_order.OrderRef
    if order_id not in context.order_detail['order_id'].values:
        order = pd.Series([order_id,rtn_order.InstrumentID,rtn_order.LimitPrice,context.parse_nano(rcv_time),\
                          rtn_order.VolumeTraded,rtn_order.VolumeTotal,rtn_order.VolumeTotalOriginal,\
                          rtn_order.Direction,rtn_order.OrderStatus,rtn_order.OrderRef],\
                          key = ['order_id','stock_code','order_price','order_time','volume_trade','volume_left','volume_total','direction','status','order_ref'])
        context.order_detail.append(order,ignore_index = True)


#测试脚本
if __name__ == '__main__':
    pass