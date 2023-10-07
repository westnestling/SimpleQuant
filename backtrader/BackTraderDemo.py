from datetime import datetime
import backtrader as bt
import pandas as pd
from tushares.TuShareTool import TuShareTool

tushare = TuShareTool()


def get_data(code='600483.SH', starttime='2022-10-01', endtime='2023-10-01'):
    df = tushare.get_stock_data(code, starttime, endtime)
    df['Datetime'] = pd.to_datetime(df['trade_date'])
    df.set_index("Datetime", inplace=True)
    df['openinterest'] = 0
    df.rename(columns={'vol': 'volume'}, inplace=True)
    # 对df的数据列进行一个整合
    print(df)
    # 在Pandas中，你可以使用df.rename(columns={'oldName': 'newName'}, inplace=True)来修改列名。
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    print(df)
    return df.iloc[::-1]


# 2.构建策略
# 上传20日线买入，跌穿20日均线就卖出其
class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 3),
    )
    i = 1

    def __init__(self):
        self.order = None
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        pass

    # 每个bar都会执行一次
    def next(self):
        if not self.position:
            # 空仓 上穿均线买入
            if self.datas[0].close[0] > self.ma[0]:
                self.order = self.buy(size=4000)
        else:
            # 下穿均线卖出
            if self.datas[0].close[0] < self.ma[0]:
                self.order = self.sell(size=4000)


if __name__ == '__main__':
    fromdate = datetime(2019, 1, 2)
    todate = datetime(2019, 12, 31)
    # 1.加载并读取数据源
    stock_df2 = get_data("000001.SZ", '2019-10-01', '2020-10-01')

    # 2.构建策略

    # 3.策略设置
    cerebro = bt.Cerebro()  # 创建大脑

    # 加入自己的策路
    cerebro.addstrategy(MyStrategy)

    # 將数据加入回測系統
    data2 = bt.feeds.PandasData(dataname=stock_df2)
    cerebro.adddata(data2, "pingan")

    # 设置初始资金
    startcash = 100000
    cerebro.broker.setcash(startcash)
    # 设置手续费
    # cerebro.broker.setcommission(0.0002)
    s = fromdate.strftime("%Y-%m-%d")
    t = todate.strftime("%Y-%m-%d")
    print(f"初始资金：{startcash}\n回测时间：{s} {t}")

    # 添加绘图
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)  # 设置图形绘制百分比

    # 添加分析
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    # 4.执行回测
    cerebro.run()

    portval = cerebro.broker.getvalue()
    print(f"剩余资金：{portval}\n回测时间：{s} {t}")
    # 绘制均线和股价图
    cerebro.plot(style='candlestick', iplot=True, volume=False)
