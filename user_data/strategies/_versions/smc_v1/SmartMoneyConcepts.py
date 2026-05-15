# --- SMC Strategy: Smart Money Concepts ---
# BOS + FVG + Premium/Discount + Order Block
# Target R:R 1:2-1:3, Fixed SL + Trailing TP

import os
os.environ["SMC_CREDIT"] = "0"

from freqtrade.strategy import IStrategy, IntParameter
import pandas as pd
import numpy as np
from smartmoneyconcepts import smc


class SmartMoneyConcepts(IStrategy):
    """
    SMC Strategy — Phase A+B
    
    Entry Logic:
    - BOS/CHoCH xác định trend direction
    - FVG tìm vùng entry (giá quay lại fill gap)
    - Premium/Discount filter (chỉ long ở discount, short ở premium)
    - Order Block confirmation
    
    Exit Logic:
    - Fixed SL + Trailing TP (target R:R 1:2+)
    """
    
    timeframe = '15m'
    startup_candle_count = 100
    can_short = True
    
    # --- Hyperopt parameters ---
    swing_length = IntParameter(5, 30, default=10, space='buy', optimize=True)
    
    # SL/TP targets (as percentage)
    stoploss = -0.02  # -2% fixed SL
    
    # Trailing stop — lock profits when trade runs
    trailing_stop = True
    trailing_stop_positive = 0.02    # trail at 2% behind peak
    trailing_stop_positive_offset = 0.04  # activate trailing after +4% profit
    trailing_only_offset_is_reached = True
    
    # Wide ROI — let winners run
    minimal_roi = {
        "0": 0.10,     # 10% max
        "60": 0.06,    # 6% after 60 candles
        "180": 0.03,   # 3% after 3h
        "360": 0.01,   # 1% after 6h
    }
    
    # Protections
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 3},
        {"method": "MaxDrawdown", "lookback_period_candles": 48,
         "trade_limit": 20, "stop_duration_candles": 12,
         "max_allowed_drawdown": 0.10},
    ]
    
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'limit',
        'stoploss_on_exchange': False,
        'stoploss_on_exchange_interval': 60,
    }
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # --- SMC Indicators ---
        ohlc = dataframe[['open', 'high', 'low', 'close', 'volume']].copy()
        
        # 1. Swing Highs and Lows
        swing_hl = smc.swing_highs_lows(ohlc, swing_length=self.swing_length.value)
        dataframe['swing_hl'] = swing_hl['HighLow']
        dataframe['swing_level'] = swing_hl['Level']
        
        # 2. BOS and CHoCH
        bos_choch = smc.bos_choch(ohlc, swing_hl, close_break=True)
        dataframe['bos'] = bos_choch['BOS']
        dataframe['choch'] = bos_choch['CHOCH']
        dataframe['bos_level'] = bos_choch['Level']
        
        # 3. Fair Value Gap
        fvg = smc.fvg(ohlc, join_consecutive=True)
        dataframe['fvg'] = fvg['FVG']
        dataframe['fvg_top'] = fvg['Top']
        dataframe['fvg_bottom'] = fvg['Bottom']
        dataframe['fvg_mitigated'] = fvg['MitigatedIndex']
        
        # 4. Order Blocks
        ob = smc.ob(ohlc, swing_hl, close_mitigation=False)
        dataframe['ob'] = ob['OB']
        dataframe['ob_top'] = ob['Top']
        dataframe['ob_bottom'] = ob['Bottom']
        dataframe['ob_volume'] = ob['OBVolume']
        
        # 5. Liquidity
        liq = smc.liquidity(ohlc, swing_hl, range_percent=0.01)
        dataframe['liquidity'] = liq['Liquidity']
        dataframe['liq_level'] = liq['Level']
        dataframe['liq_swept'] = liq['Swept']
        
        # 6. Premium/Discount Zone (manual calc based on recent swing range)
        # Find the most recent swing high and swing low
        dataframe['recent_swing_high'] = dataframe['high'].rolling(window=50).max()
        dataframe['recent_swing_low'] = dataframe['low'].rolling(window=50).min()
        dataframe['equilibrium'] = (dataframe['recent_swing_high'] + dataframe['recent_swing_low']) / 2
        
        # Premium = above equilibrium, Discount = below equilibrium
        dataframe['in_discount'] = (dataframe['close'] < dataframe['equilibrium']).astype(int)
        dataframe['in_premium'] = (dataframe['close'] > dataframe['equilibrium']).astype(int)
        
        # 7. Track last BOS/CHoCH direction (forward-fill for trend context)
        dataframe['last_bos'] = dataframe['bos'].replace(0, np.nan).ffill()
        dataframe['last_choch'] = dataframe['choch'].replace(0, np.nan).ffill()
        
        # 8. Track active FVG zones (where price hasn't mitigated yet)
        # Bullish FVG: price above fvg_bottom, hasn't been mitigated
        dataframe['active_bull_fvg_top'] = np.nan
        dataframe['active_bull_fvg_bottom'] = np.nan
        dataframe['active_bear_fvg_top'] = np.nan
        dataframe['active_bear_fvg_bottom'] = np.nan
        
        for i in range(len(dataframe)):
            if dataframe['fvg'].iloc[i] == 1:  # Bullish FVG
                dataframe.loc[dataframe.index[i], 'active_bull_fvg_top'] = dataframe['fvg_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bull_fvg_bottom'] = dataframe['fvg_bottom'].iloc[i]
            elif dataframe['fvg'].iloc[i] == -1:  # Bearish FVG
                dataframe.loc[dataframe.index[i], 'active_bear_fvg_top'] = dataframe['fvg_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bear_fvg_bottom'] = dataframe['fvg_bottom'].iloc[i]
        
        # Forward fill active FVG zones
        dataframe['active_bull_fvg_top'] = dataframe['active_bull_fvg_top'].ffill()
        dataframe['active_bull_fvg_bottom'] = dataframe['active_bull_fvg_bottom'].ffill()
        dataframe['active_bear_fvg_top'] = dataframe['active_bear_fvg_top'].ffill()
        dataframe['active_bear_fvg_bottom'] = dataframe['active_bear_fvg_bottom'].ffill()
        
        # 9. Track active Order Block zones
        dataframe['active_bull_ob_top'] = np.nan
        dataframe['active_bull_ob_bottom'] = np.nan
        dataframe['active_bear_ob_top'] = np.nan
        dataframe['active_bear_ob_bottom'] = np.nan
        
        for i in range(len(dataframe)):
            if dataframe['ob'].iloc[i] == 1:  # Bullish OB
                dataframe.loc[dataframe.index[i], 'active_bull_ob_top'] = dataframe['ob_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bull_ob_bottom'] = dataframe['ob_bottom'].iloc[i]
            elif dataframe['ob'].iloc[i] == -1:  # Bearish OB
                dataframe.loc[dataframe.index[i], 'active_bear_ob_top'] = dataframe['ob_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bear_ob_bottom'] = dataframe['ob_bottom'].iloc[i]
        
        dataframe['active_bull_ob_top'] = dataframe['active_bull_ob_top'].ffill()
        dataframe['active_bull_ob_bottom'] = dataframe['active_bull_ob_bottom'].ffill()
        dataframe['active_bear_ob_top'] = dataframe['active_bear_ob_top'].ffill()
        dataframe['active_bear_ob_bottom'] = dataframe['active_bear_ob_bottom'].ffill()
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # ========== LONG CONDITIONS ==========
        # 1. Trend: Last BOS or CHoCH is bullish
        bullish_trend = (dataframe['last_bos'] == 1) | (dataframe['last_choch'] == 1)
        
        # 2. Zone: Price is in DISCOUNT zone
        in_discount = dataframe['in_discount'] == 1
        
        # 3. Entry: Price touches bullish FVG zone OR bullish Order Block
        in_bull_fvg = (
            (dataframe['close'] <= dataframe['active_bull_fvg_top']) &
            (dataframe['close'] >= dataframe['active_bull_fvg_bottom'])
        )
        in_bull_ob = (
            (dataframe['close'] <= dataframe['active_bull_ob_top']) &
            (dataframe['close'] >= dataframe['active_bull_ob_bottom'])
        )
        
        # 4. Volume confirmation
        vol_ok = dataframe['volume'] > 0
        
        long_condition = bullish_trend & in_discount & (in_bull_fvg | in_bull_ob) & vol_ok
        dataframe.loc[long_condition, 'enter_long'] = 1
        
        # ========== SHORT CONDITIONS ==========
        # 1. Trend: Last BOS or CHoCH is bearish
        bearish_trend = (dataframe['last_bos'] == -1) | (dataframe['last_choch'] == -1)
        
        # 2. Zone: Price is in PREMIUM zone
        in_premium = dataframe['in_premium'] == 1
        
        # 3. Entry: Price touches bearish FVG zone OR bearish Order Block
        in_bear_fvg = (
            (dataframe['close'] >= dataframe['active_bear_fvg_bottom']) &
            (dataframe['close'] <= dataframe['active_bear_fvg_top'])
        )
        in_bear_ob = (
            (dataframe['close'] >= dataframe['active_bear_ob_bottom']) &
            (dataframe['close'] <= dataframe['active_bear_ob_top'])
        )
        
        short_condition = bearish_trend & in_premium & (in_bear_fvg | in_bear_ob) & vol_ok
        dataframe.loc[short_condition, 'enter_short'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Exit signals: opposite structure break
        # Long exit: bearish BOS
        dataframe.loc[dataframe['bos'] == -1, 'exit_long'] = 1
        
        # Short exit: bullish BOS
        dataframe.loc[dataframe['bos'] == 1, 'exit_short'] = 1
        
        return dataframe
    
    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 2.0
