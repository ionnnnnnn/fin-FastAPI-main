from datetime import datetime, timedelta
from multiThread_core import run_analyze_threads
from multiThread_matching_rate import run_matching_threads
from multiThread_data import run_data_threads
from multiThread_overall import run_overall_threads
from return_index import cal_return_index
from mysql_config import MySQL
from strategy_map import get_strategy_map
from multiThread_db_query import drop_and_create_strategy, update_strategy_info, get_all_strategy


def write_strategy():
    strategies = get_strategy_map()
    strategy_ids = list(strategies.keys())
    strategy_values = list(strategies.values())
    drop_and_create_strategy(MySQL)
    for i in range(0, len(strategy_ids)):
        update_strategy_info(int(strategy_ids[i]), strategy_values[i]['name'], strategy_values[i]['type'], strategy_values[i]['enable'],MySQL)


if __name__ == "__main__":
    write_strategy()
    all_strategy = get_all_strategy(MySQL)
    for strategy in all_strategy:
        print(strategy)
    print(all_strategy)
    # begin_date = datetime.utcnow() + timedelta(hours=8) - timedelta(days=7)
    # date = int(begin_date.strftime('%Y%m%d'))
    # for strategy in all_strategy:
    #     if strategy['func_enabled'] == 0:
    #         continue
    #     strategy_id = str(strategy['id'])
    #     run_analyze_threads("current", strategy_id, 16)
    #     run_matching_threads([], date, strategy_id, 16)
    run_data_threads("current", 16, [])
    # run_overall_threads(16, [])
    # cal_return_index()
