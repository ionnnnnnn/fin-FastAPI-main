import gurobipy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from multiThread_db_query import get_all_overall, get_all_tip_data, update_return_index
from mysql_config import MySQL


class DEA(object):
    def __init__(self, DMUs_Name, X, Y):
        self.m1, self.m1_name, self.m2, self.m2_name = X.shape[1], X.columns.tolist(), Y.shape[1], Y.columns.tolist()
        self.DMUs, self.X, self.Y = gurobipy.multidict(
            {DMU: [X.loc[DMU].tolist(), Y.loc[DMU].tolist()] for DMU in DMUs_Name})
        self.Res = []

    def __CCR_super(self):
        for k in self.DMUs:
            MODEL = gurobipy.Model()
            OE, lambdas, s_negitive, s_positive = MODEL.addVar(), MODEL.addVars(self.DMUs), MODEL.addVars(self.m1), \
                                                  MODEL.addVars(self.m2)
            MODEL.update()
            # 更新变量环境
            MODEL.setObjectiveN(OE, index=0, priority=1)
            # 添加目标函数Model.setObjectiveN()，并且index: 目标函数对应的序号 (默认 0，1，2，…), 以 index=0 作为目标函数的值
            MODEL.setObjectiveN(-(sum(s_negitive) + sum(s_positive)), index=1, priority=0)
            # priority大就先算
            MODEL.addConstrs(gurobipy.quicksum(lambdas[i] * self.X[i][j] for i in self.DMUs if i != k)
                             + s_negitive[j] == OE * self.X[k][j] for j in range(self.m1))
            MODEL.addConstrs(gurobipy.quicksum(lambdas[i] * self.Y[i][j] for i in self.DMUs if i != k)
                             - s_positive[j] == self.Y[k][j] for j in range(self.m2))
            MODEL.setParam('OutputFlag', 0)
            MODEL.optimize()

            id_splits = str(k).split('-')
            self.Res.append(
                {'stock_id': int(id_splits[0]), 'strategy_id': int(id_splits[1]), 'return_index': MODEL.objVal})
            # print(k, MODEL.objVal)

    def dea(self):
        self.__CCR_super()
        return self.Res


def cal_return_index():
    today_date = datetime.utcnow() + timedelta(hours=8) - timedelta(days=365)
    date = int(today_date.strftime('%Y%m%d'))
    overall_list = get_all_overall(MySQL)
    overall_data = dict()
    update_list = []
    for overall in overall_list:
        overall_key = str(overall['stock_id']) + "-" + str(overall['strategy_id'])
        tip_data_list = list(filter(lambda d: d['buy_in_date'] >= date,
                                    get_all_tip_data(overall['stock_id'], overall['strategy_id'], MySQL)))
        if len(tip_data_list) < 2:
            update_list.append(
                {'stock_id': overall['stock_id'], 'strategy_id': overall['strategy_id'], 'return_index': -1})
            continue
        # 求解标准差
        sigma = np.std(list(map(lambda d: d['profit_rate'], tip_data_list)))
        # 构建dataFrame，使用小正数代替负收益产出
        overall_data[overall_key] = [sigma, overall['profit_rate'] if overall['profit_rate'] >= 0 else 0.0001,
                                     overall['match_rate']]
    overall_df = pd.DataFrame(overall_data, index=['sigma', 'profit_rate', 'match_rate']).T
    X = overall_df[['sigma']]
    Y = overall_df[['profit_rate', 'match_rate']]

    dea = DEA(DMUs_Name=overall_df.index, X=X, Y=Y)
    update_list.extend(dea.dea())
    print("====== DEA calculation finished ======")

    for overall_update in update_list:
        update_return_index(overall_update['return_index'], overall_update['stock_id'], overall_update['strategy_id'],
                            MySQL)
    print("====== overall return_index updating finished ======")
