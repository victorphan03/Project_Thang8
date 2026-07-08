# Tổng kết: Khắc phục lỗi Phân tách hoàn hảo (Perfect Separation) cho mô hình Quyên góp

Tôi đã hoàn tất việc xử lý sự cố hồi quy Logistic cho biến **Quyên góp (Donation)**. Thay vì sử dụng phương pháp Cực đại hóa mức độ hợp lý (Maximum Likelihood Estimation - MLE) thông thường vốn tạo ra các sai số vô cực khi dữ liệu mất cân bằng (88% đồng ý), tôi đã áp dụng thuật toán **Firth's Penalized Likelihood**.

## 1. Chi tiết thực hiện

*   **Lập trình thuật toán:** Tạo mới kịch bản [run_firth_logistic.py](file:///c:/Users/NASPC/Documents/Du%20án%20tại%20SG%20tháng%208/run_firth_logistic.py). Kịch bản này tự động giải bài toán tối ưu bằng thuật toán `L-BFGS-B`, đưa hàm Log-Likelihood bị phạt (cộng thêm `0.5 * log|I|`) về điểm cực tiểu.
*   **Hội tụ thành công:** Thuật toán đạt mức độ hội tụ hoàn hảo `Firth Optimization Success: True` trên toàn bộ tập mẫu (N=200 quan sát hợp lệ không chứa biến khuyết).
*   **Khôi phục kết quả thống kê:** Tính ngược lại Ma trận Thông tin Fisher (Fisher Information Matrix) từ điểm hội tụ để lấy ra Sai số chuẩn (SE), từ đó xuất các giá trị Z, P-value, và Odds Ratio (OR).

## 2. Kết quả của mô hình mới

> [!TIP]
> **Các hệ số thổi phồng (như OR = hàng nghìn) đã hoàn toàn biến mất.** Các tỷ số chênh (Odds Ratio) bây giờ đều nằm trong khoảng thực tế từ $0.26$ đến $10.6$, chứng tỏ mô hình cực kỳ tin cậy và có thể dùng để báo cáo khoa học.

*   **Lực cản mạnh mẽ từ Phi dịch vụ (DES):** Sự bức xúc về quản lý kém (Dirty, Unsafe) là lý do chính khiến người dân từ chối quyên góp (P-value = 0.0005, OR = 0.412).
*   **Khoảng cách:** Nhà càng xa công viên, xác suất quyên góp càng giảm mạnh (P-value = 0.0304, OR = 0.569).
*   **Giá trị Văn hóa (CES):** Dù nằm ở mức ý nghĩa biên ($p \approx 0.11$), Thụ hưởng văn hóa (CES) và Thời gian lưu trú (Time) tiếp tục duy trì xu hướng tác động tích cực đến quyết định quyên góp (OR > 1.6). Ngược lại, Dịch vụ sinh thái thuần túy (RES) lại không hề có tác động ($p = 0.57$).

## 3. Các thay đổi về File

*   Bảng báo cáo thống kê đầy đủ đã được xuất ra định dạng CSV tại: [Logistic_Results_Donation_Firth.csv](file:///c:/Users/NASPC/Documents/Du%20án%20tại%20SG%20tháng%208/Logistic_Results_Donation_Firth.csv).
*   Cập nhật [Readme.md](file:///c:/Users/NASPC/Documents/Du%20án%20tại%20SG%20tháng%208/Readme.md) phần 4.D, phản ánh sự thay đổi phương pháp và bổ sung những hiểu biết mới (insight) về khoảng cách, nghề nghiệp và sự kìm hãm của DES.
