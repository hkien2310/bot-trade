# STRATEGY LOG — NHẬT KÝ CHIẾN LƯỢC

> Nhật ký ghi chép toàn bộ hành trình thử nghiệm các chiến lược. Chỉ những chiến lược vượt qua vòng loại mới được ghi vào đây.

---

## 🏆 KẾT QUẢ HIỆN TẠI: THE CHAMPION (V3)
**Strategy:** `SmartMoneyConceptsV3` (Phiên bản 12 Pairs)
**Status:** 🟢 **CHẠY LIVE TRÊN VPS** (Từ 15/05/2026)

### Thông số Backtest Ghi Nhận (Tháng 01/2025 - Tháng 05/2026)
| Tiêu chí | Đạt được | Đánh giá |
|:--|:--|:--|
| Lợi nhuận Tổng | **2717.19%** | Xuất Sắc (Gấp 27 lần vốn gốc) |
| Win Rate | **97.5%** | Siêu Việt (2702 Win / 69 Loss) |
| Max Drawdown | **1.24%** | Vô Địch (Bảo toàn vốn tuyệt đối) |
| Sharpe Ratio | 9.44 | Cực Cao (Vượt xa tiêu chuẩn quỹ) |
| Đòn bẩy | x10 | Tối ưu |
| Tổng Số Lệnh | 2771 | ~5.5 lệnh / ngày |

### Triết Lý Giao Dịch
1. **Liquidity Sweep Only:** Bot không dự đoán giá. Nó chờ đám đông giao dịch Breakout hoặc chặn đầu, sau đó nó chờ Cá mập giật râu nến (quét thanh khoản/Stop-hunt) để loại bỏ đám đông. Ngay khi nến rút chân xác nhận sự hình thành cấu trúc rũ bỏ, Bot lập tức vào lệnh.
2. **Khung thời gian:** 15m.
3. **Quản trị:** Vào lệnh Limit. Chốt lời ROI chia nhiều nấc để đảm bảo 97% lệnh đều chốt lãi nhanh nhất có thể. Cắt lỗ được kéo dài (-32.2%) để né râu nến ảo.

---

## 📉 LỊCH SỬ CÁC BẢN CŨ ĐÃ BỊ LOẠI

### V2 - SMC Monster (Bị loại vì lợi nhuận chưa tối đa)
- Triết lý: Kết hợp Order Block (OB), FVG và Liquidity Sweep. Cần lọc xu hướng HTF 1 Giờ.
- Lợi nhuận: 720% (Trên 5 Pairs).
- Win Rate: ~61%
- Drawdown: ~9.2%
- Lý do loại: Dù có lãi 720%, nhưng bộ lọc Order Block quá rườm rà, lỡ mất nhiều kèo ngon. Đã bị nâng cấp lên V3.

### V1 - Early Days (Bị loại vì Rủi ro cao)
- Triết lý: Đánh Spot, DCA lưới.
- Lợi nhuận: Âm vốn.
- Drawdown: Lên tới 98% do không có Stoploss hợp lý.
- Lý do loại: Kém hiệu quả, tốn thời gian.
