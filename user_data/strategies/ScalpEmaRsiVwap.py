# --- Scalp EMA + RSI + VWAP Strategy v5 ---
# CHANGELOG:
# v3 was best: 52 trades, 38.5% win, -$1.30, 0.21% DD
# v4a (15m): LOẠI — worse than 5m  
# v4f (relaxed ADX/RSI): LOẠI — too many bad trades
# v4h (multi-TF + no EMA cross): LOẠI — 3133 trades, -32.5%
#
# KEY INSIGHT: EMA cross proximity IS important for signal quality.
# v5: Keep v3 logic but improve:
#   - Wider stoploss (-2% instead of -1%)
#   - Wider ROI targets (allow bigger winners)
#   - Add 1h trend as ADDITIONAL filter (not replacement)
#   - Keep EMA cross proximity but extend window to 20 candles
#   - Add MACD as entry confluence

import numpy as np
from datetime import datetime
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter, informative
from freqtrade.persistence import Trade
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
import pandas as pd


class ScalpEmaRsiVwap(IStrategy):
    """
    Scalping Strategy v5: v3 base + 1h confirmation + MACD + wider SL/ROI
    
    Keeps the core v3 logic that was near break-even (0.21% DD)
    but tries to improve profitability by:
    1. Wider stoploss (-2%) = fewer stop-outs
    2. Wider ROI = bigger winners when trend works
    3. 1h EMA trend ADDITIONAL filter
    4. MACD histogram positive = momentum confirmation
    5. EMA cross window extended to 20 (from 15)
    """

    timeframe = '5m'
    startup_candle_count = 50
    
    # Wider ROI — let winners run
    minimal_roi = {
        "0": 0.025,       # 2.5%
        "30": 0.02,        # 2%
        "60": 0.015,       # 1.5%
        "120": 0.01,       # 1%
        "240": 0.003       # 0.3%
    }
    
    # WIDER stoploss — give trades more room to breathe
    stoploss = -0.02      # 2%
    
    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.006
    trailing_stop_positive_offset = 0.012
    trailing_only_offset_is_reached = True
    
    can_short = False
    
    # Hyperparameters — ranges tuned based on v3 hyperopt results
    ema_fast_period = IntParameter(5, 12, default=7, space='buy')
    ema_slow_period = IntParameter(18, 30, default=25, space='buy')
    rsi_buy_lower = IntParameter(35, 55, default=45, space='buy')
    rsi_buy_upper = IntParameter(55, 70, default=62, space='buy')
    adx_threshold = IntParameter(22, 35, default=28, space='buy')
    rsi_sell_upper = IntParameter(65, 85, default=75, space='sell')
    
    # === HIGHER TIMEFRAME (1h) ===
    @informative('1h')
    def populate_indicators_1h(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe
    
    # === 5m INDICATORS ===
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        
        # EMA
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast_period.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow_period.value)
        
        # EMA cross signal
        dataframe['ema_cross_up'] = qtpylib.crossed_above(
            dataframe['ema_fast'], dataframe['ema_slow']
        )
        # Count candles since last EMA cross
        dataframe['candles_since_cross'] = 0
        cross_idx = dataframe.index[dataframe['ema_cross_up']]
        for idx in cross_idx:
            pos = dataframe.index.get_loc(idx)
            for j in range(pos, min(pos + 30, len(dataframe))):
                dataframe.iloc[j, dataframe.columns.get_loc('candles_since_cross')] = j - pos
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_rising'] = dataframe['rsi'] > dataframe['rsi'].shift(3)
        
        # ADX
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        
        # VWAP
        dataframe['vwap'] = self.calculate_vwap(dataframe)
        
        # MACD
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macdhist'] = macd['macdhist']
        
        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        
        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_lower'] = bollinger['lower']
        
        return dataframe

    def calculate_vwap(self, dataframe: pd.DataFrame) -> pd.Series:
        typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        period = 48
        cum_vol = dataframe['volume'].rolling(window=period).sum()
        cum_vol_price = (typical_price * dataframe['volume']).rolling(window=period).sum()
        vwap = cum_vol_price / cum_vol
        return vwap

    # === ENTRY ===
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        v5 Entry — v3 base + 1h trend + MACD + wider EMA cross window:
        1. 1h EMA uptrend (higher TF confirmation) — NEW
        2. 5m EMA fast > slow (local uptrend) 
        3. Near EMA cross (within 20 candles) — KEPT from v3
        4. Price > VWAP
        5. RSI in range + rising
        6. ADX strong
        7. MACD hist > 0 — NEW
        8. Volume + BB guard
        """
        conditions = []
        
        # 1. Higher TF trend
        conditions.append(dataframe['ema_fast_1h'] > dataframe['ema_slow_1h'])
        
        # 2. Local uptrend
        conditions.append(dataframe['ema_fast'] > dataframe['ema_slow'])
        
        # 3. Near EMA cross (within 20 candles = 100 min)
        conditions.append(
            (dataframe['candles_since_cross'] > 0) & 
            (dataframe['candles_since_cross'] <= 20)
        )
        
        # 4. Price > VWAP
        conditions.append(dataframe['close'] > dataframe['vwap'])
        
        # 5. RSI
        conditions.append(dataframe['rsi'] > self.rsi_buy_lower.value)
        conditions.append(dataframe['rsi'] < self.rsi_buy_upper.value)
        conditions.append(dataframe['rsi_rising'])
        
        # 6. ADX strong
        conditions.append(dataframe['adx'] > self.adx_threshold.value)
        
        # 7. MACD positive
        conditions.append(dataframe['macdhist'] > 0)
        
        # 8. Volume + BB guard
        conditions.append(dataframe['volume'] > dataframe['volume_mean'] * 0.7)
        conditions.append(dataframe['volume'] > 0)
        conditions.append(dataframe['close'] < dataframe['bb_upper'])
        
        if conditions:
            dataframe.loc[
                self._reduce_conditions(conditions),
                'enter_long'] = 1

        return dataframe

    # === EXIT ===
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # RSI overbought
        rsi_exit = dataframe['rsi'] > self.rsi_sell_upper.value
        
        # MACD + VWAP reversal
        macd_exit = (
            (dataframe['macdhist'] < 0) & 
            (dataframe['close'] < dataframe['vwap'])
        )
        
        # Full momentum loss
        momentum_loss = (
            (dataframe['close'] < dataframe['vwap']) & 
            (dataframe['close'] < dataframe['ema_slow']) &
            (dataframe['ema_fast'] < dataframe['ema_slow'])
        )
        
        dataframe.loc[rsi_exit | macd_exit | momentum_loss, 'exit_long'] = 1
        return dataframe

    @staticmethod
    def _reduce_conditions(conditions: list) -> pd.Series:
        result = conditions[0]
        for c in conditions[1:]:
            result = result & c
        return result

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: str | None,
                 side: str, **kwargs) -> float:
        return 1.0
