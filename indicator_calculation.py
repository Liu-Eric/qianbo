import numpy as np
import pandas as pd
from tushare import get_hist_data

def calculate_hist_mean():
    hist_mean = {'short_mean':{},'long_mean':{}}
    for i in STOCK_LIST:
        hist = get_hist_data(i)
        short_mean = np.mean(hist.ix[:SHORT_PERIOD,'close'].values)
        long_mean = np.mean(hist.ix[:LONG_PERIOD,'close'].values)
        hist_mean['short_mean'][i] = short_mean
        hist_mean['long_mean'][i] = long_mean
        return pd.DataFrame(hist_mean,index = stock_list,columns=['short_mean', 'long_mean'])

def calculate_indicator():
    context.data['last_price']= context.lastprice.values
    context.data['status'] = context.status
    #更新股票仓位、可用仓位
    context.data['vol'] = context.data['stock_code'].map (lambda x: get_position (x)[0])
    context.data['vol_available'] = context.data['stock_code'].map (lambda x: get_position (x)[1])
    context.data['mktval'] = context.data['vol'] * context.data['last_price']
    context.data['mktval_available'] = context.data['vol_available'] * context.data['last_price']
    ###计算TARGET_MKTVAL
    context.target_mktval = context.data.ix[context.data.status == True,'mktval'].sum() / float(context.status.sum())
    context.data['trade_available'] = context.data['target_mktval'] - context.data['mktval']
    context.data['trade_available'] = context.data['trade_available'].map (lambda x: np.where (x > MINIMAL_UNIT, x, 0))
    context.data['fast'] = context.data['last_price'] / context.data['short_mean']
    context.data['slow'] = context.data['last_price'] / context.data['long_mean']
    context.data['fast_base'] = context.data.ix[context.data['trade_available'] > 0, 'fast'].min ()
    context.data['slow_base'] = context.data.ix[context.data['trade_available'] > 0, 'slow'].min ()
    context.data['fast_relative'] = context.data['fast'] / context.data['fast_base']
    context.data['slow_relative'] = context.data['slow'] / context.data['slow_base']
    context.data['agg'] = context.data['fast_relative'] + context.data['slow_relative']
    agg_base = context.data.ix[context.data['trade_available'] > 0, 'agg'].min ()
    context.data['agg_relative'] = context.data['agg'] / agg_base
    holding_ratio = context.data.ix[context.data['mktval_available'] > 0, 'agg_relative'].max()
    context.hold_ratios.append (holding_ratio)
    benchmark_stock = context.data.index[context.data.agg_base == agg_base]
    superme_stock = context.data.index[context.data.agg == holding_ratio]
    context.indicator_result = {
        'benchmark': {'stock_code': benchmark_stock, \
                      'trade_available': context.data.ix[context.data.index == benchmark_stock, 'trade_available'], \
                      'level2_vol': context.level2_vol.iloc[context.level2_vol.index == benchmark_stock, :], \
                      'level2_price': context.level2_price.iloc[context.level2_price.index == benchmark_stock, :]}, \
        'superme': {'stock_code': superme_stock, \
                    'mktval_available': context.data.ix[context.data.index == superme_stock, 'mktval_available'], \
                    'level2_vol': context.level2_vol.iloc[context.level2_vol.index == superme_stock, :], \
                    'level2_price': context.level2_price.iloc[context.level2_price.index == superme_stock, :]}}
    if len(context.holding_ratios) >= SLOW_HOLDING:
        holding_ratio_fast = np.array (context.hold_ratios[-FAST_HOLDING:]).mean ()
        holding_ratio_slow = np.array (context.hold_ratios[-SLOW_HOLDING:]).mean ()
        indicator_result['holding_ratio'] = (holding_ratio_fast,holding_ratio_slow)
    else:
        indicator_result['holding_ratio'] = (None,None)
    return indicator_result

def update_price(md):
    context.lastprice[md.InstrumentID] = md.LastPrice
    if md.LastPrice == md.UpperLimitPrice or md.LastPrice == md.LowerLimitPrice:
        context.status[md.InstrumentID] = False
    print context.level2_price.ix[[context.level2_price.index == md.InstrumentID,:]
    context.level2_price.ix[context.level2_price.index == md.InstrumentID,:] = [md.AskPrice5, md.AskPrice4,\
                                                                                md.AskPrice3, md.AskPrice2,\
                                                                                md.AskPrice1, md.BidPrice5,\
                                                                                md.BidPrice4, md.BidPrice3,\
                                                                                md.BidPrice2, md.BidPrice1]
    print context.level2_price.ix[[context.level2_price.index == md.InstrumentID,:]
    print context.level2_vol.ix[[context.level2_vol.index == md.InstrumentID,:]
    context.level2_vol.ix[context.level2_vol.index == md.InstrumentID,:] = [md.AskVolume5, md.AskVolume4,\
                                                                            md.AskVolume3, md.AskVolume2,\
                                                                            md.AskVolume1, md.BidVolume5,\
                                                                            md.BidVolume4, md.BidVolume3,\
                                                                            md.BidVolume2, md.BidVolume1]
