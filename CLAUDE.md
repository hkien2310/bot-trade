# Scalping Trading Bot — AI Context

> **ĐỌC FILE NÀY TRƯỚC KHI LÀM BẤT CỨ ĐIỀU GÌ**

## Mục Tiêu Dự Án

Xây dựng bot trading scalping crypto **tự động**, **an toàn**, kiếm **lãi nhỏ nhưng đều** (0.5-2%/ngày).
Đây là tài sản dài hạn — ưu tiên an toàn hơn lợi nhuận.

## Tech Stack

- **Framework**: [Freqtrade](https://www.freqtrade.io) v2026.4
- **Runtime**: Docker (image: `freqtradeorg/freqtrade:stable`)
- **Language**: Python (strategy files)
- **Exchange**: Binance (Spot only — **KHÔNG BAO GIỜ dùng Futures/Leverage**)
- **Pairs**: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT
- **Timeframe**: 5m
- **Data**: Historical 5m candles từ Jan 2025 → present

## Cấu Trúc Dự Án

```
/Users/hoangkien/Youtube/trade/
├── CLAUDE.md                           ← BẠN ĐANG ĐỌC FILE NÀY
├── docker-compose.yml                  ← Docker config
├── docs/
│   ├── STRATEGY_LOG.md                 ← Nhật ký tất cả strategy versions + kết quả
│   ├── SETUP.md                        ← Hướng dẫn setup/run
│   └── DECISIONS.md                    ← Quyết định đã chọn/loại bỏ
└── user_data/
    ├── config.json                     ← Bot config (Binance, Spot, Dry-run)
    ├── strategies/
    │   ├── ScalpEmaRsiVwap.py          ← Strategy code (active)
    │   └── ScalpEmaRsiVwap.json        ← Hyperopt-optimized params
    ├── data/binance/                   ← Historical candle data
    ├── hyperopt_results/               ← Hyperopt results
    └── logs/                           ← Trading logs
```

## Quy Tắc Bất Biến (KHÔNG BAO GIỜ VI PHẠM)

1. **SPOT ONLY** — Không futures, không leverage, không margin
2. **STOP-LOSS BẮT BUỘC** — Mọi strategy phải có stoploss (hyperopt-optimized, hiện tại -8.8%)
3. **POSITION SIZE CỐ ĐỊNH** — $50/trade (5% wallet), không dùng `unlimited`
4. **MAX 2 TRADES ĐỒNG THỜI** — Không bao giờ all-in
5. **BACKTEST TRƯỚC KHI LIVE** — Mọi thay đổi phải backtest trên data đủ dài (> 3 tháng)
6. **GHI NHẬT KÝ** — Mọi thay đổi strategy phải được ghi vào `docs/STRATEGY_LOG.md`
7. **VALIDATE ON UNSEEN DATA** — Train trên 2025, validate trên 2026 (tránh overfitting)

## Workflow Cải Thiện Strategy

```
1. Đề xuất thay đổi (thêm indicator, sửa params, thay logic)
2. Sửa code trong ScalpEmaRsiVwap.py
3. Backtest: docker compose run --rm freqtrade backtesting --config ... --strategy ... --timerange ...
4. So sánh metrics với version trước (PHẢI CẢI THIỆN ít nhất 1 metric chính)
5. Nếu tốt hơn → ghi vào STRATEGY_LOG.md → giữ
6. Nếu tệ hơn → revert → ghi vào DECISIONS.md (loại bỏ)
7. Hyperopt nếu cần: docker compose run --rm freqtrade hyperopt --config ... --strategy ... --hyperopt-loss SharpeHyperOptLoss --spaces buy sell --epochs 300 -j 4
```

## Metrics Quan Trọng (Ưu Tiên Từ Cao → Thấp)

1. **Max Drawdown** — MỤC TIÊU < 5%. Hiện tại: 0.57% ✅
2. **Sharpe Ratio** — MỤC TIÊU > 0. Hiện tại: +0.36 ✅
3. **Avg Profit** — MỤC TIÊU > 0%. Hiện tại: +0.08% ✅
4. **Total P/L** — MỤC TIÊU > 0. Hiện tại: +$2.98 ✅
5. **Profit Factor** — MỤC TIÊU > 1.5. Cần cải thiện.

## Trạng Thái Hiện Tại

- **Phase**: Backtest & Optimize (Phase 2) → chuẩn bị Dry-Run (Phase 3)
- **Strategy version**: v5 (hyperopt-optimized, 500 epochs, ALL spaces)
- **Status**: 🟢 PROFITABLE! +$2.98, Sharpe +0.36, DD 0.57%
- **Kết quả mới nhất**: Xem `docs/STRATEGY_LOG.md`
- **Ngày update**: 2026-05-14

## Lệnh Thường Dùng

```bash
# Backtest
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy ScalpEmaRsiVwap \
  --timerange 20250101-20260514 \
  --timeframe 5m

# Hyperopt (tối ưu params)
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config.json \
  --strategy ScalpEmaRsiVwap \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell roi stoploss trailing \
  --epochs 500 -j 4

# Download data mới
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config.json \
  --timeframe 5m --timerange 20250101-

# Dry-run (paper trade)
docker compose up -d

# Xem logs
docker compose logs -f freqtrade

# Web UI
# http://localhost:8080 (user: freqtrader, pass: freqtrader)
```
