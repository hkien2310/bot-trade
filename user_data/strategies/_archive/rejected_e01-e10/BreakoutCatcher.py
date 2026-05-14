# --- Style D: BreakoutCatcher ---
# R:R 1:3. Volume spike + BB squeeze → breakout trade.

from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter, stoploss_from_absolute
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
import pandas as pd


class BreakoutCatcher(IStrategy):
    timeframe = '5m'
    startup_candle_count = 30
    can_short = True
    use_custom_stoploss = True
    minimal_roi = {"0": 0.03, "30": 0.02, "90": 0.01, "180": 0.003}
    stoploss = -0.02
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True
    
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 3},
        {"method": "StoplossGuard", "lookback_period_candles": 24,
         "trade_limit": 3, "stop_duration_candles": 24, "only_per_pair": False},
    ]
    
    vol_mult = IntParameter(2, 5, default=3, space='buy')
    adx_min = IntParameter(20, 35, default=25, space='buy')
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_width'] = (bollinger['upper'] - bollinger['lower']) / bollinger['mid']
        dataframe['bb_width_min'] = dataframe['bb_width'].rolling(window=50).min()
        dataframe['bb_squeeze'] = dataframe['bb_width'] <= dataframe['bb_width_min'] * 1.1
        
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_spike'] = dataframe['volume'] > dataframe['volume_mean'] * 3
        
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)
        
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macdhist'] = macd['macdhist']
        
        dataframe['high_20'] = dataframe['high'].rolling(window=20).max()
        dataframe['low_20'] = dataframe['low'].rolling(window=20).min()
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # LONG breakout: price breaks above BB upper + volume spike + ADX rising
        long_cond = (
            (dataframe['close'] > dataframe['bb_upper']) &
            (dataframe['volume'] > dataframe['volume_mean'] * self.vol_mult.value) &
            (dataframe['adx'] > self.adx_min.value) &
            (dataframe['macdhist'] > 0) &
            (dataframe['ema_fast'] > dataframe['ema_slow']) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, 'enter_long'] = 1
        
        # SHORT breakout: price breaks below BB lower + volume spike
        short_cond = (
            (dataframe['close'] < dataframe['bb_lower']) &
            (dataframe['volume'] > dataframe['volume_mean'] * self.vol_mult.value) &
            (dataframe['adx'] > self.adx_min.value) &
            (dataframe['macdhist'] < 0) &
            (dataframe['ema_fast'] < dataframe['ema_slow']) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[short_cond, 'enter_short'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[dataframe['rsi'] > 80, 'exit_long'] = 1
        dataframe.loc[dataframe['rsi'] < 20, 'exit_short'] = 1
        return dataframe
    
    def custom_stoploss(self, pair, trade, current_time, current_rate,
                        current_profit, **kwargs):
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return self.stoploss
        atr = dataframe.iloc[-1]['atr']
        if trade.is_short:
            stop_price = current_rate + (atr * 1.5)
        else:
            stop_price = current_rate - (atr * 1.5)
        return stoploss_from_absolute(stop_price, current_rate, is_short=trade.is_short)
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 2.0
