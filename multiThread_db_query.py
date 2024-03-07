import datetime
from DBUtils.PooledDB import PooledDB
# from dbutils.pooled_db import PooledDB
import importlib


# 数据库连接池类，用于创建数据库连接池
class DataBase(object):

    def __init__(self, db_type, config):

        self.__db_type = db_type

        if self.__db_type == 'mysql':
            db_creator = importlib.import_module('pymysql')
        elif self.__db_type == 'sqlserver':
            db_creator = importlib.import_module('pymssql')
        elif self.__db_type == 'oracle':
            db_creator = importlib.import_module('cx_Oracle')
        else:
            raise Exception('unsupported database type ' + self.__db_type)
        self.pool = PooledDB(
            creator=db_creator,
            mincached=0,
            maxcached=0,
            maxconnections=16,
            blocking=True,
            ping=0,
            **config
        )

        # 获取一条数据库链接

    def get_conn(self):
        conn = self.pool.connection()
        cur = conn.cursor()
        return conn, cur

        # 关闭数据库链接

    def close_conn(self, conn, cur):
        cur.close()
        conn.close()

        # 查询数据库

    def select_infor(self, insert):
        conn, cur = self.get_conn()
        try:
            cur.execute(insert)
            return cur.fetchall()
        except BaseException as e:
            print('数据库查询错误')
        finally:
            self.close_conn(conn, cur)

        # 更新数据库

    def update_infor(self, insert):
        conn, cur = self.get_conn()
        try:
            cur.execute(insert)
            conn.commit()
            return True
        except BaseException as e:
            print(f'数据库更新错误{e}')
        finally:
            self.close_conn(conn, cur)

    def execute_query(self, sql, as_dict=True):
        conn = None
        cur = None
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            cur.execute(sql)
            rst = cur.fetchall()
            if rst:
                if as_dict:
                    fields = [tup[0] for tup in cur._cursor.description]
                    return [dict(zip(fields, row)) for row in rst]
                return rst
            return rst

        except Exception as e:
            print('sql:[{}]meet error'.format(sql))
            print(e.args[-1])
            return ()
        finally:
            if conn:
                conn.close()
            if cur:
                cur.close()


# 获取所有股票数据，返回结果为list，每一项为字典，示例：res:[{'id':0000,'name':xxxx}]
# 字典内容和数据库列完全重合
def get_all_stock(db: DataBase):
    sql = "select * from fincode.stock s where is_deleted = 0"
    res = db.execute_query(sql)
    return res


# 构建股票日线获取函数，提供cache进行缓存，不需要高频率访问数据库，提升运行速度
def build_get_price(ts_code: str, db: DataBase):
    sql = "select * from fincode.stock_price where companyId = '%s' order by time desc" % ts_code
    # print(sql)
    cache = db.execute_query(sql)

    # get_price方法会获取到最近limit天的stock_price数据，最近的一天为res[0]
    # rate参数可选，用于匹配率计算时候提取数据
    # 数据类型为list，每个项都是字典，使用方法可以参考我写的realHammer函数
    def get_price(end_date: int, _limit: int, rate=False):
        res = []
        cnt = 0
        if not rate:
            for c in cache:
                if c['time'] < end_date:
                    res += [c]
                    cnt += 1
                if cnt == _limit:
                    break
            if len(res) != _limit:
                return []
            else:
                if res[0]['time'] != int(
                        (datetime.datetime.strptime(str(end_date), "%Y%m%d") - datetime.timedelta(days=1)).strftime(
                            '%Y%m%d')):
                    # print(str(end_date) + "前一日不是交易日或数据丢失") TODO: 这两种情况是否可以分开考虑，不是交易日不需要提示
                    return []
        else:
            # 获取推荐的第二天的股票交易数据
            for i in range(len(cache) - 1, -1, -1):
                if cache[i]['time'] > end_date:
                    res += [cache[i]]
                    if len(res) == 2:
                        break
        return res

    return get_price


# 将策略加入
# 参数stock_id,strategy_id,tip(推荐策略),data(得出策略当天的股票交易数据)，db(数据库连接池引用)
def add_tip(stock_id: int, strategy_id: str, tip: str, data, db: DataBase):
    # print(data)
    sql = "INSERT INTO fincode.stock_tip_daily(stock_id,strategy_id,type,trade_date,high,low,open,close,is_deleted) " \
          "VALUES (%d, %d, '%s', %d,  %f,%f,%f,%f,%d)" % \
          (stock_id, int(strategy_id), tip, data['time'], data['high'], data['low'], data['open'], data['close'], 0)
    db.update_infor(sql)


# 查询之前的策略，用于进行止损卖出和收益卖出操作
def query_tip(stock_id, strategy_id, db):
    sql = "select e.type, e.close from fincode.stock_tip_daily e where stock_id = %d and " \
          "strategy_id=%d order by trade_date desc limit 1" % (int(stock_id), int(strategy_id))
    return db.execute_query(sql)


# 获取数据库中最早的日线数据的日期
def get_min_date(db):
    sql = "select min(time) from fincode.stock_price"
    return db.execute_query(sql, False)[0][0]


# 获取数据库中最新的日线数据的日期
def get_max_date(db):
    sql = "select max(time) from fincode.stock_price"
    return db.execute_query(sql, False)[0][0]


# 获取指定股票指定strategy的所有策略
def get_all_tip(stock_id: int, strategy_id: int, db):
    sql = "select * from fincode.stock_tip_daily where stock_id= %d and strategy_id = %d order by trade_date desc " % (
        stock_id, strategy_id)
    return db.execute_query(sql)


# 通过stock_id来获取股票
def get_stock_by_id(stock_id: int, db):
    sql = "select * from fincode.stock where id = %d" % stock_id
    return db.execute_query(sql)[0]


# 更新买入策略第二天的开盘价格
def update_next_day_data(tip_id: int, price: float, next_day_date: int, is_hit: bool, db):
    sql = ("update fincode.stock_tip_daily set next_day_open=%f,next_day_date=%d,is_hit=1 where id=%d" % (
        price, next_day_date, tip_id)) if is_hit else (
            "update fincode.stock_tip_daily set next_day_open=%f,next_day_date=%d where id=%d" %
            (price, next_day_date, tip_id))
    return db.update_infor(sql)


def query_tip_num(strategy_id: int, stock_id: int, date: int, query_all: bool, db, all_flag):
    if not all_flag:
        sql = "select count(*) from fincode.stock_tip_daily where strategy_id=%d and stock_id=%d and (type='buy' or " \
              "type='sell') and trade_date> %d and next_day_open is not null" % (strategy_id, stock_id, date) \
            if query_all else "select count(*) from fincode.stock_tip_daily where strategy_id=%d and stock_id=%d and (" \
                              "type='buy' or type='sell') and is_hit=1 and trade_date>%d and next_day_open is not null" % (
                                  strategy_id, stock_id, date)
    else:
        sql = "select count(*) from fincode.stock_tip_daily where strategy_id=%d and (type='buy' or " \
              "type='sell') and trade_date> %d and next_day_open is not null" % (strategy_id, date) \
            if query_all else "select count(*) from fincode.stock_tip_daily where strategy_id=%d and (" \
                              "type='buy' or type='sell') and is_hit=1 and trade_date>%d and next_day_open is not null" % (
                                  strategy_id, date)
    return db.execute_query(sql, False)[0][0]


def update_data(sell_tip_id: int, buy_tip_id: int, profit_rate: float, stock_id: int, strategy_id: int,
                buy_in_date: int, sell_out_date: int, db):
    sql = "insert into fincode.stock_tip_data (sell_tip_id, buy_tip_id, profit_rate, stock_id, strategy_id, " \
          "buy_in_date, sell_out_date) VALUES (%d,%d,%f,%d,%d,%d,%d)" % \
          (sell_tip_id, buy_tip_id, profit_rate, stock_id, strategy_id, buy_in_date, sell_out_date)
    db.update_infor(sql)


def get_all_strategy(db):
    sql = "select * from fincode.strategy"
    return db.execute_query(sql)


def drop_and_create(db):
    sql = "TRUNCATE TABLE fincode.stock_tip_overall"
    db.update_infor(sql)


def update_overall_data(stock_id: int, strategy_id: int, profit_rate: float, match_rate: float, all_count: int, db):
    sql = "insert into fincode.stock_tip_overall (stock_id, strategy_id, profit_rate, match_rate,all_count) " \
          "VALUES (%d,%d,%f,%f,%d)" % (stock_id, strategy_id, profit_rate, match_rate, all_count)
    db.update_infor(sql)


def get_all_overall(db):
    sql = "select * from fincode.stock_tip_overall"
    return db.execute_query(sql)


def get_all_tip_data(stock_id: int, strategy_id: int, db):
    sql = "select * from fincode.stock_tip_data where stock_id= %d and strategy_id = %d order by buy_in_date desc " % (
        stock_id, strategy_id)
    return db.execute_query(sql)


def update_return_index(return_index: float, stock_id: int, strategy_id: int, db):
    sql = "update fincode.stock_tip_overall set return_index=%f where stock_id=%d and strategy_id=%d" % (
        return_index, stock_id, strategy_id)
    db.update_infor(sql)


def drop_and_create_strategy(db):
    sql = "TRUNCATE TABLE fincode.strategy"
    db.update_infor(sql)


def update_strategy_info(strategy_id: int, strategy_name: str, strategy_type: str, enable: int, db):
    sql = "insert into fincode.strategy (id, name, type, func_enabled) " \
          "VALUES (%d,\'%s\',\'%s\',%d)" % (strategy_id, strategy_name, strategy_type, enable)
    db.update_infor(sql)
