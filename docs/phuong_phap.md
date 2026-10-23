# Phương pháp và cách đọc mã

## 1. Đơn vị quan sát

Một dòng Excel là một dòng hàng. Một `InvoiceNo` có thể có nhiều `StockCode`. Vì vậy, đếm số dòng không cho biết số đơn. Dùng `groupby('InvoiceNo')` để cộng tiền và `nunique()` để đếm đơn.

Tệp có 8 cột: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country. Định lượng: Quantity, UnitPrice. Định tính: mã sản phẩm, quốc gia, mô tả; thời gian: InvoiceDate. Các mã không được tính như biến số liên tục.

## 2. Quy tắc phân nhóm

Đọc Excel bằng OpenPyXL. Chuẩn hóa InvoiceNo/StockCode thành chuỗi, chuyển ngày về datetime và số lượng/đơn giá về số. Giá trị không chuyển được trở thành thiếu. Không sửa giá trị trong file gốc.

Điều kiện nền: có InvoiceNo, StockCode, InvoiceDate, Country; Quantity và UnitPrice hữu hạn, UnitPrice > 0.

| Nhóm | Điều kiện thêm | Giá trị |
|---|---|---|
| sale | InvoiceNo không bắt đầu C, Quantity > 0 | Quantity × UnitPrice |
| cancellation | InvoiceNo bắt đầu C, Quantity < 0 | -(Quantity × UnitPrice) |
| other | Không thuộc hai nhóm trên | Không đưa vào KPI bán/hủy |

Ba nhóm loại trừ nhau và tổng số dòng bằng dữ liệu gốc. Các cờ chất lượng như thiếu, trùng, giá âm có thể chồng lấn; không cộng tổng các cờ để suy ra số dòng bị loại.

`CustomerID` thiếu: giữ trong doanh số, bỏ khỏi phân tích khách. `Description` thiếu: không tự bịa tên; vẫn giữ nếu dữ liệu giao dịch hợp lệ. Tên đại diện sản phẩm là mô tả xuất hiện nhiều nhất cho mỗi StockCode.

## 3. Dòng trùng và ngoại lệ

`raw.duplicated(keep='first')` tìm các dòng trùng toàn bộ 8 cột sau lần xuất hiện đầu. Không có mã dòng giao dịch để kết luận lỗi: giữ trong kết quả chính. Tổng tiền của các dòng bị gắn cờ cho biết tác động nếu bỏ chúng; báo cáo cả thay đổi doanh số và giá trị hủy.

Không xóa giao dịch chỉ vì số tiền lớn. Histogram hiện tối đa P99 của giá trị đơn. Boxplot ẩn dấu điểm ngoài râu 1,5 IQR; phân vị vẫn tính toàn bộ tập mỗi nước. Scatter hiện tất cả khách và dùng log hai trục. Mọi giới hạn đều có chú thích.

## 4. Công thức và mẫu số

- Doanh số bán: tổng LineValue ở nhóm sale.
- Giá trị hủy: tổng -LineValue ở nhóm cancellation.
- Chênh lệch trong kỳ: bán − giá trị hủy; không gọi là lợi nhuận/doanh thu thuần đã đối soát.
- Số đơn bán: số InvoiceNo khác nhau trong nhóm sale. Nếu một hóa đơn có dòng không hợp lệ, giá trị đơn chỉ gồm các dòng bán hợp lệ.
- Giá trị đơn: tổng LineValue theo InvoiceNo. Kiểm tra mỗi hóa đơn chỉ có một Country và tối đa một CustomerID được biết.
- Doanh số theo tháng: cộng theo InvoiceDate của dòng; hủy cộng theo ngày chứng từ hủy, không chuyển về ngày đơn gốc.
- |Hủy|/bán: giá trị hủy chia doanh số bán; không phải tỷ lệ số đơn.
- Mức tập trung hủy: gộp giá trị hủy theo InvoiceNo, lấy hai chứng từ lớn nhất rồi chia cho tổng giá trị hủy. Bảng `cancellation_invoices.csv` và `large_cancellation_lines.csv` lưu bằng chứng.
- Cơ cấu stacked bar: bán/(bán + |hủy|) và |hủy|/(bán + |hủy|). Mẫu số này khác |hủy|/bán; hình thể hiện cơ cấu hoạt động ghi nhận, không phải các phần của doanh thu thuần.
- Chi tiêu khách: cộng doanh số bán theo CustomerID không thiếu, chưa trừ hủy.
- Nhóm top 10%: sắp khách theo chi tiêu giảm dần, lấy `ceil(0.1 × số khách)`. Chia chi tiêu nhóm này cho doanh số của **khách được định danh**. Màu đỏ scatter dùng ngưỡng P90 nên có thể bao gồm các đồng hạng.
- Spearman: tương quan Pearson của thứ hạng số đơn và thứ hạng chi tiêu; không cần giả định phân phối chuẩn. Tính bằng `.rank().corr(...)` để không cần SciPy.

## 5. Thời gian và danh mục

Một tháng được gắn `Partial` nếu ngày đầu tháng sớm hơn ngày bắt đầu quan sát hoặc ngày cuối tháng muộn hơn ngày kết thúc quan sát. Chỉ so các tháng đầy đủ; chưa đủ dữ liệu nhiều năm để xác nhận mùa vụ.

Xếp hạng sản phẩm gộp theo StockCode và chỉ giữ mã bắt đầu bằng 5 chữ số. Các mã như POST, DOT, M không vào top sản phẩm nhưng vẫn tham gia tổng doanh số nếu đạt quy tắc bán. Đây là quy tắc cấu trúc mã, không phải danh mục được doanh nghiệp xác nhận. Số tiền các mã còn lại được ghi trong metrics.json.

## 6. Thiết kế và hạn chế

Đúng sáu loại: line, bar, stacked bar, histogram, boxplot, scatter. Chọn loại theo mục đích; nền trắng, lưới nhẹ, ít màu, không 3D. Đỏ dùng để hướng chú ý vào đỉnh sản phẩm, hủy, trung vị hoặc khách chi tiêu lớn, tùy ngữ cảnh được chú thích.

Không ghép chính xác hóa đơn hủy với đơn bán do thiếu tham chiếu đơn gốc; không diễn giải mọi C là một khách trả hàng. Không có dữ liệu về chiến dịch, giá vốn, lý do hủy, tồn kho hay giao vận để khẳng định nguyên nhân hoặc lợi nhuận. Khác biệt giữa nước có thể do cơ cấu khách/sản phẩm. Dữ liệu lịch sử không đại diện thị trường 2026.

## 7. Kiểm chứng

Kiểm tra phân nhóm không mất dòng; doanh số theo đơn, tháng, nước phải bằng tổng bán; tổng chi tiêu khách bằng phần bán có CustomerID. Giá trị hủy theo tháng/nước bằng tổng hủy. Kiểm tra tháng cuối chưa đầy đủ và có đủ sáu ảnh. Notebook phải thực thi mọi ô không có lỗi. PDF phải có 10 trang, trích xuất được tiếng Việt và có hình trên sáu trang phân tích.
