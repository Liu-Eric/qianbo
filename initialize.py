
"""
策略初始化，完成以下工作：
策略运行中会修改的参数赋值给context相关属性
生成context.last_price，用以记录股票最新价格数据
生成context.level2_price，用以记录股票最新level2价格数据
生成context.level2_vol，用以记录股票最新了vevel2挂单数据
生成context.status，用以记录当前股票状态（正常/停牌/涨停/跌停）
生成context.holding_ratios，用以记录最优持仓指标
生成context.order_detail，用以记录账户下单信息及状态
生成context.benchmark、context.superme，用以记录基准股票/持仓最优股票相关数据
生成context.benchmark_stock、context.superme_stock，用以记录基准股票/持仓最优股票
生成context.data，用以记录指标计算过程中数据，计算历史均价，仓位/可用仓位
"""

import numpy as np
import pandas as pd
import orderBook_class
import indicator_calculation
from paser import parse

def initialization(target_mktval,target_num):
    #将策略运行中会修改的参数赋值给context相关属性
    #获取现金和可用资金
    """
    cash,cash_available = get_cash()
    context.cash = cash
    context.cash_available = cash_available
    """
    context.target_mktval = target_mktval
    context.targte_num = target_num
    context.time = parse(context.parse_nano(context.get_nano()))
    context.initialization = True

    context.lastprice = pd.Series (np.nan, index=STOCK_LIST)
    context.status = pd.Series (True, index=STOCK_LIST)
    context.level2_price = pd.DataFrame (np.nan,colums=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.level2_vol = pd.DataFrame (np.nan,colums=['ask5', 'ask4', 'ask3', 'ask2', 'ask1', 'bid1', 'bid2', 'bid3', 'bid4','bid5'], index=STOCK_LIST)
    context.holding_ratios = []

    context.benchmark = OrderBook()
    context.superme = OrderBook()

    context.order_detail = pd.DataFrame(columns =  ['order_id','stock_code','order_price','order_time','volume_trade','volume_left','volume_total','direction','status','order_ref'])

    context.data = calculate_hist_mean()
    context.data['last_price'] = np.nan
    context.data['vol'] = np.nan
    context.data['vol_available'] = np.nan


if __name__ == '__main__':
    pass

