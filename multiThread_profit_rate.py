import numpy as np
import threading
import json
import datetime
from threading import Lock
from typing import List

from mysql_config import MySQL
from multiThread_db_query import get_all_stock, get_stock_by_id, get_min_date, get_all_tip, get_max_date

stocks = []
lock = Lock()
stock_index = -1
strategy_select = '0'
date = int(get_min_date(MySQL))
max_date = int(get_max_date(MySQL))
data = {}
res = json.loads(json.dumps(data))


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
def run_profit_threads(stock_mode: List[int], date_mode: int, strategy_mode: str, threads_num: int):
    global strategy_select
    strategy_select = strategy_mode
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
    # return json.dumps(res, ensure_ascii=False)
    global data
    all_sum = round(return_sum(data) / len(stocks), 2)
    data["all"] = all_sum
    temp = sorted(data.items(), key=lambda kv: kv[1],reverse=True)
    output = {k: v for k, v in temp}
    global stock_index
    stock_index = -1
    data = {}
    return output


def calculate_rate(stock, strategy_id: str):
    stock_id = stock['id']
    profit_rates = []
    all_tip = get_all_tip(stock_id, int(strategy_id), MySQL)
    sell_date = 0
    sell_price = 0
    for tip in all_tip:
        if tip['next_day_open'] is None:
            continue
        if tip['type'] == 'profit_sell' or tip['type'] == 'loss_sell':
            sell_price = tip['next_day_open']
            sell_date = tip['next_day_date']
        elif tip['type'] == 'buy':
            if sell_date == 0:
                continue
            temp_price = tip['next_day_open']
            temp_date = tip['next_day_date']
            interval = datetime.datetime.strptime(str(sell_date), "%Y%m%d") - datetime.datetime.strptime(str(temp_date),
                                                                                                         "%Y%m%d")
            temp_rate = (sell_price / temp_price - 1) / interval.days
            profit_rates.append(temp_rate)
    print("====" + str(stock_id) + " is handled====")
    # global res
    # res[str(stock_id)] = profit_rate
    global data
    data[str(stock_id)] = round(np.average(profit_rates) * 365 * 100, 2) if len(profit_rates) > 0 else 0


def return_sum(dict_data):
    value_sum = 0
    for i in dict_data:
        value_sum = value_sum + dict_data[i]

    return value_sum
