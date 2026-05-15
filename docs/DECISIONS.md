# DECISIONS LOG — NHẬT KÝ QUYẾT ĐỊNH DỰ ÁN

> File này ghi lại các quyết định mang tính "Chân Lý" đã được hệ thống thống nhất. Tuyệt đối không đảo ngược các quyết định này nếu không có bằng chứng Backtest mới.

---

## 🟢 NHỮNG QUYẾT ĐỊNH ĐÃ CHỌN (ĐANG ÁP DỤNG)

### D010: Giao Dịch Hợp Đồng Tương Lai (Futures) Thay Vì Spot (2026-05)
**Lý do:**
- Giao dịch Futures cho phép sử dụng đòn bẩy và kiếm lợi nhuận từ cả 2 chiều thị trường (Long/Short). Mức Leverage x10 đã được backtest tối ưu.

### D011: Lọc Danh Sách 12 Đồng Coin Thanh Khoản Cao (2026-05)
**Lý do:**
- Các đồng coin top (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, DOT, LINK, SUI, TON) có tính thanh khoản cao, giảm thiểu trượt giá (slippage) và râu nến ảo do thao túng giá. Đánh 12 cặp giúp giảm rủi ro tập trung (Max Drawdown giảm xuống 1.2%).

### D012: Chuyển Sang Bắt Râu "Liquidity Sweep" (SMC V3 Challenger)
**Lý do:**
- Backtest AI chứng minh rằng việc bắt đáy/đỉnh tại vùng Order Block hoặc FVG có Winrate thấp hơn và dễ bị stop-hunt. 
- Chiến thuật Sweep (Turtle Soup) chờ đám đông bị Stop-hunt rồi mới vào lệnh, tạo ra Winrate 97.5%.

### D013: Vứt Bỏ Bộ Lọc Xu Hướng 1 Giờ (HTF Alignment)
**Lý do:**
- Các cú quét thanh khoản mạnh mang tính chất "giật nến", không phụ thuộc vào xu hướng lớn. Việc lọc bằng xu hướng 1 Giờ làm giảm đi rất nhiều lệnh thắng tiềm năng.

### D014: Gồng Lỗ Sâu (-32.2%) Khung 15m
**Lý do:**
- Tránh việc bị sàn "quét râu" cháy tài khoản hoặc hit Stoploss oan uổng. Tỉ lệ Winrate 97% đủ sức cover cho các lệnh gồng lỗ này.

---

## 🔴 NHỮNG QUYẾT ĐỊNH ĐÃ LOẠI BỎ (KHÔNG DÙNG NỮA)

### R005: Chơi Spot (Chỉ Mua Lên)
**Lý do loại:** Lợi nhuận quá chậm, không phù hợp cho hệ thống tự động hóa tần suất cao.

### R006: Chiến Thuật Order Block & FVG (SMC V2)
**Lý do loại:** Bị V3 Challenger đánh bại hoàn toàn (Lợi nhuận V2 là 720%, bị V3 đè bẹp với 2717%). Hủy bỏ việc giao dịch theo SMC truyền thống.

### R007: Lưu Trữ Database Trên Mac
**Lý do loại:** Máy Mac có thể bị Sleep. Đã quyết định chuyển toàn bộ hệ thống lên VPS Ubuntu 24/7 (103.172.79.72).
