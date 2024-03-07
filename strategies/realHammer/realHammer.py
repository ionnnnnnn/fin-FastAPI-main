def hammer_suggestion(tip_date: int, get_price):
    stock_price_list = get_price(end_date=tip_date, _limit=5)
    if len(stock_price_list) != 5:
        return "lack", None
    if is_hammer_test(stock_price_list[1]):
        state = before_hammer_trend(stock_price_list)
        if state != 2:
            if state == 1:
                if stock_price_list[1]['close'] > stock_price_list[0]['open'] > stock_price_list[0]['close']:
                    return "sell", stock_price_list[0]
                else:
                    return "hold", stock_price_list[0]
            if state == -1:
                if stock_price_list[1]['close'] < stock_price_list[0]['open'] < stock_price_list[0]['close']:
                    return "buy", stock_price_list[0]
                else:
                    return "hold", stock_price_list[0]
        return "hold", stock_price_list[0]
    return "hold", stock_price_list[0]


def before_hammer_trend(stock_price_list):
    four_max = max(stock_price_list[4]['open'], stock_price_list[4]['close'])
    three_max = max(stock_price_list[3]['open'], stock_price_list[3]['close'])
    two_max = max(stock_price_list[2]['open'], stock_price_list[2]['close'])
    four_min = min(stock_price_list[4]['open'], stock_price_list[4]['close'])
    three_min = min(stock_price_list[3]['open'], stock_price_list[3]['close'])
    two_min = min(stock_price_list[2]['open'], stock_price_list[2]['close'])
    if four_max > three_max > two_max and four_min > three_min > two_min:
        return -1
    elif four_max < three_max < two_max and four_min < three_min < two_min:
        return 1
    else:
        return 2


def before_hammer_trend_test(stock_price_list):
    if (stock_price_list[2]['open'] - stock_price_list[2]['close']) * (
            stock_price_list[3]['open'] - stock_price_list[3]['close']) > 0 and \
            (stock_price_list[2]['open'] - stock_price_list[2]['close']) * (
            stock_price_list[4]['open'] - stock_price_list[4]['close']) > 0:
        return -1 if stock_price_list[2]['open'] - stock_price_list[2]['close'] > 0 else 1
    return 2


def is_hammer_test(stock):
    entity_len = abs(stock['open'] - stock['close'])
    lower_len = min(stock['open'], stock['close']) - stock['low']
    upper_len = stock['high'] - max(stock['open'], stock['close'])
    return True if (lower_len > 2 * entity_len and entity_len * 0.3 > upper_len) or \
                   (upper_len > 2 * entity_len and entity_len * 0.3 > lower_len) else False
