"""
黄昏星线策略：一段趋势上涨后，以某条阳线（1）为基础，随后出现一个星线（2），星线后有一跳空阴线（3）且3与2的实体部分不交疊
    1. 1,3 分别为大阳线和大阴线
    2. 1与2、2与3的实体部分不重叠
    3. 2的实体部分较小
操作：
    1. 在2出现时，应当给予关注，停止买入
    2. 当3的收盘价小于1的开盘价与收盘价和的二分之一时，建议卖出
注意：
    1. 这里控制满足大阴线和大阳线的涨跌幅为5%
参考链接：
    https://blog.csdn.net/m0_74754828/article/details/128400386
"""


def evening_star(tip_date: int, get_price):
    stock_price_list = get_price(end_date=tip_date, _limit=3)
    if len(stock_price_list) != 3:
        return "lack", None
    max2 = max(stock_price_list[2]["open"], stock_price_list[2]["close"])
    min1 = min(stock_price_list[1]["open"], stock_price_list[1]["close"])
    max0 = max(stock_price_list[0]["open"], stock_price_list[0]["close"])
    if is_long_black(stock_price_list[0]) and \
            min1 > max(max0, max2) and \
            has_small_body(stock_price_list[1]) and \
            is_long_white(stock_price_list[2]) and \
            stock_price_list[0]["close"] < (stock_price_list[2]["close"] + stock_price_list[2]["open"])/2:
        return "sell", stock_price_list[0]
    return "hold", stock_price_list[0]


# 判断当日k线是否为大阴线，反映出行情强劲的下跌
def is_long_black(stock_price):
    return stock_price["close"]/stock_price["open"] < 0.95


# 实体部分较小
def has_small_body(stock_price):
    return abs(stock_price["open"]-stock_price["close"])/stock_price["close"] < 0.03


def is_long_white(stock_price):
    return stock_price["close"]/stock_price["open"] > 1.05
