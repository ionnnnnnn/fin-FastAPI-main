from typing import List

import numpy as np
from datetime import datetime, timedelta
import threading
from threading import Lock

from multiThread_db_query import get_all_stock, get_all_tip, update_overall_data, get_all_strategy, drop_and_create
from mysql_config import MySQL

stocks = get_all_stock(MySQL)
stock_index = -1
Strategy_id = 0
lock = Lock()
production = True


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
            store_data(stocks[stock_index], Strategy_id)


def store_data(stock, strategy_id: int):
    stock_id = stock['id']
    all_tip = get_all_tip(stock_id, strategy_id, MySQL)
    today_date = datetime.utcnow() + timedelta(hours=8) - timedelta(days=365)
    date = int(today_date.strftime('%Y%m%d'))
    sell_out_date = 0
    sell_price = 0
    all_count = 0
    match_count = 0
    profit_rates = []
    for tip in all_tip:
        if tip['trade_date'] < date:
            break
        if tip['type'] != "profit_sell" and tip['type'] != "loss_sell":
            all_count += 1
        if tip['is_hit'] == 1:
            match_count += 1
        if tip['type'] == "profit_sell" or tip['type'] == "loss_sell":
            sell_out_date = tip['next_day_date']
            sell_price = tip['next_day_open']
        if tip['type'] == "buy":
            if sell_out_date == sell_price == 0:
                continue
            buy_in_date = tip['next_day_date']
            buy_price = tip['next_day_open']
            if buy_price is None or buy_in_date is None:
                continue
            # interval = datetime.strptime(str(sell_out_date), "%Y%m%d") - datetime.strptime(str(buy_in_date), "%Y%m%d")
            # temp_rate = (sell_price / buy_price - 1) / interval.days
            # profit_rates.append(temp_rate)
    if all_count != 0:
        match_rate = match_count / all_count
    else:
        match_rate = 0
    update_overall_data(stock_id, strategy_id, np.average(profit_rates) * 365 if len(profit_rates) > 0 else 0,
                        match_rate, all_count, MySQL)


def run_overall_threads(threads_num: int, strategy_list: List[int], env=True):
    global Strategy_id
    global production
    production = env
    all_strategy = []
    if len(strategy_list) == 0:
        all_strategy = get_all_strategy(MySQL)
        drop_and_create(MySQL)
    else:
        for item in strategy_list:
            all_strategy.append({'id': item, "func_enabled": 1})
    for strategy in all_strategy:
        if strategy['func_enabled'] == 0:
            continue
        Strategy_id = strategy['id']
        start_threads(threads_num)


def start_threads(threads_num: int):
    thread_list = []
    for i in range(threads_num):
        thread = myThread(i, "Thread-" + str(i), i)
        thread.start()
        thread_list.append(thread)
    for i in thread_list:
        i.join()
    global stock_index
    stock_index = -1
