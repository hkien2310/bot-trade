# SMC Bot — v1 (2026-05-15)

> **Snapshot của version đầu tiên — KHÔNG SỬA FILE NÀY**
> File active ở `strategies/SmartMoneyConcepts.py`

## Thông số

| Thông số | Giá trị |
|:--|:--|
| Timeframe | 15m |
| Pairs | BTC, ETH, SOL, BNB, XRP (Futures) |
| Leverage | x2 isolated |
| Stake | $15/trade |
| Max positions | 3 |
| SL | -4.1% (cố định) |
| Trailing activation | +32.2% |
| Trailing distance | 24.3% |
| Swing length | 11 |

## Entry Logic
- BOS/CHoCH → xác định trend
- FVG/Order Block → vùng entry
- Premium/Discount → filter hướng
- Volume > 0

## Exit Logic
- Fixed SL -4.1%
- ROI table: 34.6% → 6.9% → 1.7% → 0%
- Trailing TP ở +32.2%
- BOS đảo chiều

## Kết quả Backtest (20250101-20260514)
```
Trades:       2,959
Win Rate:     61.3%
Total Profit: +$135.92 (+135.92%)
Median Profit: +1.70%/trade
Sharpe:       3.48
Sortino:      4.43
Calmar:       25.49
Drawdown:     20.59%
Avg Duration: 5h27m
$100 → $236.21
```

## Hạn chế cần cải thiện ở v2
1. SL cố định -4.1% → nên dynamic theo structure
2. TP bằng ROI table → nên TP theo structure level tiếp theo
3. Chỉ dùng 15m → nên multi-TF (1h structure + 15m entry)
4. Trade 24/7 → nên filter session (London/NY)
5. Mọi FVG bằng nhau → nên scoring FVG quality
6. Drawdown 20.59% → cần giảm xuống < 15%

## Roadmap
```
v1 (hiện tại):  BOS + FVG + OB + Premium/Discount + Fixed SL/ROI
v2 (tiếp theo): Custom SL/TP theo structure + Multi-TF
v3 (sau đó):    Session filter + FVG scoring
v4 (xa hơn):    Kronos prediction + FreqAI
```
