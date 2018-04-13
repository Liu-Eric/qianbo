'''
Copyright [2017] [taurus.ai]
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
test limit order and order cancelling for new wingchun strategy system.
you may run this program by:
wingchun strategy -n my_test -p order_cancel_test.py
'''

def initialize(context):
    context.add_md(source=SOURCE.XTP)
    context.ticker = '000001'
    context.exchange_id = EXCHANGE.SZE
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=[context.ticker], source=SOURCE.XTP)
    context.trade = True
    print "----initialization down----"

def on_pos(context, pos_handler, request_id, source, rcv_time):
    if request_id == -1:
        if pos_handler is not None:
            context.print_pos(pos_handler)
        else:
            context.set_pos(context.new_pos(source=SOURCE.XTP))
    else:
        print '----request pos handler----'
        context.print_pos(pos_handler)

def on_tick(context, market_data, source, rcv_time):
    if market_data.InstrumentID == context.ticker and context.trade:
        context.buy_price = market_data.BidPrice3
        context.order_rid = context.insert_limit_order(source=SOURCE.XTP,
                                                     ticker=context.ticker,
                                                     price=context.buy_price,
                                                     exchange_id=context.exchange_id,
                                                     volume=1000,
                                                     direction=DIRECTION.Buy,
                                                     offset=OFFSET.Open)
        print 'putting limit order: %s, stock：%, price: %s' % (context.order_rid,context.ticker,context.buy_price)

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    print '----on rtn order----'
    print "order_id:",order_id,"order_time",rcv_time,"stock:",rtn_order.InstrumentID,"price:",rtn_order.LimitPrice,"trade_vol:",rtn_order.VolumeTraded



def on_rtn_trade(context, rtn_trade, order_id, source, rcv_time):
    print '----on rtn trade----'
    print "order_id:",order_id,"trade_time",rtn_trade.TradeTime,"stock:",rtn_trade.InstrumentID,"price:",rtn_trade.Price,"trade_vol:",rtn_trade.Volume
