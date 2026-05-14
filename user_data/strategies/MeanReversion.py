# --- Style C: MeanReversion ---
# R:R ~1:1.5. Buy BB lower, sell BB mid. ADX < 20 only.

from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
import pandas as pd


class MeanReversion(IStrategy):
    timeframe = '15m'
    startup_candle_count = 30
    can_short = True
    minimal_roi = {"0": 0.015, "20": 0.01, "60": 0.005, "120": 0.002}
    stoploss = -0.012
    trailing_stop = True
    trailing_stop_positive = 0.004
    trailing_stop_positive_offset = 0.008
    trailing_only_offset_is_reached = True
    
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 2},
        {"method": "StoplossGuard", "lookback_period_candles": 24,
         "trade_limit": 4, "stop_duration_candles": 12, "only_per_pair": False},
    ]
    
    rsi_oversold = IntParameter(20, 35, default=30, space='buy')
    rsi_overbought = IntParameter(65, 80, default=70, space='sell')
    adx_max = IntParameter(15, 25, default=20, space='buy')
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_mid'] = bollinger['mid']
        stoch = ta.STOCHRSI(dataframe, timeperiod=14)
        dataframe['stoch_k'] = stoch['fastk']
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        ranging = dataframe['adx'] < self.adx_max.value
        long_cond = (
            ranging &
            (dataframe['close'] <= dataframe['bb_lower'] * 1.005) &
            (dataframe['rsi'] < self.rsi_oversold.value) &
            (dataframe['stoch_k'] < 20) &
            (dataframe['rsi'] > dataframe['rsi'].shift(1)) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.5) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, 'enter_long'] = 1
        
        short_cond = (
            ranging &
            (dataframe['close'] >= dataframe['bb_upper'] * 0.995) &
            (dataframe['rsi'] > self.rsi_overbought.value) &
            (dataframe['stoch_k'] > 80) &
            (dataframe['rsi'] < dataframe['rsi'].shift(1)) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.5) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[short_cond, 'enter_short'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[dataframe['close'] >= dataframe['bb_mid'], 'exit_long'] = 1
        dataframe.loc[dataframe['close'] <= dataframe['bb_mid'], 'exit_short'] = 1
        return dataframe
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 2.0
