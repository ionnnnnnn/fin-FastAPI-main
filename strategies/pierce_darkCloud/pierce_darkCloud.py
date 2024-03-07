def pierce_darkCloud_suggestion(tip_date: int, get_price):
    stock_price_list = get_price(end_date = tip_date, _limit = 6)
    if len(stock_price_list) != 6:
        return "lack", None
    before_trend = before_trend_judge(stock_price_list)
    if before_trend != 0:
        if before_trend == -1:
            if is_pierce(stock_price_list[2], stock_price_list[1]):
                build_line = stock_price_list[2]['open']
                stop_loss_line = stock_price_list[1]['open']
                confirmed, msg = pierce_tomorrow_confirm(stock_price_list[0], build_line, stop_loss_line)
                if confirmed:
                    return "buy", stock_price_list[0]
                else:
                    if msg == 'negative':
                        return 'sell', stock_price_list[0]
        elif before_trend == 1:
            if is_darkCloud(stock_price_list[1], stock_price_list[0]):
                return 'sell', stock_price_list[0]
    return 'hold', stock_price_list[0]


def is_pierce(pre_stock, lat_stock):
    if pre_stock['open'] > pre_stock['close'] and lat_stock['open'] < lat_stock['close']: # 第一天阴线，第二天阳线
        # 阳线开盘价低于前一天最低点
        # 阳线收盘价在前一天阴线实体之内，但高于前一日阴线实体的1/2
        if lat_stock['open'] < pre_stock['low'] and \
                pre_stock['open'] > lat_stock['close'] > 0.5 * (pre_stock['open'] + pre_stock['close']):
            return True
    return False


# 刺透线能否成功取决于后续交易日能否确认成功
# 压力位（建仓位）：大阴线的开盘价
# 支撑位（止损位）：大阳线的开盘价
def pierce_tomorrow_confirm(stock, build_line, stop_loss_line):
    if stock['open'] < stock['close']:
        # 当确认日为阳线，阳线开盘价高于支撑位且收盘价高于压力位，表示刺透线成功，后续可以买入
        if stock['open'] > stop_loss_line and stock['close'] > build_line:
            return True, 'positive'
        elif stock['open'] < stop_loss_line: # 确认日的开盘价跌破支撑位，后续股价下跌概率大，看跌
            return False, 'negative'
    return False, 'none'


def is_darkCloud(pre_stock, lat_stock):
    if pre_stock['open'] < pre_stock['close'] and lat_stock['open'] > lat_stock['close']: # 第一天阳线，第二天阴线
        if lat_stock['close'] < 0.5 * (pre_stock['open'] + pre_stock['close']): # 阴线实体跌穿前一日阳线实体的1/2
            return True
    return False


def before_trend_judge(stocks):
    first_max = max(stocks[5]['open'], stocks[5]['close'])
    second_max = max(stocks[4]['open'], stocks[4]['close'])
    third_max = max(stocks[3]['open'], stocks[3]['close'])
    first_min = min(stocks[5]['open'], stocks[5]['close'])
    second_min = min(stocks[4]['open'], stocks[4]['close'])
    third_min = min(stocks[3]['open'], stocks[3]['close'])
    if first_max > second_max > third_max and first_min > second_min > third_min:
        return -1 # 前阶段下跌
    elif first_max < second_max < third_max and first_min < second_min < third_min:
        return 1 # 前阶段上涨
    else:
        return 0