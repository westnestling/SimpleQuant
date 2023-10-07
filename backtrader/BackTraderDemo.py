from datetime import datetime
import backtrader as bt
import pandas as pd
from tushares.TuShareTool import TuShareTool

# 初始化 TuShareTool
tushare = TuShareTool()

# 获取股票数据
def get_data(code='600483.SH', start_date='2022-10-01', end_date='2023-10-01'):
    df = tushare.get_stock_data(code, start_date, end_date)
    df['Datetime'] = pd.to_datetime(df['trade_date'])
    df.set_index("Datetime", inplace=True)
    df['openinterest'] = 0
    df.rename(columns={'vol': 'volume'}, inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return df.iloc[::-1]  # 反转数据

# 自定义策略
class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 3),
    )

    def __init__(self):
        self.order = None
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

    def next(self):
        if not self.position:
            if self.datas[0].close[0] > self.ma[0]:
                self.order = self.buy(size=4000)
        else:
            if self.datas[0].close[0] < self.ma[0]:
                self.order = self.sell(size=4000)

if __name__ == '__main__':
    fromdate = datetime(2019, 1, 2)
    todate = datetime(2019, 12, 31)

    # 获取数据
    stock_df = get_data("000001.SZ", '2019-10-01', '2020-10-01')

    # 初始化 Backtrader 大脑
    cerebro = bt.Cerebro()

    # 添加策略
    cerebro.addstrategy(MyStrategy)

    # 添加数据
    data = bt.feeds.PandasData(dataname=stock_df)
    cerebro.adddata(data, "pingan")

    # 设置初始资金
    start_cash = 100000
    cerebro.broker.set_cash(start_cash)

    # 打印回测参数
    print(f"初始资金：{start_cash}\n回测时间：{fromdate.strftime('%Y-%m-%d')} {todate.strftime('%Y-%m-%d')}")

    # 添加绘图
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)  # 设置图形绘制百分比

    # 添加分析
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    # 执行回测
    cerebro.run()

    # 获取最终资金
    final_cash = cerebro.broker.getvalue()
    print(f"剩余资金：{final_cash}\n回测时间：{fromdate.strftime('%Y-%m-%d')} {todate.strftime('%Y-%m-%d')}")

    # 绘制均线和股价图
    cerebro.plot(style='candlestick', iplot=True, volume=False)
