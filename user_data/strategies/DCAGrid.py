# --- Style E: DCAGrid ---
# Dollar Cost Average — mua thêm khi giá giảm 1%, 2%, 3%
# Freqtrade: adjust_trade_position() callback

from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.persistence import Trade
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
import pandas as pd
import math


class DCAGrid(IStrategy):
    timeframe = '5m'
    startup_candle_count = 30
    can_short = False
    position_adjustment_enable = True  # Enable DCA
    max_entry_position_adjustment = 3  # Max 3 DCA orders
    
    minimal_roi = {"0": 0.02, "60": 0.01, "120": 0.005, "240": 0.002}
    stoploss = -0.08  # Wide SL to allow DCA to work
    trailing_stop = False  # No trailing for DCA
    
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 3},
        {"method": "MaxDrawdown", "lookback_period_candles": 288,
         "trade_limit": 10, "stop_duration_candles": 144, "max_allowed_drawdown": 0.10},
    ]
    
    rsi_buy = IntParameter(30, 45, default=40, space='buy')
    rsi_sell = IntParameter(60, 75, default=65, space='sell')
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_mid'] = bollinger['mid']
        
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Initial entry: RSI dipping + near support
        long_cond = (
            (dataframe['rsi'] < self.rsi_buy.value) &
            (dataframe['close'] <= dataframe['bb_lower'] * 1.01) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.5) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, 'enter_long'] = 1
        
        short_cond = (
            (dataframe['rsi'] > self.rsi_sell.value) &
            (dataframe['close'] >= dataframe['bb_upper'] * 0.99) &
            (dataframe['volume'] > dataframe['volume_mean'] * 0.5) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[short_cond, 'enter_short'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[dataframe['close'] >= dataframe['bb_mid'], 'exit_long'] = 1
        dataframe.loc[dataframe['close'] <= dataframe['bb_mid'], 'exit_short'] = 1
        return dataframe
    
    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: float | None, max_stake: float | None,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> float | None | tuple[float | None, str | None]:
        """DCA: Buy more when price drops 1%, 2%, 3% from entry."""
        if current_profit > -0.01:
            return None  # Only DCA when losing > 1%
        
        count = trade.nr_of_successful_entries
        if count >= 4:
            return None  # Max 3 DCA (total 4 entries)
        
        # DCA at -1%, -2%, -3%
        dca_levels = [-0.01, -0.02, -0.03]
        if count <= len(dca_levels) and current_profit <= dca_levels[count - 1]:
            stake = trade.stake_amount  # Same size as original
            return stake
        
        return None
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 2.0
