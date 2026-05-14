# Decisions Log — Quyết Định Đã Chọn & Loại Bỏ

> Ghi lại MỌI quyết định quan trọng.
> Mục đích: Không lặp lại sai lầm. Biết TẠI SAO chọn/loại.

---

## Quyết Định Đã Chọn ✅

### D001: Chọn Freqtrade thay vì tự build (2026-05-14)
**Lý do:**
- 50k+ stars, community lớn nhất
- Backtesting + Hyperopt built-in
- Docker support, Telegram integration
- Strategy dạng Python class — dễ customize
- Thay vì mất 2-3 tháng tự build infrastructure

**Thay thế đã xem xét:**
- Jesse — code sạch hơn nhưng community nhỏ, một số features cần trả phí
- OctoBot — dễ dùng nhưng ít flexibility
- Hummingbot — chuyên market making, không phù hợp scalping
- Passivbot — dùng Martingale trên Futures = quá nguy hiểm

### D002: Spot Only, Không Leverage (2026-05-14)
**Lý do:**
- Leverage amplify cả lãi lẫn lỗ
- Với kiến thức trading hạn chế, leverage = tự sát tài chính
- Spot không bao giờ bị liquidation
- Mục tiêu là lãi nhỏ đều, không cần leverage

### D003: Fixed stake_amount thay vì unlimited (2026-05-14)
**Lý do:**
- v1 dùng `unlimited` → all-in mỗi trade → drawdown 98.7%
- Fixed $50/trade = 5% wallet → 1 trade thua max mất $0.50
- Risk per trade cố định = portfolio survivable

### D004: EMA + RSI + VWAP + ADX Confluence (2026-05-14)
**Lý do:**
- Confluence = chỉ trade khi NHIỀU indicators đồng ý
- Giảm false signals so với dùng 1 indicator đơn lẻ
- EMA cho trend, VWAP cho bias, RSI cho momentum, ADX cho trend strength
- Đây là combination phổ biến và được test rộng rãi

### D005: SharpeHyperOptLoss cho Hyperopt (2026-05-14)
**Lý do:**
- Sharpe Ratio = (Return - Risk-free rate) / StdDev
- Ưu tiên consistency hơn raw profit
- Phù hợp với mục tiêu "lãi nhỏ nhưng đều"
- Alternatives: ProfitDrawDownHyperOptLoss (chưa thử)

---

## Quyết Định Đã Loại Bỏ ❌

### R001: stake_amount: unlimited (2026-05-14)
**Lý do loại:** Drawdown 98.7% — gần mất sạch tài khoản
**Bằng chứng:** v1 backtest kết quả

### R002: max_open_trades: 3 (2026-05-14)
**Lý do loại:** Với $1000 wallet và $50/trade, 3 trades = $150 exposure = 15%.
Giảm xuống 2 để giữ exposure < 10%.

---

## Quyết Định Đang Chờ ⏳

### P001: Nên dùng timeframe nào?
- 5m hiện tại: ít noise, nhưng ít trade (52 trades/498 ngày)
- 15m: có thể giảm noise hơn nữa nhưng còn ít trade hơn
- 1m: nhiều trade hơn nhưng noise nhiều, phí giao dịch ăn profit
- **Cần test:** So sánh 5m vs 15m trên cùng strategy

### P002: Nên mở rộng pair list?
- Hiện tại 5 pairs (BTC, ETH, SOL, BNB, XRP) — tất cả top liquidity
- Thêm altcoins volatile hơn (DOGE, AVAX, MATIC) có thể tăng profit
- Nhưng cũng tăng risk (spread lớn hơn, manipulation nhiều hơn)
- **Cần test:** Backtest thêm 3-5 altcoins

### P003: Dynamic stop-loss bằng ATR?
- Fixed SL -1% có thể quá chặt cho BTC (ATR lớn) và quá lỏng cho stableish pairs
- ATR-based SL: stoploss = -1.5 * ATR → tự điều chỉnh theo volatility
- **Cần test:** So sánh fixed SL vs ATR SL
