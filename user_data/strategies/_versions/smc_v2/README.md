# SMC Bot — v2 (2026-05-15)

> **Snapshot — KHÔNG SỬA FILE NÀY**

## Thay đổi từ v1
1. **1h Multi-TF as BOOST** (tag, not filter) — v1 chỉ dùng 15m
2. **Liquidity sweep entries** — thêm cơ hội trade khi smart money sweep
3. **CHoCH exit** — thoát lệnh sớm hơn khi structure đổi
4. **Trailing thực tế hơn**: +17.4% kích hoạt, trail 10.1% (v1 là +32.2%/24.3%)
5. **SL -2.6%** (v1: -4.1%) → cắt lỗ nhanh hơn

## Params (Hyperopt 300 epochs)
```python
swing_length = 5
stoploss = -0.026
trailing_stop_positive = 0.101
trailing_stop_positive_offset = 0.174
minimal_roi = {"0": 0.254, "48": 0.094, "137": 0.048, "285": 0}
```

## Kết quả (20250101-20260514, 498 ngày)
```
Total Profit: +$313.51 (+313.51%)  ← $100 → $413
Trades:       4,067
Win Rate:     57.7%
Avg Profit:   +0.54%/trade
Sharpe:       9.13
Sortino:      17.37
Calmar:       338.05
Drawdown:     3.58% ($5.33)  ← CỰC KỲ THẤP
DD Duration:  3.5 ngày
```

## So sánh v1 → v2
| Metric | v1 | v2 | Δ |
|:--|:--|:--|:--|
| Profit | +$136 | +$314 | ×2.3 |
| Drawdown | 20.59% | 3.58% | ↓83% |
| Sharpe | 3.48 | 9.13 | ×2.6 |
| Max Balance | $236 | $413 | ×1.75 |
