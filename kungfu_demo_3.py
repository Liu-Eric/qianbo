STOCK_LIST = ['000776', '600398', '601800', '600137', '600163']

def initialize(context):
    print '---running initialize---'
    context.add_md(source=SOURCE.XTP)
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=STOCK_LIST, source=SOURCE.XTP)
    print "---initialize down---"

def on_tick(context, md, source, rcv_time):
    print "---running on_tick---"
    print 'id', md.InstrumentID, 'price', md.LastPrice

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    print 'on_rtn_order:', order_id, '$', rtn_order.OrderStatus, rtn_order.OrderRef, rtn_order.InstrumentID


def on_pos(context, pos_handler, request_id, source, rcv_time):
    print "---running on_pos---"
    print "pos_handler.dump"
    print pos_handler.dump()
    for i in STOCK_LIST:
        pos_handler.add_pos(i,DIRECTION.Buy,100,100),SOURCE.XTP)
    print pos_handler.dump
    context.print_pos(pos_handler)
    pos_str = {"Cost":{"000776":[14852.0,4.4556,0.0,0.0,0.0,0.0],"600398":[14852.0,4.4556,0.0,0.0,0.0,0.0]},\
    "FeeSetup":{"future":{"ctr_multi":200,"fee_multi":[2.3e-05,0.00069,2.3e-05],"min_fee":0.0,"type":"amount"},\
                "future_exotic":null,"stock":{"ctr_multi":1,"fee_multi":0.0003,"min_fee":0.0,"type":"amount"}},\
    "Pos":{"000776":[900,900,0,0,0,0],"600398":[800,800,0,0,0,0]},\
               "Source":15,"ok":true}
    print pos_str
    pos_handler.load(pos_str)
    context.set_pos(pos_handler,SOURCE.XTP)
    context.print_pos(pos_handler)
