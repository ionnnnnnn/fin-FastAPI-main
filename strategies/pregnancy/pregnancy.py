def pregnancy_suggestion(tip_date: int, get_price):
    stock_price_list = get_price(end_date = tip_date, _limit = 5)
    if len(stock_price_list) != 5:
        return "lack", None
    is_pregnant, msg = is_pregnancy(stock_price_list[1], stock_price_list[0])
    if is_pregnant:
        state = before_trend_judge(stock_price_list)
        if state != 0:
            if state == 1:
                if msg == "negative":
                    return "sell", stock_price_list[0]
            if state == -1:
                if msg == "positive":
                    return "buy", stock_price_list[0]
    return "hold", stock_price_list[0]


def before_trend_judge(stock_price_list):
    # first日期最早
    first_max = max(stock_price_list[4]['open'], stock_price_list[4]['close'])
    second_max = max(stock_price_list[3]['open'], stock_price_list[3]['close'])
    third_max = max(stock_price_list[2]['open'], stock_price_list[2]['close'])
    first_min = min(stock_price_list[4]['open'], stock_price_list[4]['close'])
    second_min = min(stock_price_list[3]['open'], stock_price_list[3]['close'])
    third_min = min(stock_price_list[2]['open'], stock_price_list[2]['close'])
    if first_max > second_max > third_max and first_min > second_min > third_min:
        return -1 # 前阶段下跌
    elif first_max < second_max < third_max and first_min < second_min < third_min:
        return 1 # 前阶段上涨
    else:
        return 0


def is_pregnancy(mother_stock, child_stock):
    mother_upper_len = mother_stock['high'] - max(mother_stock['open'], mother_stock['close'])
    mother_lower_len = min(mother_stock['open'], mother_stock['close']) - mother_stock['low']
    mother_entity_len = abs(mother_stock['open'] - mother_stock['close'])
    if mother_entity_len * 0.3 > max(mother_lower_len, mother_upper_len): # 母线的影线如果有，不能太长
        if mother_stock['open'] > mother_stock['close']: # 母线是阴线
            if child_stock['open'] < child_stock['close']: # 子线是阳线
                if mother_stock['close'] < child_stock['low'] and mother_stock['open'] > child_stock['high']: # 母线实体包裹子线全部
                    return True, "positive" # 未来看好
        if mother_stock['open'] < mother_stock['close']: # 母线是阳线
            if child_stock['open'] > child_stock['close']: # 子线是阴线
                if mother_stock['open'] < child_stock['low'] and mother_stock['close'] > child_stock['high']: # 母线实体包裹子线全部
                    return True, "negative" # 未来看跌
    return False, "none"