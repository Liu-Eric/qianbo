###kongfu demo

M_TICKER = '000776'
M_EXCHANGE = EXCHANGE.SZE
SOURCE_INDEX = SOURCE.XTP


def initialize(context):
    print "running initialize"
    context.add_md (source=SOURCE_INDEX)
    context.add_td (source=SOURCE_INDEX)
    context.subscribe (tickers=[M_TICKER], source=SOURCE_INDEX)


def on_tick(context, market_data, source, rcv_time):
    print 'id', market_data.InstrumentID, 'price', market_data.LastPrice, 'BP1', market_data.BidPrice1, 'AP1', market_data.AskPrice1
    context.limit_rid = context.insert_limit_order (source=SOURCE_INDEX,
                                                    ticker=M_TICKER,
                                                    exchange_id=EXCHANGE,
                                                    price=market_data.BidPrice1,
                                                    volume=100,
                                                    direction=DIRECTION.Buy,
                                                    offset=OFFSET.Open)
    print "putting order_id: %s" % context.limit_rid


def on_pos(context, pos_handler, request_id, source, rcv_time):
    print 'running on_pos'
    print request_id
    if request_id == -1:
        print 'first POS', request_id, source, rcv_time
        if pos_handler is None:
            context.set_pos (context.new_pos (source=SOURCE_INDEX), source=SOURCE_INDEX)
    context.print_pos (pos_handler)


def on_rtn_trade(context, rtn_trade, order_id, source, rcv_time):
    print '----on rtn trade----'
    print 'on_rtn_order:', order_id, '$', rtn_trade.OrderStatus, '$', rtn_trade.OrderRef, '$', rtn_trade.InstrumentID, '$', rtn_trade.Price, '$', rtn_trade.Volume
    context.print_pos (context.get_pos (source=SOURCE.CTP))
    context.req_rid = context.req_pos (source=SOURCE.CTP)


def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    print "----on rtn order-----"
    print 'on_rtn_order:', order_id, '$', rtn_order.OrderStatus, '$', rtn_order.OrderRef, '$', rtn_order.InstrumentID, '$', rtn_order.LimitPrice, '$', rtn_order.VolumeTraded, '$', rtn_order.VolumeTotal, '$', rtn_order.VolumeTotalOriginal