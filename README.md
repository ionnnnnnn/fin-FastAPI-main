# 说明

**读完readme之后一定要完整阅读所有代码中的注释！！！**

**已经删除了所有文件中的main函数，运行方式参考[策略本地运行](#run)，请不要再添加main函数导致版本冲突！！！**

本项目使用了fastapi作为框架，main.py为主入口。



## 功能点

- [x] 推荐算法接口
- [x] 匹配率接口
- [x] 年化利率接口

## 接口说明

### 推荐算法接口

启动fastapi之后可以访问[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)来查看交互式文档

~~但是并未将内部算法暴露为接口，先不要看main.py中的任何内容和代码~~

已经完成fastapi接口开发，数据要求如下

```bash
{
  "date": int, #是YYYYMMDD格式的代表日期的字符串，可以使用“current”来触发昨日的推荐策略计算
  "strategyId": int, #是对应的strategy的ID
  "num": int #启动的线程数量，是可选参数，默认16线程运行
}
```



![image-20220412032803155](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220412032803155.png)

postman请求截图如下

![image-20220412032923071](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220412032923071.png)

### 匹配率运算接口

```bash
{
  "stocks": [
    0,1,2
  ], #是一个int类型的数组，每一个int对应的是stock_id，如果需要全量计算传入空数组即[]即可
  "date": int,#是int类型的YYYYMMDD格式的日期，如20220201会从这个时间开始对推荐算法的匹配率进行计算
  "strategyId": int,#是对应的strategy的ID
  "num": int #启动的线程数量，是一个可选参数，默认16线程
}
```



![image-20220412033110321](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220412033110321.png)

postman请求截图

![image-20220412033212786](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220412033212786.png)

### 匹配率请求接口

参数参考之后的postman截图即可，其中后两个未启用的参数可以传入也可以不传入

![image-20220409222924760](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220409222924760.png)

postman请求截图

![image-20220409223031549](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220409223031549.png)

### 年化利率计算接口

```bash
{
  "stocks": [
    0,1,2
  ], #是一个int类型的数组，每一个int对应的是stock_id，如果需要全量计算传入空数组即[]即可
  "date": int,#是int类型的YYYYMMDD格式的日期，如20220201会从2022年2月1日开始对推荐算法的匹配率进行计算
  "strategyId": int,#是对应的strategy的ID
  "num": int #启动的线程数量，是一个可选参数，默认16线程
}

# 返回数据说明
# 会返回所有请求的stock_id对应年化利率百分比的json例如
{
    "542": 2619.76,
    "3862": 1890.42,
    "4266": 1837.24,
    "403": 1292.71,
    "2094": 1269.01,
    "3666": 1150.58,
    "346": 1133.24,
    "345": 1091.88
}
字典按照降序排列，有每一个指定stock_id对应的百分比，同时有一个"all"对应的百分比，是这些请求的stock的平均值
```



![image-20220412033411293](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220412033411293.png)

postman请求截图

![image-20220412033346689](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220412033346689.png)

## 运行

```bash
pip install -r requirements.txt
```

> 我在创建项目的时候使用的是python3.10.4

### FastAPI模块

启动指令：uvicorn main:app --reload

或者使用pycharm配置如下即可

![image-20220406223449860](https://icimence-blog.oss-cn-beijing.aliyuncs.com/image-20220406223449860.png)

### 数据库配置

在项目根目录下新建`mysql_config.py`文件，并对应自己需要连接的数据库进行调整，一下示例对应的是我们的远程服务器**（还是建议使用本地数据库，因为访问量非常大）**

```python
from multiThread_db_query import DataBase

# 配置本地数据库，需要自己进行修改
MySQL = DataBase(
    'mysql', {'user': 'root', 'host': '116.63.159.1', 'password': 'FinGra2022#', 'database': 'fincode', 'port': 3306}
)
```

### 策略本地运行
<div id="run">在项目根目录下创建文件</div>

`local_driver.py`，内容如下：

```python
from multiThread_core import run_analyze_threads
from multiThread_matching_rate import run_matching_threads
from multiThread_profit_rate import run_profit_threads

if __name__ == "__main__":
    # 运行推荐算法，参数如下
    # YYYYMMDD起始日期
    # 策略ID
    # 线程数量
    # 生产模式，False代表调试模式，True为生产环境
    run_analyze_threads("20220201", '2', 16, False)
    # 运行推荐结果匹配检测，参数如下
    # LIST【INT】指定stock_id，空表示全量检测
    # 策略ID
    # 线程数量
    # 生产模式，False代表调试模式，True为生产环境
    # 注意运行之前需要将推荐策略注入数据库，否则会导致没有数据读入
    run_matching_threads([], 20220201, '2', 16, False)
    # 计算收益率，返回dict，建议使用fastapi接口进行计算，有利于数据展示
    # run_profit_threads([], 20220201, '0', 16)


```

可以自己决定内容来达到自己的运行目的

## 目录结构

核心的框架文件是`multiThread_core.py`和`multiThread_db_query.py`

`strategies`文件夹中是推荐算法文件

~~主函数在multiThread_core.py中，直接运行主函数即可~~，运行查看<a href="#run">策略本地运行</a>模块

## 开发推荐策略

在strategies文件夹中添加算法，需要注意入参必须保持一致，下面给一个示例

```python
# tip_date是整数类型的日期（YYYYMMDD），get_price是构建完成的查询函数
def hammer_suggestion(tip_date: int, get_price):
    # todo:推荐算法内容
```

如果只进行新策略的开发，不需要关注参数怎么传入，保持参数一致，能够正常使用即可

在完成了推荐算法的编写之后需要找到`strategy_map.py`文件，依据给出的示例续写。



