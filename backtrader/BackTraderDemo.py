# 导入必要的库
from datetime import datetime
import backtrader as bt
import pandas as pd
from tushares.TuShareTool import TuShareTool  # 导入用于获取股票数据的TuShareTool

# 初始化 TuShareTool
tushare = TuShareTool()  # 创建TuShareTool对象，用于获取股票数据


# 获取股票数据
def get_data(code='600483.SH', start_date='2022-10-01', end_date='2023-10-01'):
    # 使用TuShareTool获取指定股票代码和日期范围内的股票数据
    df = tushare.get_stock_data(code, start_date, end_date)

    # 调整数据格式，将日期列转换为Datetime类型并设置为索引
    df['Datetime'] = pd.to_datetime(df['trade_date'])
    df.set_index("Datetime", inplace=True)

    # 添加一个名为'openinterest'的列，值都设置为0
    df['openinterest'] = 0

    # 重命名'vol'列为'volume'
    df.rename(columns={'vol': 'volume'}, inplace=True)

    # 选择并返回特定的列，同时反转数据，以便按照时间升序排列
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return df.iloc[::-1]  # 反转数据，按时间升序排列


# 自定义策略
class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 3),  # 设置策略参数，默认为3
    )

    def __init__(self):
        self.order = None  # 用于存储交易指令
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)  # 创建移动均线指标

    def next(self):
        if not self.position:  # 如果当前没有持仓
            if self.datas[0].close[0] > self.ma[0]:  # 如果收盘价上穿均线
                self.order = self.buy(size=4000)  # 发出买入指令，买入指定数量的股票
        else:  # 如果当前有持仓
            if self.datas[0].close[0] < self.ma[0]:  # 如果收盘价下穿均线
                self.order = self.sell(size=4000)  # 发出卖出指令，卖出指定数量的股票


if __name__ == '__main__':
    fromdate = datetime(2019, 1, 2)  # 设置回测开始日期
    todate = datetime(2019, 12, 31)  # 设置回测结束日期

    # 获取数据
    stock_df = get_data("000001.SZ", '2019-10-01', '2020-10-01')  # 获取特定股票的数据

    # 初始化 Backtrader 大脑
    cerebro = bt.Cerebro()  # 创建Backtrader大脑

    # 添加策略
    cerebro.addstrategy(MyStrategy)  # 向大脑添加自定义策略

    # 添加数据
    data = bt.feeds.PandasData(dataname=stock_df)  # 创建数据源，使用Pandas数据
    cerebro.adddata(data, "pingan")  # 添加数据到大脑，并命名为"pingan"

    # 设置初始资金
    start_cash = 100000  # 设置初始资金
    cerebro.broker.set_cash(start_cash)  # 设置大脑经纪人的初始资金

    # 打印回测参数
    print(f"初始资金：{start_cash}\n回测时间：{fromdate.strftime('%Y-%m-%d')} {todate.strftime('%Y-%m-%d')}")

    # 添加绘图
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)  # 设置图形绘制百分比

    # 添加分析
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 添加PyFolio分析器

    # 执行回测
    cerebro.run()

    # 获取最终资金
    final_cash = cerebro.broker.getvalue()
    print(f"剩余资金：{final_cash}\n回测时间：{fromdate.strftime('%Y-%m-%d')} {todate.strftime('%Y-%m-%d')}")

    # 绘制均线和股价图
    cerebro.plot(style='candlestick', iplot=True, volume=False)
