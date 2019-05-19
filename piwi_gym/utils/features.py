import talib
import  numpy as np

close = 'bid'
volume = 'sell_vol'


def create_features(df):
    period = 14
    bid_df = df[['bid']]
    ask_df = df[['ask']]

    bid_df['dema_bid'] = talib.DEMA(df.bid.values, timeperiod=period)
    ask_df['dema_ask'] = talib.DEMA(df.ask.values, timeperiod=period)

    bid_df['ema_bid'] = talib.EMA(df.bid.values, timeperiod=period)
    ask_df['ema_ask'] = talib.EMA(df.ask.values, timeperiod=period)

    bid_df['ht_trendline_bid'] = talib.HT_TRENDLINE(df.bid.values)
    ask_df['ht_trendline_ask'] = talib.HT_TRENDLINE(df.ask.values)

    bid_df['ma_bid'] = talib.MA(df.bid.values, timeperiod=period, matype=0)
    ask_df['ma_ask'] = talib.MA(df.ask.values, timeperiod=period, matype=0)

    bid_df['sma_bid'] = talib.SMA(df.bid.values, timeperiod=period)
    ask_df['sma_ask'] = talib.SMA(df.ask.values, timeperiod=period)

    bid_df['tema_bid'] = talib.TEMA(df.bid.values, timeperiod=period)
    ask_df['tema_ask'] = talib.TEMA(df.ask.values, timeperiod=period)

    bid_df['wma_bid'] = talib.WMA(df.bid.values, timeperiod=period)
    ask_df['wma_ask'] = talib.WMA(df.ask.values, timeperiod=period)

    bid_df['kama_bid'] = talib.KAMA(df.bid.values, timeperiod=period)
    ask_df['kama_ask'] = talib.KAMA(df.ask.values, timeperiod=period)

    bid_df = bid_df.fillna(method='bfill')
    ask_df = ask_df.fillna(method='bfill')

    return bid_df, ask_df
