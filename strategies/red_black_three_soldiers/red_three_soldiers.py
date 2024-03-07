PERIOD_LEN = 30  # 以三十天为基准检查股票是否处于低位横盘或高位横盘


def red_black_three_soldiers_suggestion(tip_date: int, get_price):
    stock_price_list = get_price(end_date=tip_date, _limit=PERIOD_LEN)
    if len(stock_price_list) != PERIOD_LEN:
        # 如果股票数据不足三十天，不做低位横盘或高位横盘的检查
        stock_price_list = get_price(end_date=tip_date, _limit=6)
        if len(stock_price_list) != 6:
            return "lack", None
        is_flag, msg = is_red_or_black(stock_price_list)
        if is_flag:
            state = before_trend_judge(stock_price_list)
            if state != 0:
                if state == 1:
                    if msg == "negative":
                        return "sell", stock_price_list[0]
                if state == -1:
                    if msg == "positive":
                        return "buy", stock_price_list[0]
        return "hold", stock_price_list[0]

    is_flag, msg = is_red_or_black(stock_price_list)
    if is_flag:
        state1 = before_trend_judge(stock_price_list)
        state2 = check_horizontal_price_movement(stock_price_list)
        if state1 != 0 or state2 != 0:
            if state1 == 1 or state2 == 1:
                if msg == "negative":
                    return "sell", stock_price_list[0]
            if state1 == -1 or state2 == 1:
                if msg == "positive":
                    return "buy", stock_price_list[0]
    return "hold", stock_price_list[0]


# 以三十天为基准检查股票是否处于低位横盘或高位横盘
def check_horizontal_price_movement(stock_price_list):
    period_max_price = stock_price_list[0]['close']  # 记录周期内的股价高点
    period_min_price = stock_price_list[0]['close']  # 记录周期内的股价低点
    for item in stock_price_list:
        price = item['close']
        if price > period_max_price:
            period_max_price = price
        if price < period_min_price:
            period_min_price = price

    # 以红黑三兵线为基准向前追溯10天，判断这10天股价是否处于一个高价或低价的位置呈现箱体震荡
    high_pos = True
    low_pos = True
    avg = stock_price_list[3]['close']
    for i in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        price = stock_price_list[i]['close']
        if high_pos:
            if 0.8 * avg <= price <= 1.2 * avg and price >= 2 * period_min_price:
                pass
            else:
                high_pos = False
        if low_pos:
            if 0.8 * avg <= price <= 1.2 * avg and price <= 0.5 * period_max_price:
                pass
            else:
                low_pos = False

        avg = (avg * (i - 3) + price) / (i - 2)

    if high_pos:
        return 1  # 高位横盘
    if low_pos:
        return -1  # 低位横盘
    return 0


# 以3天为基准检查股票是否处于阶段下跌或阶段上涨
def before_trend_judge(stock_price_list):
    first_max = max(stock_price_list[5]['open'], stock_price_list[5]['close'])
    second_max = max(stock_price_list[4]['open'], stock_price_list[4]['close'])
    third_max = max(stock_price_list[3]['open'], stock_price_list[3]['close'])
    first_min = min(stock_price_list[5]['open'], stock_price_list[5]['close'])
    second_min = min(stock_price_list[4]['open'], stock_price_list[4]['close'])
    third_min = min(stock_price_list[3]['open'], stock_price_list[3]['close'])
    if first_max > second_max > third_max and first_min > second_min > third_min:
        return -1  # 前阶段下跌
    elif first_max < second_max < third_max and first_min < second_min < third_min:
        return 1  # 前阶段上涨
    else:
        return 0


# 判断最近三天的k线是否呈现红黑三兵的特征
def is_red_or_black(stock_price_list):
    is_red, msg = judge_red(stock_price_list)
    if is_red:
        return True, "positive"  # 未来看好
    is_black, msg = judge_black(stock_price_list)
    if is_black:
        return True, "negative"  # 未来看跌

    return False, "none"


# 红三兵线特征 (股票顺序 3 2 1)
# 1收盘 > 2收盘 > 3收盘
# 1收盘 > 1开盘 > 2实体的一半
# 2收盘 > 2开盘 > 3实体的一半
# 3收盘 > 3开盘
# 上下影线尽可能短
def judge_red(stock_price_list):
    flag1 = stock_price_list[0]['close'] > stock_price_list[1]['close'] > stock_price_list[2]['close']
    flag2 = stock_price_list[0]['close'] > stock_price_list[0]['open'] > 0.5 * (
            stock_price_list[1]['open'] + stock_price_list[1]['close'])
    flag3 = stock_price_list[1]['close'] > stock_price_list[1]['open'] > 0.5 * (
            stock_price_list[2]['open'] + stock_price_list[2]['close'])
    flag4 = stock_price_list[2]['close'] > stock_price_list[2]['open']

    flag5 = judge_hatch(stock_price_list)

    if flag1 and flag2 and flag3 and flag4 and flag5:
        return True, "positive"  # 未来看好
    else:
        return False, "none"


# 黑三兵线特征 (股票顺序 3 2 1)
# 1收盘 < 2收盘 < 3收盘
# 1收盘 < 1开盘 < 2实体的一半
# 2收盘 < 2开盘 < 3实体的一半
# 3收盘 < 3开盘
# 上下影线尽可能短
def judge_black(stock_price_list):
    flag1 = stock_price_list[0]['close'] < stock_price_list[1]['close'] < stock_price_list[2]['close']
    flag2 = stock_price_list[0]['close'] < stock_price_list[0]['open'] < 0.5 * (
            stock_price_list[1]['open'] + stock_price_list[1]['close'])
    flag3 = stock_price_list[1]['close'] < stock_price_list[1]['open'] < 0.5 * (
            stock_price_list[2]['open'] + stock_price_list[2]['close'])
    flag4 = stock_price_list[2]['close'] < stock_price_list[2]['open']

    flag5 = judge_hatch(stock_price_list)

    if flag1 and flag2 and flag3 and flag4 and flag5:
        return True, "negative"  # 未来看跌
    else:
        return False, "none"


def judge_hatch(stock_price_list):
    entity_len1 = abs(stock_price_list[0]['open'] - stock_price_list[0]['close'])
    upper_len1 = stock_price_list[0]['high'] - max(stock_price_list[0]['open'], stock_price_list[0]['close'])
    lower_len1 = min(stock_price_list[0]['open'], stock_price_list[0]['close']) - stock_price_list[0]['low']

    entity_len2 = abs(stock_price_list[1]['open'] - stock_price_list[1]['close'])
    upper_len2 = stock_price_list[1]['high'] - max(stock_price_list[1]['open'], stock_price_list[1]['close'])
    lower_len2 = min(stock_price_list[1]['open'], stock_price_list[1]['close']) - stock_price_list[1]['low']

    entity_len3 = abs(stock_price_list[2]['open'] - stock_price_list[2]['close'])
    upper_len3 = stock_price_list[2]['high'] - max(stock_price_list[2]['open'], stock_price_list[2]['close'])
    lower_len3 = min(stock_price_list[2]['open'], stock_price_list[2]['close']) - stock_price_list[2]['low']

    flag5 = entity_len1 * 0.3 > max(lower_len1, upper_len1) and \
            entity_len2 * 0.3 > max(lower_len2, upper_len2) and \
            entity_len3 * 0.3 > max(lower_len3, upper_len3)

    return flag5
