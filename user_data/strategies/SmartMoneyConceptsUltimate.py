# --- SMC Strategy Ultimate: Tinh Hoa Hội Tụ ---
# Kết hợp sức mạnh:
# - V3: Market Stoploss + Stoploss_On_Exchange (Chống Sập sàn)
# - V4: Tiered Auto-Compounding (Lãi Kép Bậc Thang x1.5)
# - V5: Hyperopt AI (Sweep Only, Swing 44, SL -5.4%, Smart ROI)

import os
import math
os.environ["SMC_CREDIT"] = "0"

from freqtrade.strategy import IStrategy, IntParameter, BooleanParameter
import pandas as pd
import numpy as np
from smartmoneyconcepts import smc


class SmartMoneyConceptsUltimate(IStrategy):
    """
    SMC Strategy Ultimate (V3+V4+V5)
    Bản đúc kiếm cuối cùng.
    """

    timeframe = '15m'
    startup_candle_count = 200
    can_short = True

    # ==========================================
    # BỘ NÃO V5 (HYPEROPT AI)
    # ==========================================
    # --- Structural Setup ---
    # Máy học phát hiện 44 là con số hoàn hảo để nhìn lại đỉnh/đáy trên khung 15m
    swing_length = IntParameter(5, 50, default=44, space='buy', optimize=False)

    # --- Entry Toggles ---
    # Bỏ hoàn toàn FVG/OB (Mitigation). Chỉ dùng râu nến quét thanh khoản (Sweep)
    use_mitigation_setup = BooleanParameter(default=False, space='buy', optimize=False)
    use_sweep_setup = BooleanParameter(default=True, space='buy', optimize=False)
    require_htf_alignment = BooleanParameter(default=True, space='buy', optimize=False)
    require_discount_premium = BooleanParameter(default=True, space='buy', optimize=False)

    # --- Stoploss ---
    stoploss = -0.054

    # --- Trailing Stop ---
    trailing_stop = True
    trailing_stop_positive = 0.314
    trailing_stop_positive_offset = 0.382
    trailing_only_offset_is_reached = True

    # --- ROI ---
    minimal_roi = {
        "0": 0.296,
        "53": 0.126,
        "142": 0.033,
        "473": 0
    }

    # ==========================================
    # BỘ GIÁP V3 (CHỐNG SẬP SÀN)
    # ==========================================
    protections = [
        {"method": "CooldownPeriod", "stop_duration_candles": 3},
        {"method": "MaxDrawdown", "lookback_period_candles": 48,
         "trade_limit": 20, "stop_duration_candles": 12,
         "max_allowed_drawdown": 0.10},
    ]

    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True,
        'stoploss_on_exchange_interval': 60,
    }


    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        return [(pair, '1h') for pair in pairs]

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # --- 1h HTF for trend boost ---
        inf_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        if len(inf_1h) > 0:
            ohlc_1h = inf_1h[['open', 'high', 'low', 'close', 'volume']].copy()
            swing_hl_1h = smc.swing_highs_lows(ohlc_1h, swing_length=10)
            bos_choch_1h = smc.bos_choch(ohlc_1h, swing_hl_1h, close_break=True)
            inf_1h['bos_1h'] = bos_choch_1h['BOS']
            inf_1h['choch_1h'] = bos_choch_1h['CHOCH']
            inf_1h['last_bos_1h'] = inf_1h['bos_1h'].replace(0, np.nan).ffill()
            inf_1h['last_choch_1h'] = inf_1h['choch_1h'].replace(0, np.nan).ffill()
            inf_1h = inf_1h[['date', 'last_bos_1h', 'last_choch_1h']].copy()
            dataframe = pd.merge_asof(dataframe, inf_1h, on='date', direction='backward')
        else:
            dataframe['last_bos_1h'] = np.nan
            dataframe['last_choch_1h'] = np.nan

        # --- 15m SMC Indicators ---
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

        # 3. Fair Value Gap (Giữ lại tính toán phòng trường hợp bật lại)
        fvg = smc.fvg(ohlc, join_consecutive=True)
        dataframe['fvg'] = fvg['FVG']
        dataframe['fvg_top'] = fvg['Top']
        dataframe['fvg_bottom'] = fvg['Bottom']

        # 4. Order Blocks (Giữ lại tính toán phòng trường hợp bật lại)
        ob = smc.ob(ohlc, swing_hl, close_mitigation=False)
        dataframe['ob'] = ob['OB']
        dataframe['ob_top'] = ob['Top']
        dataframe['ob_bottom'] = ob['Bottom']
        dataframe['ob_volume'] = ob['OBVolume']
        dataframe['ob_pct'] = ob['Percentage']

        # 5. Liquidity (Thành phần quan trọng nhất theo AI)
        liq = smc.liquidity(ohlc, swing_hl, range_percent=0.01)
        dataframe['liquidity'] = liq['Liquidity']
        dataframe['liq_level'] = liq['Level']
        dataframe['liq_swept'] = liq['Swept']

        # 6. Premium/Discount Zone
        dataframe['recent_swing_high'] = dataframe['high'].rolling(window=50).max()
        dataframe['recent_swing_low'] = dataframe['low'].rolling(window=50).min()
        dataframe['range_size'] = dataframe['recent_swing_high'] - dataframe['recent_swing_low']
        dataframe['equilibrium'] = (dataframe['recent_swing_high'] + dataframe['recent_swing_low']) / 2
        dataframe['in_discount'] = (dataframe['close'] < dataframe['equilibrium']).astype(int)
        dataframe['in_premium'] = (dataframe['close'] > dataframe['equilibrium']).astype(int)

        # 7. Track last BOS/CHoCH direction
        dataframe['last_bos'] = dataframe['bos'].replace(0, np.nan).ffill()
        dataframe['last_choch'] = dataframe['choch'].replace(0, np.nan).ffill()

        # 8. Track active FVG zones
        dataframe['active_bull_fvg_top'] = np.nan
        dataframe['active_bull_fvg_bottom'] = np.nan
        dataframe['active_bear_fvg_top'] = np.nan
        dataframe['active_bear_fvg_bottom'] = np.nan

        for i in range(len(dataframe)):
            if dataframe['fvg'].iloc[i] == 1:
                dataframe.loc[dataframe.index[i], 'active_bull_fvg_top'] = dataframe['fvg_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bull_fvg_bottom'] = dataframe['fvg_bottom'].iloc[i]
            elif dataframe['fvg'].iloc[i] == -1:
                dataframe.loc[dataframe.index[i], 'active_bear_fvg_top'] = dataframe['fvg_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bear_fvg_bottom'] = dataframe['fvg_bottom'].iloc[i]

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
            if dataframe['ob'].iloc[i] == 1:
                dataframe.loc[dataframe.index[i], 'active_bull_ob_top'] = dataframe['ob_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bull_ob_bottom'] = dataframe['ob_bottom'].iloc[i]
            elif dataframe['ob'].iloc[i] == -1:
                dataframe.loc[dataframe.index[i], 'active_bear_ob_top'] = dataframe['ob_top'].iloc[i]
                dataframe.loc[dataframe.index[i], 'active_bear_ob_bottom'] = dataframe['ob_bottom'].iloc[i]

        dataframe['active_bull_ob_top'] = dataframe['active_bull_ob_top'].ffill()
        dataframe['active_bull_ob_bottom'] = dataframe['active_bull_ob_bottom'].ffill()
        dataframe['active_bear_ob_top'] = dataframe['active_bear_ob_top'].ffill()
        dataframe['active_bear_ob_bottom'] = dataframe['active_bear_ob_bottom'].ffill()

        # 10. Liquidity sweep tracking
        dataframe['liq_just_swept'] = 0
        dataframe['liq_sweep_dir'] = 0
        for i in range(1, len(dataframe)):
            swept = dataframe['liq_swept'].iloc[i]
            if pd.notna(swept) and swept > 0:
                # Bullish sweep: sell-side liquidity swept → price should go UP
                if dataframe['liquidity'].iloc[i] == -1:
                    dataframe.loc[dataframe.index[i], 'liq_just_swept'] = 1
                    dataframe.loc[dataframe.index[i], 'liq_sweep_dir'] = 1  # bullish
                elif dataframe['liquidity'].iloc[i] == 1:
                    dataframe.loc[dataframe.index[i], 'liq_just_swept'] = 1
                    dataframe.loc[dataframe.index[i], 'liq_sweep_dir'] = -1  # bearish

        # Forward fill sweep signal for a few candles
        dataframe['recent_bull_sweep'] = (dataframe['liq_sweep_dir'] == 1).rolling(window=8).max().fillna(0)
        dataframe['recent_bear_sweep'] = (dataframe['liq_sweep_dir'] == -1).rolling(window=8).max().fillna(0)

        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # ========== LONG CONDITIONS ==========
        # 1. 15m Trend: Last BOS or CHoCH is bullish
        bullish_trend = (dataframe['last_bos'] == 1) | (dataframe['last_choch'] == 1)

        # 2. Zone: Price is in DISCOUNT zone
        in_discount = dataframe['in_discount'] == 1

        # 3a. Entry: Price touches bullish FVG zone OR bullish Order Block
        in_bull_fvg = (
            (dataframe['close'] <= dataframe['active_bull_fvg_top']) &
            (dataframe['close'] >= dataframe['active_bull_fvg_bottom'])
        )
        in_bull_ob = (
            (dataframe['close'] <= dataframe['active_bull_ob_top']) &
            (dataframe['close'] >= dataframe['active_bull_ob_bottom'])
        )

        # 3b. NEW: Liquidity sweep entry (sell-side swept → go long)
        liq_sweep_long = (dataframe['recent_bull_sweep'] == 1) & in_discount & bullish_trend

        # 4. Volume
        vol_ok = dataframe['volume'] > 0

        # 5. HTF boost: 1h trend alignment (not required, but adds tag)
        htf_aligned = (dataframe['last_bos_1h'] == 1) | (dataframe['last_choch_1h'] == 1)

        discount_cond = in_discount if self.require_discount_premium.value else True
        htf_cond = htf_aligned if self.require_htf_alignment.value else True

        if self.use_mitigation_setup.value:
            long_base = bullish_trend & discount_cond & htf_cond & (in_bull_fvg | in_bull_ob) & vol_ok
        else:
            long_base = pd.Series(False, index=dataframe.index)

        if self.use_sweep_setup.value:
            long_sweep = liq_sweep_long & htf_cond & vol_ok
        else:
            long_sweep = pd.Series(False, index=dataframe.index)

        dataframe.loc[long_base, 'enter_long'] = 1
        dataframe.loc[long_base & htf_aligned, 'enter_tag'] = 'smc_htf_aligned'
        dataframe.loc[long_base & ~htf_aligned, 'enter_tag'] = 'smc_15m_only'
        dataframe.loc[long_sweep & ~long_base, 'enter_long'] = 1
        dataframe.loc[long_sweep & ~long_base, 'enter_tag'] = 'liq_sweep_long'

        # ========== SHORT CONDITIONS ==========
        bearish_trend = (dataframe['last_bos'] == -1) | (dataframe['last_choch'] == -1)
        in_premium = dataframe['in_premium'] == 1

        in_bear_fvg = (
            (dataframe['close'] >= dataframe['active_bear_fvg_bottom']) &
            (dataframe['close'] <= dataframe['active_bear_fvg_top'])
        )
        in_bear_ob = (
            (dataframe['close'] >= dataframe['active_bear_ob_bottom']) &
            (dataframe['close'] <= dataframe['active_bear_ob_top'])
        )

        liq_sweep_short = (dataframe['recent_bear_sweep'] == 1) & in_premium & bearish_trend
        htf_bear_aligned = (dataframe['last_bos_1h'] == -1) | (dataframe['last_choch_1h'] == -1)

        premium_cond = in_premium if self.require_discount_premium.value else True
        htf_bear_cond = htf_bear_aligned if self.require_htf_alignment.value else True

        if self.use_mitigation_setup.value:
            short_base = bearish_trend & premium_cond & htf_bear_cond & (in_bear_fvg | in_bear_ob) & vol_ok
        else:
            short_base = pd.Series(False, index=dataframe.index)

        if self.use_sweep_setup.value:
            short_sweep = liq_sweep_short & htf_bear_cond & vol_ok
        else:
            short_sweep = pd.Series(False, index=dataframe.index)

        dataframe.loc[short_base, 'enter_short'] = 1
        dataframe.loc[short_base & htf_bear_aligned, 'enter_tag'] = 'smc_htf_aligned'
        dataframe.loc[short_base & ~htf_bear_aligned, 'enter_tag'] = 'smc_15m_only'
        dataframe.loc[short_sweep & ~short_base, 'enter_short'] = 1
        dataframe.loc[short_sweep & ~short_base, 'enter_tag'] = 'liq_sweep_short'

        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Exit on opposite BOS
        dataframe.loc[dataframe['bos'] == -1, 'exit_long'] = 1
        dataframe.loc[dataframe['bos'] == 1, 'exit_short'] = 1

        # Also exit when CHoCH signals reversal
        dataframe.loc[dataframe['choch'] == -1, 'exit_long'] = 1
        dataframe.loc[dataframe['choch'] == 1, 'exit_short'] = 1

        return dataframe

    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs):
        return 10.0

    # ==========================================
    # TRÁI TIM V4 (LÃI KÉP BẬC THANG)
    # ==========================================
    # Chế độ 3: Lãi Kép Bậc Thang (Vốn x2 -> Lệnh x1.5). Vừa đủ lớn để tăng tài sản nhanh, vừa đủ nhỏ để không ảnh hưởng tỷ lệ Thắng/Thua.
    compounding_mode = 3

    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            leverage: float, entry_tag: str, side: str,
                            **kwargs) -> float:
        total_wallet = self.wallets.get_total_stake_amount()
        base_stake = 15.0
        base_wallet = 100.0
        
        calculated_stake = base_stake
        
        if self.compounding_mode == 3:
            # Mode 3: Tiered x1.5 (Vốn x2 -> Vol x1.5)
            power = int(math.log2(max(1, total_wallet / base_wallet)))
            calculated_stake = base_stake * (1.5 ** power)
                
        # Limit the maximum stake to $50,000 to prevent Binance position limit crashes
        return min(calculated_stake, max_stake, 50000.0)

