# Strategy Log — Nhật Ký Chiến Lược

> Mỗi thay đổi strategy PHẢI được ghi lại ở đây.
> Format: Version → Thay đổi → Kết quả backtest → Kết luận

---

## Bảng Tổng Hợp

| Version | Date | Trades | Win% | Avg Profit | Total P/L | Drawdown | Sharpe | Verdict |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| v1 | 2026-05-14 | 6,861 | 41.4% | -0.19% | -$987 | 98.7% | N/A | ❌ LOẠI |
| v2 | 2026-05-14 | 2,523 | 31.1% | -0.22% | -$279 | 27.9% | -9.78 | ❌ LOẠI |
| v3 | 2026-05-14 | 52 | 38.5% | -0.05% | -$1.30 | 0.21% | -15.27 | ⚠️ SAFE BASELINE |
| v4a | 2026-05-14 | 30 | 36.7% | -0.24% | -$3.59 | 0.40% | -1.78 | ❌ LOẠI |
| v4f | 2026-05-14 | 967 | 28.6% | -0.23% | -$108 | 10.9% | -9.78 | ❌ LOẠI |
| v4h | 2026-05-14 | 3,133 | 30.3% | -0.21% | -$325 | 32.6% | -12.92 | ❌ LOẠI |
| v5 (default) | 2026-05-14 | 355 | 28.5% | -0.22% | -$38 | 3.86% | -4.05 | ❌ LOẠI |
| **v5 (hyperopt)** | **2026-05-14** | **78** | **29.5%** | **+0.08%** | **+$2.98** | **0.57%** | **+0.36** | **✅ BEST** |

---

## v1 — Initial Strategy (2026-05-14)

**Indicators**: EMA 9/21 + VWAP + RSI 14
**Entry**: EMA9 > EMA21 + Price > VWAP + RSI 40-65 + Volume > avg
**Exit**: RSI > 70 OR (EMA cross down + Price < VWAP)
**Config**: stake_amount = unlimited, max_open_trades = 3

### Backtest (20250101-20260514, 5m, 5 pairs)
```
Trades:     6,861
Win Rate:   41.4% (2,841W / 4,020L)
Avg Profit: -0.19%
Total P/L:  -$987.15 (-98.71%)
Drawdown:   98.72% ($991.84)
Best Trade: SOL/USDT +1.50%
Worst Trade: BTC/USDT -1.20%
Avg Duration: 1h01m
```

### Phân Tích Thất Bại
1. **`stake_amount: unlimited`** → Bot all-in mỗi trade → 1 trade thua kéo cả tài khoản
2. **Entry quá lỏng** → 6,861 trades trong 498 ngày = ~14 trades/ngày = overtrading
3. **Win rate 41%** + stoploss -1% + TP ~1.5% → net negative do phí giao dịch (0.1% × 2)
4. **Không có ADX filter** → trade cả khi thị trường sideway (choppy) → nhiều false signals

---

## v2 — ADX + EMA Cross Proximity (2026-05-14)

**Thay đổi so với v1:**
- ✅ Thêm **ADX > 22** (chỉ trade khi có trend)
- ✅ Thêm **EMA cross proximity** (chỉ mua trong 15 candles sau EMA crossover)
- ✅ Thêm **RSI direction** (RSI phải đang tăng)
- ✅ Thêm **BB upper guard** (không mua khi giá ở trên Bollinger Band upper)
- ✅ Fix **stake_amount = 50** (fixed $50/trade)
- ✅ Fix **max_open_trades = 2**
- ✅ Thêm **startup_candle_count = 50**
- ✅ Thêm **ATR** indicator (chưa dùng, chuẩn bị cho dynamic SL)
- ✅ Exit: thêm bearish EMA cross + momentum loss conditions

### Backtest (20250101-20260514, 5m, 5 pairs)
```
Trades:     2,523
Win Rate:   31.1% (784W / 1,739L)
Avg Profit: -0.22%
Total P/L:  -$279.21 (-27.91%)
Drawdown:   27.93% ($279.36)
Best Trade: SOL/USDT +1.51%
Worst Trade: BTC/USDT -1.20%
Avg Duration: 50m
```

### Phân Tích
- ✅ Trades giảm 63% (6,861 → 2,523) — filters hoạt động
- ✅ Drawdown giảm 71% (98.7% → 27.9%) — position sizing fix là yếu tố chính
- ❌ Win rate TỤT từ 41% → 31% — EMA cross proximity filter quá aggressive
- ❌ Avg profit vẫn negative — cần tối ưu params

---

## v3 — Hyperopt Optimized (2026-05-14)

**Thay đổi so với v2:**
- ✅ Chạy **Hyperopt 300 epochs** với SharpeHyperOptLoss
- ✅ Train data: 20250101-20260101 (1 năm)
- ✅ Params tối ưu tự động lưu vào `ScalpEmaRsiVwap.json`

**Optimized Parameters:**
```python
adx_threshold = 30      # Tăng từ 22 → chỉ trade khi trend CỰC MẠNH
ema_fast_period = 7      # Giảm từ 9 → phản ứng nhanh hơn
ema_slow_period = 25     # Tăng từ 21 → gap lớn hơn = trend rõ hơn
rsi_buy_lower = 50       # Tăng từ 42 → range RSI cực hẹp
rsi_buy_upper = 55       # Giảm từ 62 → chỉ mua khi RSI "vừa phải"
rsi_sell_upper = 79      # Tăng từ 72 → giữ position lâu hơn
```

### Backtest (20250101-20260514, 5m, 5 pairs, FULL PERIOD)
```
Trades:     52
Win Rate:   38.5% (20W / 32L)
Avg Profit: -0.05%
Total P/L:  -$1.30 (-0.13%)
Drawdown:   0.21% ($2.11)
Best Trade: SOL/USDT +1.51%
Worst Trade: BTC/USDT -1.20%
Avg Duration: 39m
Max Consecutive Wins:  9
Max Consecutive Losses: 23
```

### Phân Tích
- ✅ Drawdown giảm xuống 0.21% — GẦN NHƯ ZERO RISK
- ✅ Total loss chỉ -$1.30 trên 498 ngày — gần break-even
- ✅ Avg profit cải thiện từ -0.22% → -0.05%
- ⚠️ Chỉ 52 trades trong 498 ngày → ~1 trade/10 ngày → quá ít
- ⚠️ Win rate 38.5% vẫn < 50%

### Kết Luận
Strategy v3 là **BASELINE AN TOÀN**. Drawdown gần zero, loss gần zero.

---

## v4a — 15m Timeframe (2026-05-14) ❌ LOẠI

**Thay đổi**: Chỉ thay timeframe 5m → 15m, giữ nguyên v3 params
**Kết quả**: 30 trades, 36.7% win, -$3.59, 0.40% DD
**Kết luận**: Tệ hơn v3 trên mọi metric. 15m ít candle hơn → ít cơ hội hơn, không cải thiện quality.

---

## v4f — Relaxed ADX/RSI (2026-05-14) ❌ LOẠI

**Thay đổi**: ADX 30→25, RSI 50-55→45-60, RSI sell 79→75
**Kết quả**: 967 trades, 28.6% win, -$108, 10.9% DD
**Kết luận**: Nới lỏng filter = nhiều trade kém chất lượng. Khẳng định v3 params (ADX 30, RSI 50-55) là tối ưu.

---

## v4h — Multi-TF + No EMA Cross (2026-05-14) ❌ LOẠI

**Thay đổi**: Thêm 1h EMA confirmation, MACD, candle body filter. BỎ EMA cross proximity.
**Kết quả**: 3,133 trades, 30.3% win, -$325, 32.6% DD
**Kết luận**: **EMA cross proximity LÀ QUAN TRỌNG**. Bỏ nó = quay lại overtrading.

**KEY LEARNING**: EMA cross proximity là filter quan trọng nhất trong strategy này.

---

## v5 — Multi-TF + MACD + Wider SL/ROI (2026-05-14) 🏆 BEST

**Thay đổi so với v3:**
- ✅ Giữ **EMA cross proximity** (mở rộng window 15→20 candles)
- ✅ Thêm **1h EMA trend** confirmation (ADDITIONAL filter, không thay thế)
- ✅ Thêm **MACD histogram > 0** (momentum confirmation)
- ✅ Thêm **RSI rising** direction check
- ✅ Exit: thêm MACD reversal + momentum loss

**Hyperopt (500 epochs, ALL spaces, SharpeHyperOptLoss, train: 20250101-20260101):**
```python
# Buy params
adx_threshold = 32
ema_fast_period = 7
ema_slow_period = 23
rsi_buy_lower = 55
rsi_buy_upper = 60

# Sell params
rsi_sell_upper = 80

# ROI — CỰC KỲ RỘNG (cho winner chạy xa)
minimal_roi = {
    "0": 0.181,     # 18.1%
    "32": 0.072,    # 7.2%
    "87": 0.022,    # 2.2%
    "185": 0        # Breakeven
}

# Stoploss — RỘNG HƠN NHIỀU
stoploss = -0.088    # 8.8%

# Trailing — kích hoạt ở 28.4% profit (chỉ cho mega winners)
trailing_stop = True
trailing_stop_positive = 0.269
trailing_stop_positive_offset = 0.284
trailing_only_offset_is_reached = False
```

### Backtest (20250101-20260514, 5m, 5 pairs, FULL PERIOD including unseen data)
```
Trades:       78
Win Rate:     29.5% (23W / 55L)
Avg Profit:   +0.08%  ← FIRST POSITIVE ✅
Total P/L:    +$2.98 (+0.30%)  ← PROFITABLE ✅
Drawdown:     0.57% ($5.71)  ← EXCELLENT ✅
Sharpe:       +0.36  ← POSITIVE ✅
Sortino:      +0.32  ← POSITIVE ✅
Calmar:       +1.90  ← POSITIVE ✅
Best Trade:   XRP/USDT +2.00%
Worst Trade:  ETH/USDT -1.70%
Avg Duration: 1h18m
Min balance:  $998.91
Max balance:  $1,009.08
```

### KEY INSIGHTS từ v5
1. **Stoploss -8.8% là bất ngờ** — tight stoploss (-1%) kill profits. Wide SL let winners recover.
2. **ROI cực rộng (18%)** — đây KHÔNG phải scalping nữa, mà là micro-swing trading.
3. **Win rate 29.5% nhưng vẫn profitable** — vì winners > losers (asymmetric R:R).
4. **1h trend filter hiệu quả** khi kết hợp với EMA cross proximity (không thay thế).
5. **MACD histogram** thêm 1 lớp confirmation hiệu quả.

### Kết Luận
v5 hyperopt là **STRATEGY PROFITABLE ĐẦU TIÊN**. Sharpe, Sortino, Calmar đều positive.
Drawdown 0.57% = cực kỳ an toàn.

---

## Bài Học Tổng Hợp (Lessons Learned)

| # | Bài Học | Từ Version |
|:--|:--|:--|
| 1 | KHÔNG BAO GIỜ dùng `stake_amount: unlimited` | v1 |
| 2 | ADX filter là ESSENTIAL cho bất kỳ trend-following strategy | v2 |
| 3 | EMA cross proximity là filter QUAN TRỌNG NHẤT | v4h |
| 4 | Nới lỏng entry filters = nhiều trade kém chất lượng | v4f |
| 5 | 15m KHÔNG tốt hơn 5m cho strategy này | v4a |
| 6 | Tight stoploss (-1%) GIẾT profit — wide SL (-8.8%) cho winners room | v5 |
| 7 | Wide ROI (18%) + asymmetric R:R > high win rate | v5 |
| 8 | Multi-TF (1h) confirmation + MACD = good additional filter | v5 |
| 9 | Hyperopt ALL spaces cùng lúc tốt hơn chỉ buy/sell | v5 |

---

## Multi-Strategy Matrix (v2 Upgrade Plan - 2026-05-14)

**Mục tiêu**: Tìm kiếm strategy tốt nhất cho Binance Futures x2 với vốn $100.
**Kết quả Ma Trận 10 Thử Nghiệm (E01 - E10)**:

| # | Strategy | Mode | Trades | Win% | Profit % | Drawdown | Sharpe | Verdict |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| E01 | ScalpTight | Spot | 12 | 58.3% | 0.01% | 0.01% | 0.11 | REJECT |
| E02 | TrendRider | Spot | 382 | 23.6% | -4.06% | 4.06% | -9.74 | REJECT |
| E03 | MeanReversion | Spot | 7 | 42.9% | -0.09% | 0.16% | -0.09 | REJECT |
| E04 | BreakoutCatcher | Spot | 1705 | 7.2% | -28.55% | 28.55% | -15.93 | REJECT |
| E05 | DCAGrid | Spot | 7877 | 44.1% | -90.01% | 90.14% | -15.27 | REJECT |
| E06 | TrendRider | Futures | 740 | 14.5% | -43.20% | 43.20% | N/A | REJECT |
| E07 | MeanReversion | Futures | 14 | 57.1% | -0.31% | 0.98% | -0.07 | REFINE |
| E08 | BreakoutCatcher | Futures | 1216 | 2.5% | -84.89% | 84.89% | N/A | REJECT |
| E09 | ScalpTight Hyp | Futures | 2 | 50.0% | 0.02% | 0.00% | 0.08 | REFINE |
| E10 | MeanRev Hyp | Futures | 66 | 68.2% | **2.44%** | **2.31%** | **0.28** | **KEEP** |

### KEY INSIGHTS từ E01-E10 Matrix
1. **Hyperopt là bắt buộc cho Futures**: Các chiến lược default (dù hoạt động tốt trên Spot hoặc lý thuyết) đều fail thảm hại trên Futures nếu không optimize params.
2. **MeanReversion là best fit**: Trong market sideway/downtrend dài (hiện tại), MeanReversion + Hyperopt (E10) cho kết quả rất tốt: Win rate 68.2%, Drawdown nhỏ (2.31%), Sharpe dương (0.28).
3. **Breakout và DCA rất rủi ro**: BreakoutCatcher (E04/E08) bị false breakout liên tục. DCAGrid (E05) cháy account (-90%) khi market sập mạnh.
4. **TrendRider cần trailing stop linh hoạt hơn**: Swing trade trên TF 5m với leverage dễ bị stopout trước khi kịp catch trend (win rate rớt xuống 14-23%).

---

## Hướng Cải Thiện Tiếp Theo (Phase 2)

- [x] ~~Phase 2.1: MeanReversion Dry-Run~~ → **GÁC LẠI** (chuyển sang SMC)
- [x] ~~Phase 2.2: TrendRider Hyperopt~~ → **GÁC LẠI**
- [x] **Phase A+B: SMC Strategy** → ✅ DONE (xem bên dưới)

---

## SMC — Smart Money Concepts Strategy (2026-05-15) 🏆🏆🏆 NEW CHAMPION

### Triết lý
Không dùng indicator (RSI, BB, MACD). Thay vào đó, **theo dõi dấu chân dòng tiền lớn (institutions)**:
- **BOS** (Break of Structure): Xác định trend
- **CHoCH** (Change of Character): Phát hiện đảo chiều
- **FVG** (Fair Value Gap): Tìm vùng entry chính xác
- **Order Block**: Vùng institutions đặt lệnh lớn
- **Premium/Discount**: Chỉ long ở discount, short ở premium

### Thư viện
`smartmoneyconcepts` (pip install smartmoneyconcepts) — tự động phát hiện tất cả SMC patterns từ OHLCV data.

### Hyperopt Params (300 epochs, SharpeHyperOptLoss, train: 20250101-20260101)
```python
swing_length = 11
stoploss = -0.041  # -4.1%
trailing_stop = True
trailing_stop_positive = 0.243       # trail ở 24.3%
trailing_stop_positive_offset = 0.322 # kích hoạt ở +32.2%
trailing_only_offset_is_reached = True

minimal_roi = {
    "0": 0.346,    # 34.6%
    "101": 0.069,  # 6.9%
    "240": 0.017,  # 1.7%
    "531": 0       # breakeven
}
```

### Backtest Validation (20250101-20260514, 15m, 5 pairs, FULL PERIOD)
```
Trades:       2,959
Win Rate:     61.3% (1,815W / 1,143L)
Avg Profit:   +0.32%
Median Profit: +1.70%  ← ĐÚNG TARGET 1-2%/TRADE ✅
Total P/L:    +$135.92 (+135.92%)  ← $100 → $236 ✅
Drawdown:     20.59% ($23.96)  ← Hơi cao ⚠️
Sharpe:       3.48  ← XUẤT SẮC ✅
Sortino:      4.43  ← XUẤT SẮC ✅
Calmar:       25.49 ← XUẤT SẮC ✅
Avg Duration: 5h27m
Min Balance:  $92.43
Max Balance:  $236.21
Best Day:     +$4.02
Worst Day:    -$4.58
Days Win/Draw/Lose: 312/3/183
```

### So sánh với strategies trước

| Metric | MeanReversion (E10) | **SMC** | Thay đổi |
|:--|:--|:--|:--|
| Trades | 66 | **2,959** | ×45 |
| Win Rate | 68.2% | **61.3%** | -7% (chấp nhận) |
| Total Profit | +$2.44 | **+$135.92** | **×55** 🔥 |
| Median Profit | N/A | **+1.70%** | Target achieved |
| Sharpe | 0.28 | **3.48** | ×12 |
| Drawdown | 2.31% | **20.59%** | Cao hơn ⚠️ |

### KEY INSIGHTS từ SMC
1. **Median profit 1.70%/trade** — đạt đúng mục tiêu 1-2% đã brainstorm
2. **Sharpe 3.48** — strategy quality cực cao (>2 là xuất sắc)
3. **$100 → $236 trong 498 ngày** — performance tốt hơn 55x so với MeanReversion
4. **Drawdown 20.59%** — cần giảm bằng Position Sizing hoặc MaxDrawdown protection
5. **6 trades/ngày trung bình** — active trading, không phải chờ cả tuần
6. **SMC concepts (BOS/FVG/OB) + Trailing TP** = combo cực mạnh cho Futures

### Rủi ro cần lưu ý
- Drawdown 20% nghĩa là có lúc vốn từ $100 xuống $80 trước khi hồi
- Market regime change có thể làm giảm performance
- Cần dry-run validate trước khi trade thật

---

## Bài Học Tổng Hợp (Lessons Learned) — CẬP NHẬT

| # | Bài Học | Từ Version |
|:--|:--|:--|
| 1 | KHÔNG BAO GIỜ dùng `stake_amount: unlimited` | v1 |
| 2 | ADX filter là ESSENTIAL cho trend-following | v2 |
| 3 | EMA cross proximity là filter QUAN TRỌNG NHẤT cho indicator-based | v4h |
| 4 | Tight stoploss (-1%) GIẾT profit — wide SL cho winners room | v5 |
| 5 | Hyperopt ALL spaces cùng lúc tốt hơn chỉ buy/sell | v5 |
| 6 | **MeanReversion indicator-based quá ít profit/trade (0.24%)** | E10 |
| 7 | **SMC (price action/structure) > indicator-based cho R:R** | SMC |
| 8 | **SMC + Trailing TP = median 1.70%/trade — đạt target** | SMC |
| 9 | **Sharpe 3.48 > 0.28 — chất lượng signal vượt trội** | SMC |
| 10 | **Drawdown là trade-off: high return = higher DD** | SMC |

---

## Hướng Tiếp Theo (Phase 3)

- [ ] **Phase 3.1**: Giảm drawdown — thử MaxDrawdown protection tighter hoặc giảm max_open_trades
- [ ] **Phase 3.2**: Dry-run SMC trên Binance Futures (paper trading real-time)
- [ ] **Phase 3.3**: Tích hợp Kronos (Foundation Model) để predict hướng bổ trợ cho SMC entry
- [ ] **Phase 3.4**: Thêm pairs (DOGE, AVAX, LINK...) để tăng cơ hội trade

