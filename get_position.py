
"""
获取某只股票最新仓位和可用仓位
获取现金和可用资金
"""
def get_position(stock):
    pos_handler = context.get_pos(SOURCE.XTP)
    if stock in pos_handler.get_tickers():
        vol = pos_handler.get_net_tot(stock)
        vol_available = pos_handler.get_net_yd(stock)
        return (vol,vol_available)
    else:
        return (0,0)

def get_cash():
    pass

if __name__ == '__main__':
    pass