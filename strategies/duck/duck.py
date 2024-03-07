import numpy as np

MA_20_MONOTONE = 0
PERIOD_LEN = 30
SHAPE_X_DELTA = 0.2
SHAPE_X_BASE = 0.5
SHAPE_Y = 0.25


def duck(tip_date: int, get_price):
    day_k_list = get_price(end_date=tip_date, _limit=PERIOD_LEN + 60)  # 60天均线向前追溯，当日index为0
    if len(day_k_list) != PERIOD_LEN + 60:
        return "lack", None
    day_close = list(map(lambda k: k['close'], day_k_list))
    ma_60, ma_20, diff = [], [], []
    for i in range(PERIOD_LEN):
        ma_60.append(np.mean(day_close[i:i + 60]))
        ma_20.append(np.mean(day_close[i:i + 20]))
        diff.append(ma_20[i] - ma_60[i])
    if diff[1] < 0 or ma_20[1] >= ma_20[0]:
        return "hold", day_k_list[0]  # 不能跌穿 且 短期均线要有拉起
    cross_flag, cross_i = 0, -1
    for i in range(2, PERIOD_LEN - 1):
        if diff[i] * diff[i + 1] <= 0:
            cross_flag, cross_i = 1, i  # 两条均线出现交叉
            break
    if not cross_flag:
        return "hold", day_k_list[0]  # 没有交叉不推荐
    shape_flag, max_idx = check_trend(ma_60, ma_20, cross_i)
    if shape_flag and not max_idx == 1:
        if diff[max_idx] == 0:
            return "hold", day_k_list[0]
        shape_x, shape_y = (cross_i - max_idx) / (cross_i - 1), diff[1] / diff[max_idx]
        if SHAPE_X_BASE - SHAPE_X_DELTA <= shape_x <= SHAPE_X_BASE + SHAPE_X_DELTA:
            if shape_y <= SHAPE_Y:
                return "buy", day_k_list[0]
    return "hold", day_k_list[0]


def check_trend(ma_60, ma_20, end_idx):
    # 长期均线上扬
    for i in range(1, end_idx - 1):
        if ma_60[i] < ma_60[i + 1]:
            return 0, None
    ma_20_max = np.max(ma_20[2:end_idx + 1])
    max_idx = ma_20.index(ma_20_max)
    # 短期均线在最高点前持续上扬
    for i in range(max_idx, end_idx - 1):
        if ma_20[i] < ma_20[i + 1]:
            return 0, None
    # 控制短期均线拉回部分是否需要单调下降
    if MA_20_MONOTONE:
        for i in range(1, max_idx):
            if ma_20[i] > ma_20[i + 1]:
                return 0, None
    return ma_20_max, max_idx
