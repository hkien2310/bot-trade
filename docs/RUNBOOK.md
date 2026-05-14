# RUNBOOK — Kịch Bản Test Tự Động

> **AI: Đọc file này rồi thực hiện TỪNG BƯỚC. Ghi kết quả vào bảng cuối.**
> **KHÔNG skip bước. KHÔNG thay đổi code. Chỉ CHẠY và GHI KẾT QUẢ.**

## Bước 0: Chuẩn Bị Data

```bash
# Download futures data cho 5 pairs, 3 timeframes
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config-futures.json \
  --timeframe 5m 15m 1h \
  --timerange 20250101-20260514
```

Nếu lỗi futures data, dùng spot data thay thế (đã có sẵn).

## Bước 1: Backtest 5 Strategies (Spot mode — dùng config.json cũ)

Chạy lần lượt 5 lệnh sau. SAU MỖI LỆNH, ghi kết quả vào bảng E01-E05.

```bash
# E01: ScalpTight (Style A)
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy ScalpTight \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30

# E02: TrendRider (Style B)
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy TrendRider \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30

# E03: MeanReversion (Style C)
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy MeanReversion \
  --timerange 20250101-20260514 \
  --timeframe 15m \
  --enable-protections \
  2>&1 | tail -30

# E04: BreakoutCatcher (Style D)
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy BreakoutCatcher \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30

# E05: DCAGrid (Style E)
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy DCAGrid \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30
```

## Bước 2: Backtest Futures Mode (config-futures.json)

Chạy lại TOP strategies từ Bước 1 với futures config:

```bash
# E06: TrendRider Futures
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config-futures.json \
  --strategy TrendRider \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30

# E07: MeanReversion Futures
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config-futures.json \
  --strategy MeanReversion \
  --timerange 20250101-20260514 \
  --timeframe 15m \
  --enable-protections \
  2>&1 | tail -30

# E08: BreakoutCatcher Futures
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config-futures.json \
  --strategy BreakoutCatcher \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30
```

## Bước 3: Hyperopt Top 2 Strategies

Chọn 2 strategies có score cao nhất từ Bước 1-2, chạy hyperopt:

```bash
# Hyperopt Strategy 1 (thay STRATEGY_NAME bằng tên thật)
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config-futures.json \
  --strategy STRATEGY_NAME \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell roi stoploss trailing \
  --epochs 500 -j 4 \
  --timerange 20250101-20260101 \
  2>&1 | tail -40

# Hyperopt Strategy 2
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config-futures.json \
  --strategy STRATEGY_NAME_2 \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell roi stoploss trailing \
  --epochs 500 -j 4 \
  --timerange 20250101-20260101 \
  2>&1 | tail -40
```

## Bước 4: Validate Hyperopt (Full Period)

Backtest top 2 strategies SAU hyperopt trên FULL data:

```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config-futures.json \
  --strategy STRATEGY_NAME \
  --timerange 20250101-20260514 \
  --timeframe 5m \
  --enable-protections \
  2>&1 | tail -30
```

## Bước 5: Ghi Kết Quả

### Bảng Kết Quả (ĐIỀN SAU KHI CHẠY)

| # | Strategy | Config | Trades | Win% | Avg Profit | Total P/L | Drawdown | Sharpe | Score | Verdict |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| E01 | ScalpTight | Spot | 12 | 58.3% | 0.02% | 0.01% (0.13 USDT) | 0.01% | 0.11 | 5.1 | REJECT |
| E02 | TrendRider | Spot | 382 | -0.21% | -4.06% (-40.59 USDT) | 4.06% | -9.74 | 3.55 | REJECT |
| E03 | MeanReversion | Spot | 7 | -0.27% | -0.09% (-0.92 USDT) | 0.16% | -0.09 | 3.85 | REJECT |
| E04 | BreakoutCatcher | Spot | 1705 | -0.34% | -28.55% (-285.5 USDT) | 28.55% | -15.93 | 1.8 | REJECT |
| E05 | DCAGrid | Spot | 7877 | -0.08% | -90.01% (-900.1 USDT) | 90.14% | -15.27 | 2.55 | REJECT |
| E06 | TrendRider | Futures | 740 | -0.41% | -43.20% (-43.19 USDT) | 43.20% | - | 1.8 | REJECT |
| E07 | MeanReversion | Futures | 14 | -0.13% | -0.31% (-0.30 USDT) | 0.98% | -0.07 | 4.3 | REFINE |
| E08 | BreakoutCatcher | Futures | 1216 | -0.49% | -84.89% (-84.89 USDT) | 84.89% | - | 1.8 | REJECT |
| E09 | ScalpTight Hyp | Futures | 2 | 50.0% | 0.06% | 0.02% (0.017 USDT) | 0.00% | 0.08 | 5.1 | REFINE |
| E10 | MeanRev Hyp | Futures | 66 | 68.2% | 0.24% | 2.44% (2.44 USDT) | 2.31% | 0.28 | 6.4 | KEEP |

### Scoring (tính thủ công)

| Metric | Weight | > 5% P/L = 10 | > 2% = 7 | > 0 = 4 | < 0 = 0 |
|:--|:--|:--|:--|:--|:--|
| Total Profit | 25% | | | | |
| Max Drawdown | 25% | < 3% = 10 | < 5% = 7 | < 10% = 4 | > 10% = 0 |
| Sharpe | 20% | > 1.0 = 10 | > 0.5 = 7 | > 0 = 4 | < 0 = 0 |
| Win Rate | 15% | > 50% = 10 | > 40% = 7 | > 30% = 4 | < 30% = 2 |
| Trades | 15% | > 200 = 10 | > 100 = 7 | > 50 = 4 | < 50 = 2 |

**Score > 7 = KEEP. Score 5-7 = REFINE. Score < 5 = REJECT.**

## Bước 6: Cập Nhật Docs

Sau khi hoàn thành, cập nhật:
1. `docs/STRATEGY_LOG.md` — thêm entry cho mỗi experiment
2. `docs/DECISIONS.md` — ghi strategies nào KEEP/REJECT và lý do  
3. `CLAUDE.md` — cập nhật trạng thái hiện tại

## Lưu Ý Quan Trọng

- Nếu backtest lỗi (KeyError, import error): FIX code rồi chạy lại
- Nếu futures data không download được: dùng spot config thay thế
- Mỗi hyperopt mất ~5-10 phút
- Tổng thời gian: ~30-60 phút
- SAU KHI XONG: `git add -A && git commit -m "experiment results: E01-E10"`
