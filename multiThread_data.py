from datetime import datetime, timedelta
import threading
from threading import Lock
from typing import List

from multiThread_db_query import get_all_stock, get_all_tip, update_data, get_all_strategy
from mysql_config import MySQL

stocks = get_all_stock(MySQL)
stock_index = -1
Strategy_id = 0
Mode = "history"
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
    date = 0
    if Mode == "current":
        today_date = datetime.utcnow() + timedelta(hours=8)
        date = int(today_date.strftime('%Y%m%d'))
    sell_tip_id = 0
    sell_out_date = 0
    sell_price = 0
    for tip in all_tip:
        if tip['type'] == "profit_sell" or tip['type'] == "loss_sell":
            if Mode == "current" and tip['trade_date'] != date:
                break
            sell_tip_id = tip['id']
            sell_out_date = tip['next_day_date']
            sell_price = tip['next_day_open']
        if tip['type'] == "buy":
            if sell_tip_id == sell_out_date == sell_price == 0:
                continue
            buy_tip_id = tip['id']
            buy_in_date = tip['next_day_date']
            buy_price = tip['next_day_open']
            profit_rate = sell_price / buy_price - 1
            update_data(sell_tip_id, buy_tip_id, profit_rate, stock_id, strategy_id, buy_in_date, sell_out_date, MySQL)


def run_data_threads(mode: str, threads_num: int, strategy_list: List[int], env=True):
    global Mode
    global Strategy_id
    global production
    Mode = mode
    production = env
    all_strategy = []
    if len(strategy_list) == 0:
        all_strategy = get_all_strategy(MySQL)
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
