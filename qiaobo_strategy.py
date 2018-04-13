# -*- coding: utf-8 -*-

#导入参数列表
import pandas as pd
import numpy as np
from datetime import timedelta
from parser import parse
from tushare import get_hist_data
import parameters
import get_position
import initialize
import orderBook_class
import indicator_calculation
import order_operation
import on_rtn_order_update

# 待检查：日期是否为从后往前排列，如何处理停牌，拆分
# 待检查：从tushare获取股票是否停牌

def initialize(context):
    context.add_md (source=SOURCE.XTP)
    context.add_td (source=SOURCE.XTP)
    context.subscribe (tickers=[STOCK_LIST], source=SOURCE.XTP)
    # 收盘后调整交易状态（最后收盘后自动退出）
    #计算历史价格均价
    #加载参数
    initialization(TARGET_MKTVAL,TARGET_NUM)

def on_tick(context, md, source, rcv_time):
    update_price(md)
    current_time = parse (context.parse_nano (context.get_nano ()))
    if context.initialization == True:
        if context.lastprice.notnull().sum() == len(STOCK_LIST):
            if context.unfavor_orderid != None:
                cancel_last_unfavorable ()
            indicator = calculate_indicator ()
            context.initialization = False
            context.time = current_time
        else:
            continue
    else:
        if (current_time - context.time).seconds > UPDATE_INTERVAL:
            if context.unfavor_orderid != None:
                cancel_last_unfavorable ()
            indicator = calculate_indicator ()
            context.time = current_time


    #买入操作
    context.benchmark.update_order_datail()
    if (context.benchmark.order_detail.shape[0] > 0) and (context.benchmark.stock_code != indicator['benchmark']['stock_code']):
        print "benchamrk stock changes"
        cancell_all(context.benchmark_stock)
        检查是否撤单成功
        context.benchmark.stock_code == None
        context.benchmark.reset_order_book()
    #判断当前是否有买方挂单，是否触发买入交易
    if context.benchmark.order_detail.shape[0] == 0:
        print "there are no pending buy orders"
        #获取当前可用资金？可用资金是否已经包含现金
        if (context.cash +context.cash_available - CASH_WITHDRAW) >= MINIMAL_UNIT:
            print "cash:",context.cash,"cash_available:",context.cash_available
            context.benchmark.stock_code = indicator['benchmark']['stock_code']
            context.benchmark.update_order_detail(context.order_detail)
            X = np.min((context.cash + context.cash_available - CASH_WITHDRAW),indicator['benchmark']['trade_available']) // context.last_price[indicator['benchmark']['stock_code']]
            Y = context.benchmark.calculate_Y(indicator['benchmark']['level2_vol'],side = 'bid')
            N = np.min(X,Y)
            print "X",X,"Y",Y,"N",N
            context.benchmark.get_order_book(side ='bid')
            target_price = context.benchmark.Y_versus_order_book(Y,side ='bid')
            put_limit_order(indicator['benchmark']['stock_code'],N,target_price,DIRECTION.Buy,OFFSET.Open)
            if X > Y:
                n = X - Y
                put_opposite_order(indicator['benchmark']['stock_code'],n,DIRECTION.Buy,OFFSET.Open)
    if (context.benchmark.order_detail.shape[0] > 0) and (context.benchmark.stock_code == indicator['benchmark']['stock_code']):
        print "there has been pending buy orders"
        context.benchmark.update_order_detail (context.order_detail)
        pending_vol = context.benchmark.calculate_total_order_vol()
        pending_mktval = pending_vol * context.last_price[indicator['benchmark']['stock_code']]
        X = np.min ((context.cash + context.cash_available +  pending_mktval- CASH_WITHDRAW), indicator['benchmark']['trade_available']) // context.last_price[indicator['benchmark']['stock_code']]
        Y = context.benchmark.calculate_Y (indicator['benchmark']['level2_vol'], side='bid')
        N = np.min (X, Y)
        print "X", X, "Y", Y, "N", N
        context.get_order_book (side='bid')
        target_price = context.benchmark.Y_versus_order_book (Y, side='bid')
        cancel_beyond_limit(indicator['benchmark']['stock_code'],target_price,DIRECTION.Buy)
        检查是否撤单成功
        更新可用资金
        context.benchmark.update_order_detail(context.order_detail)
        pending_vol = context.benchmark.calculate_total_order_vol()
        n = N - pending_vol
        确定挂单规则
        更行可用资产
        buy_available = (context.cash +context.cash_available - CASH_WITHDRAW)//context.last_price[indicator['benchmark']['stock_code']]
        print "n",n,"buy_available",buy_available
        if n <= buy_available:
            put_limit_order(indicator['benchmark']['stock_code'],n,target_price,DIRECTION.Buy,OFFSET.Open)
            input_opposite_order(indicator['benchmark']['stock_code'],buy_available - n ,DIRECTION.Buy,OFFSET.Open)
        else:
            cancel_one_by_one(indicator['benchmark']['stock_code'],n - buy_available,side = 'bid')
            put_limit_order (indicator['benchmark']['stock_code'], n, target_price, DIRECTION.Buy, OFFSET.Open)

    检查卖出条件
    context.superme.update_order_detial(context.order_detail)
    if (indicator['holding_ratio'][0] > indicator['holding_ratio'][1]) or context.holding_ratios[-1] < TARGET_HOLDING_RATIO:
        print "sell condition is not satisfied"
        if context.superme.order_detail.shape[0] > 0:
            print "there has been pending sell orders"
            cancel_all(context.superme.stock_code)
            #检查是否全部撤单成功
        context.superme.stock_code = None
    else:
        if context.superme.stock_code != indicator['superme']['stock_code'] and context.superme.order_detail.shape[0] > 0:
            print "superme stock changes"
            cancel_all (context.superme.stock_code)
            # 检查是否全部撤单成功
            context.superme.stock_code = indicator['superme']['stock_code']
            context.superme.reset_order_book()
         #更新新持仓最优股票order_detail和order_book
        context.superme.update_order_detial(context.order_detail)
        if context.superme.order_detail.shape[0] == 0:
            print "there are no pending sell orders"
            a = indicator['superme']['mktval_available']
            b = context.cash + context.cash_available -CASH_WITHDRAW
            c = MINIMAL_UNIT
            d = indicator['benchmark']['trade_available']
            if (a + b - c) <= d:
                X = a
            else:
                X = d - b
            X = X // context.last_price[indicator['superme']['stock_code']]
            Y = context.superme.calculate_Y(indicator['superme']['level2_vol'], side='ask')
            N = np.min(X,Y)
            print "X",X,"Y",Y,"N",N
            context.superme.get_order_book (side='ask')
            target_price = context.superme.Y_versus_orderbook (Y, side='ask')
            put_limit_order (indicator['superme']['stock_code'], N, target_price, DIRECTION.Sell, OFFSET.Open)
            if X > Y:
                n = X - Y
            put_opposite_order (indicator['superme']['stock_code'], n, DIRECTION.Sell, OFFSET.Open)
        else:
            pending_vol = context.superme.calculate_total_order_vol()
            a = context.superme_mktval_available + pending_vol * context.last_price[indicator['superme']['stkcode']]
            b = context.cash + context.cash_available - CASH_WITHDRAW
            c = MINIMAL_UNIT
            d = context.benchmark_trade_available
            if (a + b - c) <= d:
                X = a
            else:
                X = d - b
            X = X // context.last_price[indicator['superme']['stock_code']]
            Y = calculate_Y (side='ask')
            N = np.min (X, Y)
            print "X", X, "Y", Y, "N", N
            context.superme.get_order_book (side='ask')
            target_price = context.superme.Y_versus_orderbook (Y, side='ask')
            cancel_beyond_limit (context.superme_stock, target_price, MINIMAL_UNIT, DIRECTION.Sell)
            #检查是否撤单成功
            #更新order_detail和order_book
            context.superme.update_order_detial(context.order_detail)
            pending_vol =  context.superme.calculate_total_order_vol()
            n = N - pending_vol
            sell_available = get_position(context,context.superme_stock)[1]
            print "n", n, "buy_available", buy_available
            if n <= sell_available:
                put_limit_order(context.superme_stock, n, target_price, DIRECTION.Sell, OFFSET.Open)
                input_opposite_order(context.superme_stock, sell_available - n, DIRECTION.Sell, OFFSET.Open)
            else:
                cancel_one_by_one (context.superme.stock_code, n - sell_available, side='ask')
                put_limit_order (indicator['superme']['stock_code'], n, target_price, DIRECTION.Sell, OFFSET.Open)

def on_pos(context, pos_handler, request_id, source, rcv_time):
    if (request_id == -1) and (pos_handler is None):
        context.set_pos (context.new_pos (SOURCE.XTP), SOURCE.XTP)
    else:
        context.data['vol'] = context.data['stock_code'].map (lambda x: get_position (x)[0])
        context.data['vol_available'] = context.data['stock_code'].map (lambda x: get_position (x)[1])


#测试脚本
if __name__ == '__main__':