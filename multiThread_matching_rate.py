import threading
from threading import Lock
from typing import List

from mysql_config import MySQL
from multiThread_db_query import get_all_stock, get_stock_by_id, get_min_date, get_all_tip, build_get_price, \
    update_next_day_data, get_max_date, query_tip_num

stocks = []
lock = Lock()
stock_index = -1
strategy_select = '0'
production = True
date = int(get_min_date(MySQL))
max_date = int(get_max_date(MySQL))


class myThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        global stock_index
        print("started " + self.name)
        while True:
            with lock:
                if stock_index < len(stocks) - 1:
                    stock_index += 1
                else:
                    return
            calculate_rate(stocks[stock_index], strategy_select)


# stock_mode为空默认计算所有股票的收益率，或者使用list【stock_id】选定需要计算的股票
# date_mode接受YYYYMMDD字符串作为计算起始日期，或者使用“all”来触发所有日期的计算
# strategy_id接受string作为选定策略，如果需要对多个策略进行计算，请多次请求
# threads_num是使用的计算线程数量
def run_matching_threads(stock_mode: List[int], date_mode: int, strategy_mode: str, threads_num: int, env=True):
    global strategy_select
    strategy_select = strategy_mode
    global production
    production = env
    global stocks
    if len(stock_mode) == 0:
        stocks = get_all_stock(MySQL)
    else:
        for stock_id in stock_mode:
            stocks += [get_stock_by_id(stock_id, MySQL)]
    global date
    date = max(date_mode, date)
    thread_list = []
    for i in range(threads_num):
        thread = myThread(i, "Thread-" + str(i), i)
        thread.start()
        thread_list.append(thread)
    for i in thread_list:
        i.join()
    global stock_index
    stock_index = -1


# 计算预测成功率
def calculate_rate(stock, strategy_mode: str):
    tip_count = 0
    correct_count = 0
    stock_id = stock['id']
    stock_code = stock['ts_code']
    all_tip = get_all_tip(stock_id, int(strategy_mode), MySQL)
    for tip in all_tip:
        if tip['trade_date'] < date:
            break
        if tip['trade_date'] == max_date:
            continue
        tip_id = tip['id']
        flag = False
        tip_count += 1
        get_price = build_get_price(stock_code, MySQL)
        # 如果是推荐卖出检测第二天是否跌了
        next_day = get_price(tip['trade_date'], 0, True)
        if len(next_day) == 0:
            print(str(tip['trade_date']) + "之后的数据缺失")
            continue
        if tip['type'] == "sell":
            if len(next_day) == 1:
                if next_day[0]['open'] >= next_day[0]['close']:
                    flag = True
                    correct_count += 1
            else:
                if min(next_day[1]['open'], next_day[1]['close']) <= next_day[0]['open']:
                    flag = True
                    correct_count += 1
        # 如果是买入策略检测第二天是不是涨了，并且记录第二天的开盘价
        elif tip['type'] == "buy":
            if len(next_day) == 1:
                if next_day[0]['open'] <= next_day[0]['close']:
                    correct_count += 1
                    flag = True
            else:
                if max(next_day[1]['open'], next_day[1]['close']) >= next_day[0]['open']:
                    correct_count += 1
                    flag = True
        price = next_day[0]['open']
        next_day_date = next_day[0]['time']
        if production:
            update_next_day_data(tip_id, price, next_day_date, flag, MySQL)
            print("====" + "tip handled: " + str(correct_count) + "/" + str(tip_count) + "====")
        else:
            print("tip_id为 " + str(tip_id) + "的推荐结果次日即" + str(next_day_date) + "的开盘价为 " + str(price) +
                  "判断结果为 " + str(flag))
    rate = correct_count / tip_count if tip_count != 0 else 0
    print("======" + "stock:" + stock_code + "is handled! Correct Rate is " + str(rate) + "======")


def calculate_hit_rate(stock_id: int, strategy_id: int, begin_date: int):
    if begin_date == 0:
        begin_date = date
    if stock_id == -1:
        all_flag = True
    else:
        all_flag = False
    all_num = query_tip_num(strategy_id, stock_id, begin_date, True, MySQL, all_flag)
    if all_num == 0:
        return False, 0.0, 0
    correct_num = query_tip_num(strategy_id, stock_id, begin_date, False, MySQL, all_flag)
    return True, correct_num / all_num, all_num
