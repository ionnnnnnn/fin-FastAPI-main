def kdj_suggestion(tip_date: int, get_price):
    # 天数
    n = 9
    stock_price_list = get_price(end_date=tip_date, _limit=n)
    stock_price_list.reverse()
    if len(stock_price_list) != n:
        return "lack", None
    # 计算kdj
    hn = sorted(stock_price_list, key=lambda x: x['high'], reverse=True)[0]['high']
    ln = sorted(stock_price_list, key=lambda x: x['low'])[0]['low']
    rsv_list = []
    for i in range(len(stock_price_list)):
        rsv_list.append((stock_price_list[i]['close'] - ln) / (hn - ln) * 100)
    k_list, d_list, j_list = [], [], []
    for i in range(len(stock_price_list)):
        if i == 0:
            # 不同平台的初值设置可能不同
            k_list.append(50)
            d_list.append(50)
        else:
            k_list.append(2 / 3 * k_list[i - 1] + 1 / 3 * rsv_list[i])
            d_list.append(2 / 3 * d_list[i - 1] + 1 / 3 * k_list[i])
        j_list.append(3 * k_list[i] - 2 * d_list[i])
    # 考虑K、D值的交叉，1代表金叉，-1代表死叉，0代表无金叉或死叉
    kd_cross_list = []
    for i in range(len(k_list)):
        if i == 0:
            kd_cross_list.append(0)
        if k_list[i] > d_list[i] and k_list[i - 1] >= d_list[i - 1]:
            kd_cross_list.append(1)
        elif k_list[i] < d_list[i] and k_list[i - 1] <= d_list[i - 1]:
            kd_cross_list.append(-1)
        else:
            kd_cross_list.append(0)
    # 返回最近一天的结果
    if kd_cross_list[-1] == 1:
        return "buy", stock_price_list[-1]
    elif kd_cross_list[-1] == 0:
        return "hold", stock_price_list[-1]
    else:
        return "sell", stock_price_list[-1]
