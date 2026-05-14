# Phân Tích Các Trường Phái Trading & Khả Năng Tự Động Hoá (Bot)

> **Mục đích**: Tài liệu tham khảo để chọn phương pháp tối ưu cho bot.
> **Context**: Vốn $100, Binance Futures x2, Freqtrade, mục tiêu R:R 1:2+, win rate ≥ 45%.
> **Ngày tạo**: 2026-05-14

---

## 1. Tổng Quan — 2 Trường Phái Lớn

### A. Indicator-Based (Kỹ thuật cổ điển)
- **Triết lý**: Dùng công thức toán (RSI, MACD, BB...) để đo trạng thái thị trường
- **Ưu**: Dễ code, dễ backtest, có sẵn trong TA-Lib
- **Nhược**: Chỉ phản ứng SAU KHI giá đã di chuyển (lagging)
- **R:R điển hình**: 1:1 → 1:1.5

### B. Smart Money / Institutional (Theo dòng tiền lớn)
- **Triết lý**: Phát hiện hành vi của "big players" → đi theo họ
- **Ưu**: Entry chính xác hơn, SL chặt hơn → R:R cao hơn
- **Nhược**: Phức tạp hơn để code, cần hiểu sâu price action
- **R:R điển hình**: 1:2 → 1:5

---

## 2. Chi Tiết Từng Phương Pháp

### 2.1 RSI + Bollinger Bands (Đang dùng — MeanReversion)

**Cách hoạt động:**
- RSI < 30 = quá bán → mua
- Giá chạm BB dưới = quá rẻ → mua
- Kết hợp cả 2 = xác suất cao hơn

**Kết quả đã test (E10):**
- Win rate: 68.2%
- Avg profit/trade: 0.24% (quá thấp)
- 66 trades / 498 ngày

**Đánh giá cho bot:**
| Tiêu chí | Điểm |
|:--|:--|
| Dễ code | ⭐⭐⭐⭐⭐ |
| Backtest | ⭐⭐⭐⭐⭐ |
| R:R tiềm năng | ⭐⭐ (1:1) |
| Độ chính xác entry | ⭐⭐⭐ |
| Phù hợp mục tiêu | ⚠️ Cần cải thiện exit |

**Kết luận**: Entry signal tốt, nhưng exit logic cần thay đổi căn bản để đạt R:R 1:2+.

---

### 2.2 SMC — Smart Money Concepts

**Triết lý**: Institutions (ngân hàng, quỹ lớn) không trade như retail. Họ cần liquidity (thanh khoản) để vào/ra lệnh lớn. SMC giúp đọc "dấu chân" của họ.

**Các concept chính:**

#### 2.2.1 Break of Structure (BOS) ✅ DỄ CODE
```
Uptrend:  Higher High → Higher Low → Higher High
          Khi giá phá Higher High mới → BOS xác nhận trend tiếp tục

Downtrend: Lower Low → Lower High → Lower Low  
           Khi giá phá Lower Low mới → BOS xác nhận trend tiếp tục
```
- **Code**: So sánh swing high/low bằng rolling window
- **Dùng cho bot**: XÁC NHẬN HƯỚNG trade (thay cho ADX)
- **Độ khó**: ⭐⭐ (trung bình)

#### 2.2.2 Change of Character (CHoCH) ✅ DỄ CODE
```
Đang downtrend (Lower Low liên tục)
→ Bất ngờ tạo Higher Low
→ CHoCH = tín hiệu đảo chiều
→ ENTRY LONG
```
- **Code**: Phát hiện khi chuỗi Lower Low bị phá
- **Dùng cho bot**: TÍN HIỆU ĐẢO CHIỀU — entry sớm khi trend thay đổi
- **Độ khó**: ⭐⭐ (trung bình)

#### 2.2.3 Fair Value Gap (FVG) ✅ CODE ĐƯỢC
```
Nến 1: High = 100
Nến 2: Nến lớn bất thường (big move)
Nến 3: Low = 105

→ Gap giữa nến 1 high (100) và nến 3 low (105) = FVG
→ Giá thường QUAY LẠI fill gap này
→ Entry khi giá quay lại vùng 100-105
```
- **Code**: So sánh high[2] với low[0], nếu có gap → đánh dấu zone
- **Dùng cho bot**: TÌM ĐIỂM VÀO CHÍNH XÁC — giá quay lại FVG → entry
- **Độ khó**: ⭐⭐⭐ (trung bình-khó)
- **R:R rất tốt**: SL ngay ngoài FVG → rất chặt

#### 2.2.4 Order Block (OB) ⭐⭐⭐⭐ KHÓ
```
Nến cuối cùng trước khi giá phá structure (BOS)
= Vùng mà institutions đã đặt lệnh lớn
→ Giá sẽ quay lại test vùng này
→ Entry khi giá chạm Order Block
```
- **Code**: Tìm nến cuối trước BOS, đánh dấu vùng high-low
- **Dùng cho bot**: ENTRY POINT cực kì chính xác, SL chặt
- **Độ khó**: ⭐⭐⭐⭐ (khó — cần xác định swing structure đúng)
- **R:R tiềm năng**: 1:3 → 1:5

#### 2.2.5 Liquidity Sweep ⭐⭐⭐ TRUNG BÌNH
```
Giá phá qua đỉnh/đáy cũ (hunt stoploss của retail)
→ Rồi quay lại ngay lập tức
→ = Big money đã gom xong liquidity
→ ENTRY theo hướng quay lại
```
- **Code**: Giá vượt previous high/low → rồi close lại bên trong → signal
- **Dùng cho bot**: FILTER mạnh — chỉ trade sau khi liquidity đã bị sweep
- **Độ khó**: ⭐⭐⭐

#### 2.2.6 Premium/Discount Zone ✅ RẤT DỄ
```
Lấy range (đỉnh - đáy gần nhất)
Chia đôi = Equilibrium (50%)
Trên 50% = Premium → CHỈ SHORT
Dưới 50% = Discount → CHỉ LONG
```
- **Code**: `(high_range - low_range) / 2`
- **Dùng cho bot**: FILTER đơn giản nhưng hiệu quả
- **Độ khó**: ⭐ (rất dễ)

---

### 2.3 Wyckoff Method

**Triết lý**: Thị trường có 4 pha lặp lại:
1. **Accumulation** — big money gom hàng (giá đi ngang ở đáy)
2. **Markup** — giá tăng (trend up)
3. **Distribution** — big money xả hàng (giá đi ngang ở đỉnh)
4. **Markdown** — giá giảm (trend down)

**Phát hiện bằng gì:**
- Volume tăng + giá không tăng = accumulation
- Volume giảm + giá tăng = distribution sắp xảy ra

**Đánh giá cho bot:**
| Tiêu chí | Điểm |
|:--|:--|
| Dễ code | ⭐⭐ (khó xác định pha chính xác) |
| Backtest | ⭐⭐⭐ |
| R:R tiềm năng | ⭐⭐⭐⭐ (1:3+) |
| Độ chính xác | ⭐⭐⭐ (khi đúng pha thì rất chính xác) |

**Kết luận**: Phù hợp cho swing trading (giữ lệnh dài). Khó auto hoá hoàn toàn nhưng một số elements (volume divergence) có thể thêm vào bot.

---

### 2.4 Volume Spread Analysis (VSA)

**Triết lý**: Volume + kích thước nến tiết lộ ý định của big money.

**Tín hiệu chính:**
| Pattern | Volume | Nến | Ý nghĩa |
|:--|:--|:--|:--|
| **Stopping Volume** | Cực cao | Nhỏ, đuôi dài | Big money chặn đà giảm → sắp đảo chiều |
| **No Demand** | Cực thấp | Nhỏ, tăng yếu | Không ai muốn mua → giá sẽ giảm |
| **Climax** | Cực cao | Lớn | Đỉnh/đáy → sắp đảo chiều |
| **Test** | Thấp | Nhỏ, vào vùng supply/demand | Big money test xem còn ai bán không |

**Đánh giá cho bot:**
| Tiêu chí | Điểm |
|:--|:--|
| Dễ code | ⭐⭐⭐ (volume + candle body + wick) |
| Backtest | ⭐⭐⭐⭐ |
| R:R tiềm năng | ⭐⭐⭐ (1:2) |
| Kết hợp với SMC | ⭐⭐⭐⭐⭐ (rất tốt) |

**Kết luận**: VSA đơn giản hơn SMC nhưng bổ trợ rất tốt. Có thể dùng làm filter.

---

### 2.5 Price Action Patterns (Nến Nhật)

**Các pattern code được trong TA-Lib:**
- Engulfing (nhấn chìm)
- Hammer / Shooting Star (búa)
- Doji
- Morning Star / Evening Star
- Three White Soldiers / Three Black Crows

**Đánh giá cho bot:**
| Tiêu chí | Điểm |
|:--|:--|
| Dễ code | ⭐⭐⭐⭐⭐ (TA-Lib có sẵn hàm) |
| Backtest | ⭐⭐⭐⭐⭐ |
| R:R tiềm năng | ⭐⭐ (1:1, cần kết hợp thêm) |
| Standalone | ⚠️ Yếu khi dùng một mình |

**Kết luận**: Tốt nhất làm FILTER bổ trợ, không nên là signal chính.

---

### 2.6 FreqAI — Machine Learning (Phase cuối)

**Cách hoạt động:**
- Train model trên historical data
- Model tự học pattern nào dẫn đến lãi/lỗ
- Tự động predict entry/exit

**Đánh giá:**
| Tiêu chí | Điểm |
|:--|:--|
| Dễ code | ⭐ (cần ML knowledge) |
| Backtest | ⭐⭐⭐⭐ (walk-forward validation) |
| R:R tiềm năng | ❓ (phụ thuộc features) |
| Overfitting risk | ⚠️ CAO |

**Kết luận**: Để phase cuối khi đã có strategy rule-based hoạt động tốt. FreqAI dùng để fine-tune, không dùng để tìm strategy từ đầu.

---

## 3. Ma Trận So Sánh Tổng Hợp

| Phương pháp | Dễ code | R:R | Win Rate kỳ vọng | Độ tin cậy | Ưu tiên |
|:--|:--|:--|:--|:--|:--|
| BB + RSI (hiện tại) | ⭐⭐⭐⭐⭐ | 1:1 | 60-70% | ⭐⭐⭐ | Đã có |
| **SMC (BOS+FVG+OB)** | ⭐⭐⭐ | **1:3-1:5** | 45-55% | ⭐⭐⭐⭐ | **🥇 #1** |
| VSA | ⭐⭐⭐ | 1:2 | 50-60% | ⭐⭐⭐ | 🥈 #2 (filter) |
| Wyckoff | ⭐⭐ | 1:3+ | 50% | ⭐⭐⭐ | Phase sau |
| Price Action | ⭐⭐⭐⭐⭐ | 1:1 | 50% | ⭐⭐ | Filter bổ trợ |
| FreqAI | ⭐ | ❓ | ❓ | ⚠️ | Phase cuối |

---

## 4. Đề Xuất — Kế Hoạch Triển Khai

### Phase A: Quick Win (Session tiếp theo)
**MeanReversion v2 = Entry hiện tại + Exit mới**
- Giữ entry logic (BB + RSI + ADX + StochRSI) → đã proven 68% win rate
- Thay exit: Fixed SL (-2%) + Trailing TP
- Hyperopt tìm SL/trailing tối ưu trong range constraint
- **Mục tiêu**: R:R 1:2, mỗi trade ±$1-$2
- **Thời gian**: 30 phút

### Phase B: SMC Lite (Session sau)
**Thêm BOS + FVG vào entry filter**
- Implement BOS (xác định trend structure)
- Implement FVG (tìm vùng entry chính xác)
- Kết hợp: Chỉ trade khi BB+RSI signal + BOS confirm + FVG zone
- **Mục tiêu**: Giảm false signal, tăng R:R lên 1:3
- **Thời gian**: 1-2 giờ code + test

### Phase C: SMC Full (Tuần sau)
**Build SMC strategy riêng biệt**
- BOS → CHoCH → Order Block → Entry
- Liquidity sweep filter
- Premium/Discount zone filter
- **Mục tiêu**: Strategy hoàn toàn mới, R:R 1:3-1:5
- **Thời gian**: Nhiều session

### Phase D: ML Enhancement (Tháng sau)
**FreqAI bổ trợ**
- Dùng SMC features làm input cho ML model
- Model predict xác suất trade thành công
- **Chỉ làm khi Phase B/C đã profitable**

---

## 5. Decision Log (Brainstorm Session 2026-05-14)

| # | Quyết định | Lý do |
|:--|:--|:--|
| 1 | Giữ MeanReversion entry logic | Win rate 68% đã proven |
| 2 | Thay exit: Fixed SL + Trailing TP | Avg profit 0.24% quá thấp, cần R:R 1:2+ |
| 3 | SL target ~-2% | Cho giá thở, R:R 1:2 → TP ≥ +4% |
| 4 | Trailing TP thay fixed TP | Bắt big winners, cut losses short |
| 5 | SMC (BOS+FVG) là ưu tiên #1 tiếp theo | Phù hợp R:R 1:3+, code được |
| 6 | FreqAI để phase cuối | Cần rule-based thành công trước |
| 7 | Hyperopt tìm params, không chọn thủ công | Máy tìm tối ưu tốt hơn cảm tính |

---

## 6. Assumptions (Cần Xác Nhận)

1. Market 2025-2026 vẫn sideway/downtrend → MeanReversion vẫn phù hợp
2. 5 pairs (BTC, ETH, SOL, BNB, XRP) đủ cho testing
3. Freqtrade có thể implement BOS/FVG bằng pandas (không cần thư viện ngoài)
4. 15m timeframe vẫn phù hợp cho SMC (thường SMC dùng trên 1h+)

---

## 7. Open Questions (Cần Trả Lời Trước Khi Code)

1. **Timeframe cho SMC**: 15m hay nên chuyển lên 1h? (SMC truyền thống dùng 1h/4h)
2. **Multi-TF**: Entry trên 15m nhưng structure analysis trên 1h?
3. **Số lượng pairs**: Thêm pairs (DOGE, AVAX...) hay giữ 5 pairs?
4. **Risk per trade**: Giữ $15/trade hay tăng lên khi profitable?
