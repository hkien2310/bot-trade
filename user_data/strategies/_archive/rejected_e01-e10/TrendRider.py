# --- Style B: TrendRider ---
# Evolution of v5 (best so far). R:R 1:3-1:5. Few trades, big winners.
# Added: short selling, ATR dynamic SL, 1h confirmation, MACD
# Need win rate > 25%

from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter, informative, stoploss_from_absolute
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
import pandas as pd


class TrendRider(IStrategy):
    """
    Style B: Swing Micro / Trend Following — R:R 1:3-1:5
    Ít trade nhưng big winners. Long & Short.
    Evolution of ScalpEmaRsiVwap v5 (first profitable strategy).
    """

    timeframe = '5m'
    startup_candle_count = 50
    can_short = True
    use_custom_stoploss = True
    
    minimal_roi = {
        "0": 0.15,
        "30": 0.06,
        "90": 0.02,
        "180": 0
    }
    
    stoploss = -0.10  # Hard max SL
    
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True
    
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 3},
        {"method": "StoplossGuard", "lookback_period_candles": 24,
         "trade_limit": 3, "stop_duration_candles": 24, "only_per_pair": False},
        {"method": "MaxDrawdown", "lookback_period_candles": 288,
         "trade_limit": 10, "stop_duration_candles": 144, "max_allowed_drawdown": 0.10},
    ]
    
    # Params
    ema_fast_period = IntParameter(5, 12, default=7, space='buy')
    ema_slow_period = IntParameter(18, 30, default=23, space='buy')
    rsi_buy_lower = IntParameter(40, 58, default=50, space='buy')
    rsi_buy_upper = IntParameter(55, 70, default=62, space='buy')
    adx_threshold = IntParameter(22, 35, default=28, space='buy')
    rsi_sell_upper = IntParameter(65, 85, default=75, space='sell')
    
    @informative('1h')
    def populate_indicators_1h(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast_period.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow_period.value)
        
        # EMA cross tracking
        dataframe['ema_cross_up'] = qtpylib.crossed_above(dataframe['ema_fast'], dataframe['ema_slow'])
        dataframe['ema_cross_down'] = qtpylib.crossed_below(dataframe['ema_fast'], dataframe['ema_slow'])
        
        dataframe['candles_since_cross_up'] = 0
        dataframe['candles_since_cross_down'] = 0
        for idx in dataframe.index[dataframe['ema_cross_up']]:
            pos = dataframe.index.get_loc(idx)
            for j in range(pos, min(pos + 25, len(dataframe))):
                dataframe.iloc[j, dataframe.columns.get_loc('candles_since_cross_up')] = j - pos
        for idx in dataframe.index[dataframe['ema_cross_down']]:
            pos = dataframe.index.get_loc(idx)
            for j in range(pos, min(pos + 25, len(dataframe))):
                dataframe.iloc[j, dataframe.columns.get_loc('candles_since_cross_down')] = j - pos
        
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_rising'] = dataframe['rsi'] > dataframe['rsi'].shift(3)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        cum_vol = dataframe['volume'].rolling(window=48).sum()
        cum_vol_price = (typical_price * dataframe['volume']).rolling(window=48).sum()
        dataframe['vwap'] = cum_vol_price / cum_vol
        
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macdhist'] = macd['macdhist']
        
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_lower'] = bollinger['lower']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # LONG
        long_cond = (
            (dataframe['ema_fast_1h'] > dataframe['ema_slow_1h']) &
            (dataframe['ema_fast'] > dataframe['ema_slow']) &
            (dataframe['candles_since_cross_up'] > 0) &
            (dataframe['candles_since_cross_up'] <= 20) &
            (dataframe['close'] > dataframe['vwap']) &
            (dataframe['rsi'] > self.rsi_buy_lower.value) &
            (dataframe['rsi'] < self.rsi_buy_upper.value) &
            (dataframe['rsi_rising']) &
            (dataframe['adx'] > self.adx_threshold.value) &
            (dataframe['macdhist'] > 0) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.7) &
            (dataframe['volume'] > 0) &
            (dataframe['close'] < dataframe['bb_upper'])
        )
        dataframe.loc[long_cond, 'enter_long'] = 1
        
        # SHORT (mirror)
        short_cond = (
            (dataframe['ema_fast_1h'] < dataframe['ema_slow_1h']) &
            (dataframe['ema_fast'] < dataframe['ema_slow']) &
            (dataframe['candles_since_cross_down'] > 0) &
            (dataframe['candles_since_cross_down'] <= 20) &
            (dataframe['close'] < dataframe['vwap']) &
            (dataframe['rsi'] > (100 - self.rsi_buy_upper.value)) &
            (dataframe['rsi'] < (100 - self.rsi_buy_lower.value)) &
            (~dataframe['rsi_rising']) &
            (dataframe['adx'] > self.adx_threshold.value) &
            (dataframe['macdhist'] < 0) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.7) &
            (dataframe['volume'] > 0) &
            (dataframe['close'] > dataframe['bb_lower'])
        )
        dataframe.loc[short_cond, 'enter_short'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[dataframe['rsi'] > self.rsi_sell_upper.value, 'exit_long'] = 1
        macd_exit_long = (dataframe['macdhist'] < 0) & (dataframe['close'] < dataframe['vwap'])
        dataframe.loc[macd_exit_long, 'exit_long'] = 1
        
        dataframe.loc[dataframe['rsi'] < (100 - self.rsi_sell_upper.value), 'exit_short'] = 1
        macd_exit_short = (dataframe['macdhist'] > 0) & (dataframe['close'] > dataframe['vwap'])
        dataframe.loc[macd_exit_short, 'exit_short'] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair, trade, current_time, current_rate, 
                        current_profit, **kwargs):
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) < 1:
            return self.stoploss
        atr = dataframe.iloc[-1]['atr']
        if trade.is_short:
            stop_price = current_rate + (atr * 2.5)
        else:
            stop_price = current_rate - (atr * 2.5)
        return stoploss_from_absolute(stop_price, current_rate, is_short=trade.is_short)
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 2.0
