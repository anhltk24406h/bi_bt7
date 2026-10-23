# Kịch bản thuyết trình 5–7 phút

Điền tên nhóm, lớp và phân công người nói trước khi nộp. Mở PDF và trình bày theo trang, không cần slide riêng.

## 0:00–0:40 · Câu hỏi và thông điệp (trang 1)
Nhóm em phân tích dữ liệu bán lẻ trực tuyến để trả lời: doanh số tập trung ở đâu, khách hàng nào đóng góp nhiều và giá trị hủy cần được kiểm tra thế nào?
Ba điểm chính: UK chiếm 84.61% doanh số; xấp xỉ 10% khách chi tiêu cao nhất đóng góp 61.38% doanh số có định danh; giá trị hủy bằng 8.41% doanh số bán.

## 0:40–1:30 · Dữ liệu và làm sạch (trang 2–3)
Nguồn UCI Online Retail có 541,909 dòng và 8 cột. Mỗi dòng là một dòng hàng, nên phải gộp InvoiceNo để tính đơn.
Nhóm tách bán, hủy theo mã C và dữ liệu bất thường. Giữ các giao dịch thiếu mã khách trong doanh số nhưng không đưa vào phân tích khách hàng.
Dòng trùng được giữ vì không có mã dòng hàng xác định lỗi; nếu loại thì doanh số thay đổi 24,573.74 GBP. Ngoại lệ chỉ được xử lý cách hiển thị, không xóa tùy ý.

## 1:30–2:20 · Xu hướng và sản phẩm (trang 4–5)
Trong các tháng đầy đủ, 2011-11 đạt doanh số cao nhất: 1,509,496.33 GBP. Tháng 12/2011 chỉ có đến ngày 09, không thể dùng để kết luận suy giảm.
Sản phẩm dẫn đầu là REGENCY CAKESTAND 3 TIER, đạt 174,484.74 GBP. Nhóm dùng biểu đồ thanh để so sánh sản phẩm và biểu đồ đường cho thời gian.
Đề xuất là kiểm tra năng lực đáp ứng, chưa suy diễn nguyên nhân tăng do quảng cáo hay khẳng định tính mùa vụ từ một năm dữ liệu.

## 2:20–3:10 · Thị trường và hủy (trang 6)
Doanh số bán hợp lệ là 10,666,684.54 GBP; giá trị hủy là 896,812.49 GBP. UK đóng góp phần lớn doanh số nên cần ưu tiên kiểm tra theo tác động tuyệt đối.
Thanh chồng dùng mẫu số bán cộng trị tuyệt đối hủy để thể hiện cơ cấu; chỉ số hủy trên bán trong diễn giải có mẫu số khác.
Đây không phải tỷ lệ số đơn bị hủy, cũng chưa phải tỷ lệ trả hàng: cần ghép hóa đơn hủy với đơn gốc để xác minh.
Hai chứng từ hủy lớn nhất chiếm 27.39% tổng giá trị hủy, nên kiểm tra các chứng từ này trước. Mã 23843 xuất hiện trong cả dòng bán lớn 168,469.60 GBP và chứng từ hủy cùng giá trị; không nên xem thứ hạng doanh số trước hủy là bằng chứng đủ để tăng nhập hàng.

## 3:10–4:10 · Phân phối đơn hàng (trang 7–8)
Giá trị đơn trung vị là 303.84 GBP, trung bình là 534.40 GBP. Đuôi phải dài khiến vài đơn lớn kéo trung bình lên.
Histogram cho biết phần tập trung; boxplot so sánh trung vị và phân tán giữa thị trường. Histogram chỉ hiện đến P99; boxplot ẩn điểm ngoài râu; KPI vẫn giữ toàn bộ giao dịch hợp lệ.
Vì khác biệt cơ cấu đơn, nên xem xét mục tiêu theo thị trường thay vì chỉ đặt một mức trung bình chung.

## 4:10–5:10 · Khách hàng (trang 9)
Có 4,338 khách được định danh, đóng góp 83.54% doanh số. Nhóm top xấp xỉ 10% đóng góp 61.38% doanh số trong tập này.
Scatter sử dụng trục log để giữ cả khách chi tiêu lớn và nhỏ. Tương quan Spearman là 0.807, nhưng tổng chi tiêu vốn được cộng qua các đơn nên không thể diễn giải nhân quả.
Đề xuất ưu tiên chăm sóc khách đóng góp cao, đồng thời theo dõi sự phụ thuộc vào nhóm này.

## 5:10–6:00 · Đề xuất và giới hạn (trang 10)
Nhóm đề xuất kiểm tra chứng từ hủy lớn, chăm sóc khách đóng góp cao, rà soát hàng hóa trước cao điểm và xem xét khác biệt thị trường.
Dữ liệu là lịch sử 2010–2011, không có giá vốn, quảng cáo hay lý do hủy; vì vậy không tính lợi nhuận hoặc khẳng định nguyên nhân. Các đề xuất cần được kiểm chứng trên dữ liệu cập nhật.
Quy trình Python có thể chạy lại và đối soát tổng theo đơn, tháng, quốc gia và khách hàng.

## Câu hỏi thường gặp

**1. Vì sao chọn bộ dữ liệu này?** Có nguồn thực tế rõ ràng, vượt 10.000 dòng, đủ 8 biến với số, danh mục và thời gian; có câu hỏi kinh doanh cụ thể.

**2. UCI ghi 6 features thì có đủ biến không?** Tệp có 8 cột: UCI tách hai cột ID khỏi sáu features. Bài mô tả đúng cả hai cách đếm.

**3. Vì sao không bỏ CustomerID thiếu?** Các dòng còn đủ giá và số lượng vẫn cung cấp doanh số hợp lệ. Bỏ chúng làm giảm doanh số và thay đổi cơ cấu thị trường. Chỉ loại khi phân tích khách hàng.

**4. Tại sao không xóa mọi dòng trùng?** Không có mã dòng hàng độc lập để chứng minh nhập lặp. Nhóm giữ trong kết quả chính và báo cáo độ nhạy khi bỏ.

**5. Số lượng âm có luôn là trả hàng?** Không. Phải đối chiếu mã C. Dòng âm không mã C được lưu vào nhóm khác, không tự gán là hủy.

**6. Bán trừ hủy có phải lợi nhuận không?** Không có giá vốn, chi phí hoặc đối soát đơn gốc; đây chỉ là chênh lệch giá trị trong kỳ. Ngay cả doanh thu thuần kế toán cũng cần kiểm tra thêm.

**7. Biểu đồ đã bỏ outlier chưa?** Không xóa khỏi tập hợp lệ. Chỉ giới hạn hình histogram ở P99, ẩn điểm ngoài râu boxplot, và dùng log cho scatter. Tất cả được chú thích.

**8. Tại sao Spearman thay vì chỉ Pearson?** Dữ liệu lệch mạnh và có đuôi dài; Spearman mô tả liên hệ thứ hạng. Không chứng minh quan hệ nhân quả.

**9. Form follows Function thể hiện ở đâu?** Đường: xu hướng; thanh: so sánh; thanh chồng: cơ cấu; histogram/boxplot: phân phối; scatter: tương quan.

**10. Data-ink ratio được áp dụng thế nào?** Không 3D, nền trắng, ít đường lưới, bỏ khung dư thừa và giới hạn màu nhấn.

**11. Có thể nói do quảng cáo nên doanh số tăng không?** Chưa thể: không có dữ liệu chiến dịch. Chỉ nêu giả thuyết cần kiểm chứng.

**12. Top khách có đại diện cho mọi khách không?** Không. Tỷ trọng top khách dùng mẫu số doanh số của khách có mã; phần thiếu mã không được phân bổ giả.

**13. Tại sao mã phí không có trong top sản phẩm?** Top sản phẩm chỉ dùng StockCode bắt đầu bằng 5 chữ số. Các mã điều chỉnh/phí vẫn có trong tổng doanh số, và quy tắc này được ghi rõ là cần đối chiếu danh mục chính thức.

**14. Đề xuất có cam kết hiệu quả không?** Không. Đây là hành động ưu tiên kiểm tra và giả thuyết vận hành; cần thử nghiệm hoặc dữ liệu bổ sung để đo hiệu quả.
