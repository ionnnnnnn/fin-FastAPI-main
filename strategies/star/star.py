def star_suggestion(tip_date: int, get_price):
    stock_price_list = get_price(end_date=tip_date, _limit=6)
    if len(stock_price_list) != 6:
        return "lack", None
    before_trend, avg_len = trend_judge(stock_price_list)
    status_code = star_type_judge(stock_price_list)
    if status_code == 1 and stock_price_list[0]['close'] > stock_price_list[2]['open'] + abs(
            stock_price_list[2]['open'] - stock_price_list[2]['close']) / 2 and before_trend == -1 \
            and abs(stock_price_list[2]['open'] - stock_price_list[2]['close']) > 1.2 * avg_len:
        return "buy", stock_price_list[0]
    elif status_code == -1 and stock_price_list[0]['close'] < stock_price_list[2]['open'] + abs(
            stock_price_list[2]['open'] - stock_price_list[2]['close']) / 2 and before_trend == 1 \
            and abs(stock_price_list[2]['open'] - stock_price_list[2]['close']) > 1.2 * avg_len:
        return "sell", stock_price_list[0]
    return "hold", stock_price_list[0]


def star_type_judge(stocks):
    star_entity_len = abs(stocks[1]['open'] - stocks[1]['close'])
    after_star_entity_len = abs(stocks[0]['open'] - stocks[0]['close'])
    pre_star_entity_len = abs(stocks[2]['open'] - stocks[2]['close'])
    pre_star_low_len = abs(stocks[2]['low'] - min(stocks[2]['open'], stocks[2]['close']))
    pre_star_up_len = abs(stocks[2]['high'] - max(stocks[2]['open'], stocks[2]['close']))
    is_same = (stocks[0]['open'] - stocks[0]['close']) * (stocks[2]['open'] - stocks[2]['close'])
    if after_star_entity_len > pre_star_entity_len * 0.6 and star_entity_len < pre_star_entity_len * 0.3 and is_same < 0:
        if stocks[0]['open'] < stocks[0]['close'] and morning_jump_judge(stocks, True) and stocks[2]['close'] + \
                pre_star_entity_len / 2 > stocks[1]['high'] and pre_star_low_len < pre_star_entity_len \
                and stocks[2]['low'] > stocks[1]['low']:
            return 1
        elif stocks[0]['open'] > stocks[0]['close'] and morning_jump_judge(stocks, False) and stocks[1]['low'] > \
                stocks[1]['close'] - pre_star_entity_len / 2 and pre_star_up_len < pre_star_entity_len \
                and stocks[2]['high'] < stocks[2]['high']:
            return -1
    else:
        return 0


def morning_jump_judge(stocks, is_morning: bool):
    if is_morning and stocks[1]['high'] > stocks[2]['low'] and max(stocks[1]['open'], stocks[1]['close']) < \
            stocks[2]['close']:
        return True
    elif not is_morning and stocks[1]['low'] < stocks[2]['high'] and min(stocks[1]['open'], stocks[1]['close']) > \
            stocks[2]['close']:
        return True


def trend_judge(stocks):
    first_max = max(stocks[5]['open'], stocks[5]['close'])
    second_max = max(stocks[4]['open'], stocks[4]['close'])
    third_max = max(stocks[3]['open'], stocks[3]['close'])
    first_min = min(stocks[5]['open'], stocks[5]['close'])
    second_min = min(stocks[4]['open'], stocks[4]['close'])
    third_min = min(stocks[3]['open'], stocks[3]['close'])
    avg_len = (abs(stocks[3]['open'] - stocks[3]['close']) + abs(stocks[5]['open'] - stocks[5]['close']) + abs(
        stocks[4]['open'] - stocks[4]['close'])) / 3
    if first_max > second_max > third_max and first_min > second_min > third_min:
        return -1, avg_len
    elif first_max < second_max < third_max and first_min < second_min < third_min:
        return 1, avg_len
    else:
        return 0, avg_len
