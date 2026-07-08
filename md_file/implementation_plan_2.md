# Kế hoạch Triển khai: Bước 4 - Xử lý lỗi Perfect Separation cho mô hình Logistic (Donation)

Mô hình dự đoán quyết định Quyên góp (Donation) hiện đang gặp lỗi **Phân tách hoàn hảo (Perfect Separation)** do tỷ lệ đồng ý quá cao (88% tương đương 271/307 mẫu). Trong hồi quy Logistic truyền thống (MLE), điều này dẫn đến việc các hệ số ước lượng (Beta) và sai số chuẩn (Standard Errors) bị thổi phồng vô hạn, khiến kết quả mất đi độ tin cậy.

Kế hoạch này đề xuất sử dụng thuật toán **Firth's Penalized Likelihood Regression** để khắc phục triệt để lỗi này. 

## Proposed Changes

Chúng tôi sẽ tạo một script Python mới có tên `run_firth_logistic.py` để xử lý riêng biệt mô hình Donation.

### Thuật toán Firth Logistic Regression
Thay vì tối đa hóa hàm Log-Likelihood tiêu chuẩn ($L$), phương pháp Firth cộng thêm một hàm phạt (penalty) dựa trên ma trận thông tin Fisher ($I$):
$$ L^* = L + 0.5 \ln|I| $$
Việc này giúp:
- Triệt tiêu chệch (bias) của các ước lượng trong mẫu nhỏ hoặc mẫu mất cân bằng cực đại.
- Giữ các hệ số Beta và Odds Ratio (OR) ở mức hữu hạn và hợp lý (không bị thổi phồng lên mức hàng nghìn).
- Khôi phục tính hợp lệ của các kiểm định giả thuyết (p-value).

### Quy trình thực hiện
1. **Làm sạch & Chuẩn bị dữ liệu:** Tương tự `run_final_logistic.py`, xử lý các biến số thành biến phân loại dummy (Drop first) và làm sạch NA.
2. **Lập trình hàm Firth's Likelihood:** Tự định nghĩa hàm Log-likelihood bị phạt và sử dụng thuật toán tối ưu `scipy.optimize.minimize` (phương pháp L-BFGS-B hoặc Newton-CG) để tìm bộ trọng số tối ưu.
3. **Tính toán thống kê suy diễn:** Tính toán ma trận hiệp phương sai từ ma trận Fisher tại điểm hội tụ để lấy ra Sai số chuẩn (SE), từ đó tính Z-statistic, P-value và Odds Ratio.
4. **Xuất báo cáo:** Lưu các chỉ số thống kê chuẩn mực vào file `Logistic_Results_Donation_Firth.csv`.
5. **Cập nhật Readme.md (Nếu cần):** Ghi chú lại rằng mô hình Donation đã được xử lý thành công bằng phương pháp Firth's Penalization, đảm bảo tính vững chắc về mặt học thuật.

## Open Questions

> [!IMPORTANT]
> **Đánh giá mức độ ý nghĩa thống kê:**
> Trong bài kiểm tra sơ bộ bằng hàm Firth, biến `MEAN CES` (Dịch vụ Văn hóa) có giá trị p-value = 0.0725 (ý nghĩa biên ở mức 10%), và biến `Time` (Thời gian lưu trú) có p-value = 0.0548. Trong khi đó, `MEAN DES` tác động tiêu cực rất mạnh (p=0.0048). Bạn có đồng ý sử dụng ngưỡng ý nghĩa $\alpha = 0.10$ cho mô hình này trong bài nghiên cứu để biện luận cho vai trò của `MEAN CES` không? 

## Verification Plan

### Automated Tests
- Chạy script `run_firth_logistic.py`.
- Kiểm tra tính hội tụ (Convergence) của thuật toán tối ưu (`res.success == True` hoặc đạt mức sai số tối thiểu).

### Manual Verification
- Kiểm tra file `Logistic_Results_Donation_Firth.csv` xem các Odds Ratio có nằm ở ngưỡng hợp lý không (ví dụ: từ 0.1 đến 30, thay vì các con số vô cực hay hàng tỷ như mô hình MLE gặp lỗi).
- Đối chiếu lại các kết luận (DES làm giảm quyên góp, CES làm tăng, RES không ảnh hưởng) xem có đúng với khung lý thuyết đặt ra hay không.
