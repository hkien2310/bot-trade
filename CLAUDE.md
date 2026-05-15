# SMC Trading Bot — AI Context

> **ĐỌC FILE NÀY ĐẦU TIÊN KHI BẮT ĐẦU MỘT PHIÊN LÀM VIỆC MỚI**
> (Cập nhật mới nhất: Tháng 05/2026 - SMC V3 Challenger)

## Mục Tiêu Dự Án
Xây dựng bot giao dịch tự động hoàn toàn (Scalping/Swing) sử dụng Smart Money Concepts (SMC). Mục tiêu là tạo ra "Cỗ Máy In Tiền" với Winrate cực cao và Drawdown cực thấp.

## Tech Stack (Hiện Tại)
- **Framework**: [Freqtrade](https://www.freqtrade.io)
- **Runtime**: Docker (VPS Ubuntu IP: 103.172.79.72)
- **Language**: Python (strategy files)
- **Exchange**: Binance Futures (**Isolated Margin, x10 Leverage**)
- **Pairs (12)**: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT, ADA/USDT, DOGE/USDT, AVAX/USDT, DOT/USDT, LINK/USDT, SUI/USDT, TON/USDT
- **Timeframe**: 15m

## Cấu Trúc Dự Án (V3)
```
/Users/hoangkien/Youtube/trade/
├── CLAUDE.md                           ← TỔNG QUAN DỰ ÁN
├── V3_REPORT.md                        ← REPORT KẾT QUẢ V3 CHÍNH THỨC
├── docker-compose.yml                  ← Docker config (đang trỏ vào V3)
├── docs/
│   ├── STRATEGY_LOG.md                 ← Nhật ký hiệu suất các phiên bản
│   ├── DECISIONS.md                    ← Quyết định chiến lược (Chân Lý)
│   └── UPGRADE_PLAN.md                 ← Kế hoạch Phase tiếp theo
└── user_data/
    ├── config-futures.json             ← Config chính (12 pairs, x10 Leverage)
    ├── strategies/
    │   ├── SmartMoneyConceptsV3.py     ← Strategy Code (SMC V3 Challenger)
    │   └── SmartMoneyConceptsV3.json   ← File lưu tham số Hyperopt (Núm vặn)
    ├── data/binance/                   ← Dữ liệu nến quá khứ
    └── backtest_results/               ← Nơi lưu file zip kết quả backtest
```

## Quy Tắc Bất Biến (Đã Test Thực Tế)
1. **FUTURES ONLY** — Không đánh Spot. Tối đa x10 Leverage.
2. **LIQUIDITY SWEEP (RÂU NẾN)** — V3 chỉ tập trung bắt các cú quét thanh khoản (Turtle Soup). Từ chối giao dịch trên Order Block / FVG.
3. **KHÔNG LỌC XU HƯỚNG 1H** — HTF Alignment đã bị chứng minh là làm giảm lợi nhuận.
4. **TRAIING STOP BẮT BUỘC** — V3 sử dụng Trailing Stop và nhiều mức ROI linh hoạt. Stoploss kéo dài (-32%) để gồng râu nến.

## Trạng Thái Hiện Tại (THE CHAMPION)
- **Strategy version**: SmartMoneyConceptsV3 (SMC V3 Challenger)
- **Status**: 🟢 **CHẠY LIVE TRÊN VPS** (103.172.79.72)
- **Kết quả Backtest 16.4 tháng**: 
  - **Lợi nhuận**: 2717%
  - **Win Rate**: 97.5%
  - **Max Drawdown**: 1.24%
  - **Tần suất**: ~5.5 lệnh/ngày

## Lệnh Thường Dùng (Dành Cho AI)
```bash
# Backtest V3
rtk docker-compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config-futures.json \
  --strategy SmartMoneyConceptsV3 \
  --timerange 20250101-20260515

# Hyperopt
rtk docker-compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config-futures.json \
  --strategy SmartMoneyConceptsV3 \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy roi stoploss trailing \
  -j 8 -e 500
```
