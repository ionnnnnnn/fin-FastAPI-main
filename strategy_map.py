from strategies.eveningStar.eveningStar import evening_star
from strategies.morningStar.morningStar import morning_star
from strategies.phagocytosis.phagocytosis import phagocytosis_suggestion
from strategies.realHammer.realHammer import hammer_suggestion
from strategies.duck.duck import duck
from strategies.star.star import star_suggestion
from strategies.kdj.kdj import kdj_suggestion
from strategies.macd.macd import macd_suggestion
from strategies.pregnancy.pregnancy import pregnancy_suggestion
from strategies.pierce_darkCloud.pierce_darkCloud import pierce_darkCloud_suggestion
from strategies.red_black_three_soldiers.red_three_soldiers import red_black_three_soldiers_suggestion


def get_strategy_map():
    strategy_map = {
        # 键：strategyId
        '0': {
            # 函数参数，将判定买/卖点的函数填入
            "func": hammer_suggestion,
            # 策略名称
            "name": "K线锤子",
            # 策略类型
            "type": "all",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '1': {
            # 函数参数，将判定买/卖点的函数填入
            "func": duck,
            # 策略类型
            "type": "buy",
            # 策略名称
            "name": "均线鸭嘴",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '2': {
            # 函数参数，将判定买/卖点的函数填入
            "func": star_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "K线流星",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '3': {
            # 函数参数，将判定买/卖点的函数填入
            "func": pregnancy_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "母子线",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '4': {
            # 函数参数，将判定买/卖点的函数填入
            "func": pierce_darkCloud_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "刺破乌云顶盖",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '5': {
            # 函数参数，将判定买/卖点的函数填入
            "func": macd_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "macd",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 0
        },
        '6': {
            # 函数参数，将判定买/卖点的函数填入
            "func": kdj_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "kdj",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 0
        },
        '7': {
            # 函数参数，将判定买/卖点的函数填入
            "func": phagocytosis_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "多空吞噬线",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '8': {
            # 函数参数，将判定买/卖点的函数填入
            "func": morning_star,
            # 策略类型
            "type": "buy",
            # 策略名称
            "name": "启明星线",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '9': {
            # 函数参数，将判定买/卖点的函数填入
            "func": evening_star,
            # 策略类型
            "type": "sell",
            # 策略名称
            "name": "黄昏星线",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
        '10': {
            # 函数参数，将判定买/卖点的函数填入
            "func": red_black_three_soldiers_suggestion,
            # 策略类型
            "type": "all",
            # 策略名称
            "name": "红黑三兵",
            # 止损卖点，损失率超过这个数量会进行卖出
            "stop_loss_rate": -0.10,
            # 收益卖点，收益率超过这个数量会进行卖出
            "stop_profit_rate": 0.12,
            # 是否启用该算法
            "enable": 1
        },
    }
    return strategy_map
