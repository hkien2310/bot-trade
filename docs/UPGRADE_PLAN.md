# UPGRADE PLAN: SMC V3 & BEYOND

> Kế hoạch nâng cấp và theo dõi hiệu suất hệ thống Giao dịch Tự động.

## 📊 TRẠNG THÁI HIỆN TẠI (ĐÃ HOÀN THÀNH)
*   **Chiến lược (Strategy):** SmartMoneyConceptsV3 (SMC V3 Challenger)
*   **Thị trường:** Binance Futures
*   **Đòn bẩy (Leverage):** x10
*   **Tài sản (Pairs):** 12 Đồng Coin (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, DOT, LINK, SUI, TON)
*   **Hạ tầng:** Chạy Live/Dry-run 24/7 qua Docker trên VPS Ubuntu (IP: 103.172.79.72)
*   **Triết lý cốt lõi:** Bắt Râu Turtle Soup (Liquidity Sweep) trên khung 15 Phút, chu kỳ 24 nến.

---

## 🚀 KẾ HOẠCH NÂNG CẤP TIẾP THEO (V4)

### Phase 1: Giám Sát & Thu Thập Dữ Liệu V3 (Tháng 05/2026 - Tháng 06/2026)
- [ ] Giữ nguyên cấu hình V3 trên VPS chạy trong 2 đến 4 tuần.
- [ ] Ghi nhận Win Rate thực tế so với Win Rate lý thuyết (97.5%).
- [ ] Theo dõi độ trượt giá (Slippage) khi chạy Live Futures.
- [ ] Nếu lợi nhuận thực tế đạt > 50% kỳ vọng backtest, bắt đầu nạp tiền thật (Live Account).

### Phase 2: Mở Khóa AI (FreqAI - Tùy chọn)
- [ ] Nếu thị trường thay đổi cấu trúc khiến thuật toán Liquidity Sweep bị bắt bài.
- [ ] Bắt đầu nghiên cứu tích hợp Machine Learning (FreqAI) bằng PyTorch/TensorFlow.
- [ ] Thuê VPS cấu hình cao (hoặc chạy Local trên máy Mac) để Train AI dự đoán giá thay vì dùng các tham số tĩnh.

### Phase 3: Tự Động Hóa Quản Trị Rủi Ro Chéo
- [ ] Cài đặt cơ chế giới hạn Drawdown toàn danh mục (Portfolio Max Drawdown).
- [ ] Theo dõi mối tương quan (Correlation) giữa 12 cặp coin để tránh rủi ro hệ thống khi Bitcoin sập.
