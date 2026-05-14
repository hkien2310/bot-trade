# --- Style A: ScalpTight ---
# R:R = 1:1. TP/SL tight (0.3-0.5%). Nhiều trade. Cần win rate > 55%.
# Entry: RSI bounce từ oversold/overbought + VWAP + Volume confirm
# Logic: Mua khi RSI bật lên từ vùng oversold, bán khi RSI chạm overbought

from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter, stoploss_from_absolute
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
import pandas as pd


class ScalpTight(IStrategy):
    """
    Style A: Tight Scalping — R:R 1:1
    Nhiều trade, TP/SL chặt, cần win rate > 55%
    """

    timeframe = '5m'
    startup_candle_count = 30
    can_short = True
    
    # Tight ROI — chốt nhanh
    minimal_roi = {
        "0": 0.005,     # 0.5%
        "15": 0.003,    # 0.3%
        "30": 0.002,    # 0.2%
        "60": 0.001     # 0.1%
    }
    
    stoploss = -0.005   # 0.5% SL
    
    trailing_stop = True
    trailing_stop_positive = 0.002
    trailing_stop_positive_offset = 0.004
    trailing_only_offset_is_reached = True
    
    # Protections
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 2},
        {"method": "StoplossGuard", "lookback_period_candles": 24,
         "trade_limit": 4, "stop_duration_candles": 12, "only_per_pair": False},
    ]
    
    # Params
    rsi_buy = IntParameter(25, 40, default=30, space='buy')
    rsi_sell = IntParameter(60, 80, default=70, space='sell')
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=7)
        
        # VWAP
        typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        cum_vol = dataframe['volume'].rolling(window=48).sum()
        cum_vol_price = (typical_price * dataframe['volume']).rolling(window=48).sum()
        dataframe['vwap'] = cum_vol_price / cum_vol
        
        # EMA for micro-trend
        dataframe['ema_8'] = ta.EMA(dataframe, timeperiod=8)
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)
        
        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        
        # Stochastic RSI
        stoch = ta.STOCHRSI(dataframe, timeperiod=14)
        dataframe['stoch_k'] = stoch['fastk']
        dataframe['stoch_d'] = stoch['fastd']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # LONG: RSI bouncing up from oversold + price near VWAP + volume
        long_cond = (
            (dataframe['rsi'] < self.rsi_buy.value) &
            (dataframe['rsi'] > dataframe['rsi'].shift(1)) &  # RSI rising
            (dataframe['stoch_k'] < 25) &
            (dataframe['close'] >= dataframe['vwap'] * 0.998) &  # Near or above VWAP
            (dataframe['volume'] > dataframe['volume_mean'] * 0.8) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, 'enter_long'] = 1
        
        # SHORT: RSI dropping from overbought
        short_cond = (
            (dataframe['rsi'] > self.rsi_sell.value) &
            (dataframe['rsi'] < dataframe['rsi'].shift(1)) &  # RSI falling
            (dataframe['stoch_k'] > 75) &
            (dataframe['close'] <= dataframe['vwap'] * 1.002) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.8) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[short_cond, 'enter_short'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Exit long when RSI overbought
        dataframe.loc[dataframe['rsi'] > 65, 'exit_long'] = 1
        # Exit short when RSI oversold
        dataframe.loc[dataframe['rsi'] < 35, 'exit_short'] = 1
        return dataframe
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 2.0
