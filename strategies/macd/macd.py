def macd_suggestion(tip_date: int, get_price):
    # 天数
    n = 9
    stock_price_list = get_price(end_date=tip_date, _limit=n)
    stock_price_list.reverse()
    if len(stock_price_list) != n:
        return "lack", None
    # 更改对不同的参数选择
    terms = {'short': 9, 'long': 26, 'mid': 12}
    ema_short_list = cal_ema(stock_price_list, terms['short'])
    ema_long_list = cal_ema(stock_price_list, terms['long'])
    dif_list = cal_dif(ema_short_list, ema_long_list)
    dea_list = cal_dea(dif_list, terms['mid'])
    bar_list = cal_bar(dif_list, dea_list)
    # 1代表金叉，-1代表死叉，0代表无金叉或死叉
    cross_list = []
    for i in range(len(bar_list)):
        if i == 0:
            cross_list.append(0)
        if bar_list[i] > 0 > bar_list[i - 1]:
            cross_list.append(1)
        elif bar_list[i] < 0 < bar_list[i - 1]:
            cross_list.append(-1)
        else:
            cross_list.append(0)
    # 返回最近一天的结果
    if cross_list[-1] > 0:
        return "buy", stock_price_list[-1]
    elif cross_list[-1] == 0:
        return "hold", stock_price_list[-1]
    else:
        return "sell", stock_price_list[-1]


def cal_ema(stock_price_list, term):
    ema_list = []
    for i in range(len(stock_price_list)):
        if i == 0:
            ema_list.append(stock_price_list[i]['close'])
        else:
            ema_list.append(ema_list[i - 1] * (term - 1) / (term + 1) + stock_price_list[i]['close'] * 2 / (term + 1))
    return ema_list


def cal_dif(ema_short_list, ema_long_list):
    dif_list = []
    for i in range(len(ema_short_list)):
        dif_list.append(ema_short_list[i] - ema_long_list[i])
    return dif_list


def cal_dea(dif_list, term):
    dea_list = []
    for i in range(len(dif_list)):
        if i == 0:
            dea_list.append(dif_list[i])
        else:
            dea_list.append(dea_list[i - 1] * (term - 1) / (term + 1) + dif_list[i] * 2 / (term + 1))
    return dea_list


def cal_bar(dif_list, dea_list):
    bar_list = []
    for i in range(len(dif_list)):
        bar_list.append((dif_list[i] - dea_list[i]) * 2)
    return bar_list
