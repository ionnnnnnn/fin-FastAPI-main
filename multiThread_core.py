from datetime import datetime, timedelta
import threading
from threading import Lock

from multiThread_db_query import get_all_stock, build_get_price, add_tip, query_tip, get_max_date
from strategy_map import get_strategy_map
from mysql_config import MySQL

stocks = get_all_stock(MySQL)
stock_index = -1
Mode = "current"
Strategy_id = '0'
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
            optimize_stock_analyze(stocks[stock_index], Strategy_id, Mode)


# 核心函数
# 参数介绍
# stock(从数据库中取出的单个股票数据)
# strategy_id是string类型的和strategy_map中对应的Id
# mode是string类型，可以是current，只计算昨日的推荐策略，或者使用YYYYMMDD(20220401)日期，计算从这个日期起每一天的推荐策略
def optimize_stock_analyze(stock, strategy_id: str, mode: str):
    # 从strategy_map中获取到对应的推荐算法函数
    func = get_strategy_map()[strategy_id]["func"]
    end = int((datetime.strptime(str(get_max_date(MySQL)), "%Y%m%d") + timedelta(days=1)).strftime('%Y%m%d'))
    if mode != "current":
        # 计算从mode(YYYYMMDD)开始的每天的推荐
        begin_date = datetime.strptime(mode, "%Y%m%d")
    else:
        # 只计算昨日的推荐
        begin_date = datetime.utcnow() + timedelta(hours=8)
    date = int(begin_date.strftime('%Y%m%d'))

    print("****start strategy_id " + str(strategy_id) + " in day " + str(date))

    stock_id = stock['id']
    stock_code = stock['ts_code']
    # 构建get_price函数查询结果缓存，减少IO，提高速度
    get_price = build_get_price(stock['ts_code'], MySQL)
    print(date)
    print(end)
    while date <= end:
        # 获取推荐算法的返回结果
        tip, data = func(date, get_price)
        # lack表示数据缺失，直接跳过该日的计算
        if tip == "lack":
            date = int((datetime.strptime(str(date), "%Y%m%d") + timedelta(days=1)).strftime('%Y%m%d'))
            continue
        # 如果推荐算法给出了结果，那么直接将结果注入数据库
        elif tip == "buy" or tip == "sell":
            if production:
                add_tip(stock_id, strategy_id, tip, data, MySQL)
                print("%%%%" + strategy_id + " 策略针对stock_id为 " + str(stock_id) + "的股票触发了推荐：" + tip + "\n触发数据为", end="")
            else:
                print(strategy_id + " 策略针对stock_id为 " + str(stock_id) + "的股票触发了推荐：" + tip + "\n触发数据为", end="")
                print(data)
        # 如果推荐算法给出的是hold，则查询前一个推荐结果
        else:
            res = query_tip(stock_id, strategy_id, MySQL)
            # 如果没有查询到之前的推荐，即之前没有任何推荐历史，则直接跳过
            if len(res) == 0:
                date = int((datetime.strptime(str(date), "%Y%m%d") + timedelta(days=1)).strftime('%Y%m%d'))
                continue
            else:
                last_tip = res[0]
            # 如果最近一次的推荐是buy计算收益率和止损率是否超过了预设值，如果超过注入新的推荐策略
            if last_tip['type'] == "buy":
                rate = data['close'] / last_tip['close'] - 1
                if rate <= get_strategy_map()[strategy_id]["stop_loss_rate"]:
                    if production:
                        add_tip(stock_id, strategy_id, "loss_sell", data, MySQL)
                        print("%%%%" + strategy_id + " 策略针对stock_id为 " + str(stock_id) + "的股票触发了推荐：loss_sell\n触发数据为", end="")
                    else:
                        print(strategy_id + " 策略针对stock_id为 " + str(stock_id) + "的股票触发了推荐：loss_sell\n触发数据为", end="")
                        print(data)
                elif rate >= get_strategy_map()[strategy_id]["stop_profit_rate"]:
                    if production:
                        add_tip("%%%%%" + stock_id, strategy_id, "profit_sell", data, MySQL)
                        print(strategy_id + " 策略针对stock_id为 " + str(stock_id) + "的股票触发了推荐：profit_sell\n触发数据为", end="")
                    else:
                        print(strategy_id + " 策略针对stock_id为 " + str(stock_id) + "的股票触发了推荐：profit_sell\n触发数据为", end="")
                        print(data)
        date = int((datetime.strptime(str(date), "%Y%m%d") + timedelta(days=1)).strftime('%Y%m%d'))
    if production:
        print("===== handled: " + str(stock_id) + ": " + stock_code + " =====")


def run_analyze_threads(mode: str, strategy_id: str, threads_num: int, env=True):
    global Mode
    global Strategy_id
    global production
    production = env
    Strategy_id = strategy_id
    Mode = mode
    thread_list = []
    for i in range(threads_num):
        thread = myThread(i, "Thread-" + str(i), i)
        thread.start()
        thread_list.append(thread)
    for i in thread_list:
        i.join()
    global stock_index
    stock_index = -1
