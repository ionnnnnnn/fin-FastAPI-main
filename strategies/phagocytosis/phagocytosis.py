def phagocytosis_suggestion(tip_date: int, get_price):
    stock_price_list = get_price(end_date = tip_date, _limit = 6)
    if len(stock_price_list) != 6:
        return "lack", None
    is_pregnant, msg = phagocytosis(stock_price_list[2], stock_price_list[1])
    if is_pregnant:
        state = before_trend_judge(stock_price_list)
        if state != 0:
            if state == 1:
                if msg == "negative":
                    confirmed, msg1 = phagocytosis_negative_confirm(stock_price_list[0], stock_price_list[1]['close'])

                    if confirmed:
                        return "sell", stock_price_list[0]

            if state == -1:
                if msg == "positive":
                    confirmed, msg1 = phagocytosis_tomorrow_confirm(stock_price_list[0], stock_price_list[1]['close'], stock_price_list[1]['open'])
                    if confirmed:
                        return "buy", stock_price_list[0]

    return "hold", stock_price_list[0]


def before_trend_judge(stock_price_list):
    # first日期最早
    first_max = max(stock_price_list[5]['open'], stock_price_list[5]['close'])
    second_max = max(stock_price_list[4]['open'], stock_price_list[4]['close'])
    third_max = max(stock_price_list[3]['open'], stock_price_list[3]['close'])
    first_min = min(stock_price_list[5]['open'], stock_price_list[5]['close'])
    second_min = min(stock_price_list[4]['open'], stock_price_list[4]['close'])
    third_min = min(stock_price_list[3]['open'], stock_price_list[3]['close'])
    if first_max > second_max > third_max and first_min > second_min > third_min:
        return -1 # 前阶段下跌
    elif first_max < second_max < third_max and first_min < second_min < third_min:
        return 1 # 前阶段上涨
    else:
        return 0


def phagocytosis(front_stock, behind_stock):
    # front_upper_len = front_stock['high'] - max(front_stock['open'], front_stock['close'])
    # front_lower_len = min(front_stock['open'], front_stock['close']) - front_stock['low']
    # front_entity_len = abs(front_stock['open'] - front_stock['close'])
    # behind_upper_len = behind_stock['high'] - max(behind_stock['open'], behind_stock['close'])
    # front_lower_len = min(behind_stock['open'], behind_stock['close']) - behind_stock['low']
    # front_entity_len = abs(behind_stock['open'] - behind_stock['close'])
    if front_stock['open'] > front_stock['close'] and behind_stock['open'] < behind_stock['close'] and front_stock['open'] < behind_stock['close'] and front_stock['close'] > behind_stock['open']and 1.2*(front_stock['vol'] )< behind_stock['vol']:
        return True, "positive"
    if front_stock['open'] < front_stock['close'] and behind_stock['open'] > behind_stock['close'] and front_stock['close'] < behind_stock['open'] and front_stock['open'] > behind_stock['close']:
        return True, "negative"
    return False, "none"
def phagocytosis_tomorrow_confirm(stock, close_price, open_price):
    if stock['open'] < stock['close'] and stock['change']>0:
        # 当确认日为阳线
        if stock['close'] > close_price and stock['low'] > close_price:
            return True, 'positive'
    return False, 'none'

def phagocytosis_negative_confirm(stock, close_price):
    if stock['open']>stock['close'] or close_price >stock['close']:
        return True, 'negative'
    return False, 'none'