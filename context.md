Mục tiêu: Ứng dụng quy trình phân tích trực quan (Visual Analytics) vào một tập dữ liệu thực tế để phát hiện insight, thiết kế biểu đồ chuyên nghiệp và xây dựng một câu chuyện dữ liệu có sức thuyết phục.
Nguồn dữ liệu: Nhóm tự tìm kiếm một tập dữ liệu thực tế (khuyến nghị từ Kaggle, World Bank, Google Dataset Search hoặc UCI Machine Learning Repository). Tập dữ liệu cần có tối thiểu 10.000 dòng thô và ít nhất 5-7 biến số (bao gồm cả biến định lượng và định tính/chuỗi thời gian).
Công cụ thực hiện: Tự do lựa chọn nền tảng thế mạnh của nhóm: Ngôn ngữ lập trình (Python với Pandas, Plotly/Matplotlib, R) hoặc Phần mềm BI (Tableau, Power BI).
Sản phẩm trực quan: Xây dựng một Bảng điều khiển (Dashboard) hoặc một chuỗi biểu đồ logic (tối thiểu 6 biểu đồ khác loại nhau). Bắt buộc áp dụng nguyên lý "Form follows Function" (chọn đúng biểu đồ theo mục đích: So sánh, Thành phần, Phân phối, Tương quan) và nguyên tắc "Data-ink ratio".
Báo cáo phân tích: Nộp file pdf trình bày theo cấu trúc kể chuyện dữ liệu.
HƯỚNG DẪN LÀM BÀI
1. Tìm & Hiểu dữ liệu
Đừng chọn dữ liệu chỉ vì nó "trông có vẻ dễ". Hãy chọn một tập dữ liệu có vấn đề (problem) để giải quyết.
Yêu cầu bắt buộc: Tập dữ liệu phải có tối thiểu 10.000 dòng thô và ít nhất 5-7 biến số (phải có sự pha trộn giữa biến định lượng như doanh thu, lợi nhuận, số lượng và biến định tính/thời gian như danh mục, khu vực, ngày tháng).
Nguồn đề xuất: Kaggle, World Bank, Google Dataset Search, hoặc UCI Machine Learning Repository.
Mẹo: Hãy chọn các chủ đề như E-commerce (Bán lẻ), Finance (Tài chính - Ngân hàng), Supply Chain (Chuỗi cung ứng) hoặc Healthcare (Y tế). Đây là những lĩnh vực mà Data Storytelling có đất diễn mạnh mẽ nhất.
2. Công cụ thực hiện
Các bạn tự do lựa chọn công cụ phù hợp với nhóm mình:
Nhóm thiên về Lập trình & Xử lý linh hoạt: Python (với Pandas để xử lý data, Plotly/Matplotlib/Seaborn để vẽ biểu đồ) hoặc R.
Nhóm thiên về Tốc độ xây dựng & Tương tác UI/UX: Các phần mềm BI chuyên dụng như Tableau, Power BI.
Lưu ý: Công cụ chỉ là phương tiện. Một biểu đồ xuất sắc vẽ bằng Python sẽ luôn được đánh giá cao hơn một Dashboard lộn xộn, rối mắt trên Power BI.
3. Thiết kế Trực quan (Visual Design & Khai phá Insight)
Đây là phần cốt lõi của đồ án. Các bạn cần xây dựng một Dashboard hoặc một chuỗi biểu đồ logic với tối thiểu 6 loại biểu đồ khác nhau.
Bắt buộc tuân thủ 2 nguyên tắc thiết kế phân tích:
3.1. Nguyên lý "Form follows Function" (Chọn biểu đồ theo mục đích):
So sánh: Dùng Bar chart (Biểu đồ cột/Thanh), Bullet chart. Tránh dùng biểu đồ tròn để so sánh các giá trị gần nhau.
Thành phần: Dùng Stacked Bar Chart, Treemap, hoặc Pie/Donut Chart (chỉ khi có ít hơn 4-5 thành phần).
Phân phối: Dùng Histogram, Boxplot để xem dữ liệu tập trung ở đâu, có giá trị ngoại lai không.
Tương quan: Dùng Scatter Plot để xem hai biến có quan hệ đồng biến/nghịch biến không.
Xu hướng: Dùng Line chart đối với dữ liệu chuỗi thời gian.
3.2. Nguyên tắc "Data-ink Ratio" (Tối ưu hóa tỷ lệ mực in - Edward Tufte):
Loại bỏ mọi yếu tố trang trí rườm rà không mang lại thông tin, ví dụ: Bỏ lưới nền quá đậm, bỏ viền biểu đồ, bỏ đổ bóng, hiệu ứng 3D.
Làm nổi bật dữ liệu quan trọng bằng màu sắc tương phản. 
Nếu tất cả đều nổi bật, nghĩa là không có gì nổi bật.
4. Cấu trúc Báo cáo Kể chuyện Dữ liệu (Data Storytelling PDF)
Báo cáo không phải là nơi các bạn liệt kê "Tôi đã vẽ 6 biểu đồ này". Báo cáo là nơi các bạn kể một câu chuyện kinh doanh có mở bài, diễn biến và kết luận. File PDF nộp lại cần tuân thủ cấu trúc sau:
Tóm tắt Thực thi: 1 đoạn ngắn gọn trình bày vấn đề của tập dữ liệu và 2-3 insight quan trọng nhất tìm được.
Bối cảnh Dữ liệu: Giới thiệu tập dữ liệu, nguồn gốc, và các bước tiền xử lý (làm sạch dữ liệu thiếu, xử lý outliers).
Phân tích: Trình bày chuỗi 6+ biểu đồ theo một luồng logic. Ví dụ: Bắt đầu từ bức tranh tổng quan (doanh thu tổng) -> Đi sâu vào vấn đề (sụt giảm ở một khu vực) -> Phân tích nguyên nhân (thay đổi giá, lỗi vận chuyển).
Dưới mỗi biểu đồ, không mô tả lại biểu đồ (VD: Đừng viết "Biểu đồ này cho thấy đường màu xanh đi lên").
Thay vào đó, hãy diễn dịch nó (VD: "Doanh số tháng 4 tăng đột biến 15% là do chiến dịch giảm giá mùa hè được tung ra sớm tại khu vực miền Nam": Biểu hiện - Số liệu chứng minh - Nguyên nhân).
Hành động & Đề xuất: Dựa trên insight tìm được, đề xuất giải pháp gì cho doanh nghiệp? (Ví dụ: Dừng bán sản phẩm lỗi, tập trung marketing vào nhóm khách hàng X).