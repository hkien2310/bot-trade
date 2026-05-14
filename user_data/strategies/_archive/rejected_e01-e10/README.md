# Rejected Strategies — E01-E10 Matrix (2026-05-14)

> ⚠️ CÁC STRATEGY NÀY ĐÃ THẤT BẠI. KHÔNG SỬ DỤNG LẠI TRỰC TIẾP.
> Lưu ở đây để tham khảo và TRÁNH lặp lại cùng sai lầm.

## Bối cảnh
- Vốn: $100 USDT
- Leverage: x2 (Binance Futures, isolated)
- Data: 20250101 - 20260514 (~498 ngày)
- 5 pairs: BTC, ETH, SOL, BNB, XRP

## Kết quả

| File | Style | Lý do REJECT |
|:--|:--|:--|
| `ScalpTight.py` | Scalping R:R 1:1 | Quá ít trade (2-12), không đủ sample. Hyperopt cũng không cải thiện. |
| `ScalpTight.json` | Hyperopt params | Params tốt nhất cũng chỉ 2 trades trong 498 ngày = vô nghĩa. |
| `TrendRider.py` | Swing R:R 1:3 | Win rate 14-23% trên Futures. Leverage x2 + wide SL = bị stopout liên tục. |
| `BreakoutCatcher.py` | Breakout R:R 1:3 | False breakout liên tục. Win rate 2.5-7.2%. Mất -28% (Spot) đến -84% (Futures). |
| `DCAGrid.py` | DCA/Grid | Cháy account -90% khi market sập. DCA + leverage = TỰ SÁT TÀI CHÍNH. |

## Bài học rút ra (KHÔNG LẶP LẠI)

1. **KHÔNG dùng DCA/Grid với leverage** — khi thị trường sập, mua thêm = chết nhanh hơn
2. **KHÔNG dùng Breakout strategy trên 5m** — quá nhiều noise, false breakout 90%+
3. **Trend Following cần TF lớn hơn (15m/1h)** khi dùng leverage — 5m quá nhạy
4. **Scalping cần spread thấp + fee thấp** — với fee 0.1% trên Spot / 0.05% Futures, TP 0.3-0.5% không đủ cover
5. **Hyperopt bắt buộc trước khi deploy Futures** — default params LUÔN fail

## Strategy duy nhất KEEP từ matrix này
→ `MeanReversion.py` + `MeanReversion.json` (E10, nằm ở folder strategies chính)
