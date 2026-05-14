# Setup Guide — Hướng Dẫn Chạy Bot

## Prerequisites
- Docker Desktop (Mac)
- Internet connection (cho exchange API)

## Quick Start

### 1. Mở Docker Desktop
```bash
open -a Docker
```

### 2. Chạy Dry-Run (Paper Trade)
```bash
cd /Users/hoangkien/Youtube/trade
docker compose up -d
```

### 3. Xem Web UI
Mở browser: http://localhost:8080
- Username: `freqtrader`
- Password: `freqtrader`

### 4. Xem Logs
```bash
docker compose logs -f freqtrade
```

### 5. Dừng Bot
```bash
docker compose down
```

## Backtest Commands

### Chạy backtest
```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.json \
  --strategy ScalpEmaRsiVwap \
  --timerange 20250101-20260514 \
  --timeframe 5m
```

### Hyperopt (tối ưu params)
```bash
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config.json \
  --strategy ScalpEmaRsiVwap \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell \
  --epochs 300 -j 4
```

### Download data mới
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config.json \
  --timeframe 5m --timerange 20250101-
```

## Live Trading Setup (CHƯA KÍCH HOẠT)

### Bước 1: Tạo Binance API Key
1. Login Binance → API Management
2. Create API key
3. Enable: ✅ Read ✅ Spot Trading
4. Disable: ❌ Withdraw ❌ Futures ❌ Margin
5. Whitelist IP (IP VPS của bạn)

### Bước 2: Cập nhật config.json
```json
{
    "dry_run": false,
    "exchange": {
        "key": "YOUR_API_KEY",
        "secret": "YOUR_API_SECRET"
    }
}
```

### Bước 3: Telegram Bot (Optional)
1. Tạo bot qua @BotFather trên Telegram
2. Lấy token và chat_id
3. Cập nhật config.json:
```json
{
    "telegram": {
        "enabled": true,
        "token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    }
}
```

## Troubleshooting

### Docker không chạy
```bash
open -a Docker
# Đợi 10-30 giây
docker info
```

### Strategy error
```bash
# Kiểm tra syntax
docker compose run --rm freqtrade backtesting --strategy-list ScalpEmaRsiVwap
```

### Data cũ
```bash
# Re-download
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config.json \
  --timeframe 5m --timerange 20250101-
```
