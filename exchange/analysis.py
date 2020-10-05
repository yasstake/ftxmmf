import talib


class Indicator:
    def __init__(self, df):
        """
        :param df: ohlc data('open', 'high', 'low', 'close')
        """
        self.df = df

    def make_analysis(self):
        pass


