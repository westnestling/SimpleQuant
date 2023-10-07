import pandas as pd
from pandas import DataFrame
import tushare as ts
from config.global_config import TU_SHARE_TOKEN

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


class TuShareTool:
    def __init__(self, token=TU_SHARE_TOKEN):
        self.token = token
        ts.set_token(self.token)
        self.pro = ts.pro_api()

    def get_stock_data(self, symbol, start_date, end_date):
        """
        获取指定股票的历史行情数据
        :param symbol: 股票代码，例如'000001.SZ'表示平安银行
        :param start_date: 起始日期，格式为'YYYYMMDD'
        :param end_date: 结束日期，格式为'YYYYMMDD'
        :return: 股票的历史行情数据，DataFrame类型
        """
        data = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
        return data

