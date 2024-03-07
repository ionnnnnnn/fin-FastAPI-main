from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
from multiThread_core import run_analyze_threads
from multiThread_matching_rate import run_matching_threads, calculate_hit_rate
from multiThread_profit_rate import run_profit_threads

app = FastAPI()


class Run_config(BaseModel):
    date: int
    strategyId: int
    num: Optional[int] = None


class Matching_Rate_Config(BaseModel):
    stocks: List[int]
    date: int
    strategyId: int
    num: Optional[int] = None


class profit_rate_config(BaseModel):
    stocks: List[int]
    date: int
    strategyId: int
    num: Optional[int] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/suggestion/")
async def read_item(data: Run_config):
    if data.num is not None:
        run_analyze_threads(str(data.date), str(data.strategyId), data.num)
    else:
        run_analyze_threads(str(data.date), str(data.strategyId), 16)
        return {"message": "done"}


@app.post("/rate/calculate")
async def read_item(data: Matching_Rate_Config):
    if data.num is not None:
        run_matching_threads(data.stocks, data.date, str(data.strategyId), data.num)
    else:
        run_matching_threads(data.stocks, data.date, str(data.strategyId), 16)
    return {"message": "done"}


@app.get("/rate/query/")
async def query_rate(strategy_id: int, date: Optional[int] = None, stock_id: Optional[int] = None):
    if date is None:
        date = 0
    if stock_id is None:
        stock_id = -1
    flag, rate, count = calculate_hit_rate(stock_id, strategy_id, date)
    return {"success": flag, "rate": rate, "count": count}


@app.post("/rate/profit/")
def calculate_profit_rate(data: profit_rate_config):
    print("calculate" + str(data.strategyId) + " rate")
    if data.num is not None:
        return run_profit_threads(data.stocks, data.date, str(data.strategyId), data.num)
    else:
        return run_profit_threads(data.stocks, data.date, str(data.strategyId), 16)
