# Bài tập Visual Analytics — UCI Online Retail

**Câu hỏi:** Doanh thu tập trung ở đâu, khách hàng nào đóng góp nhiều và giao dịch hủy ảnh hưởng thế nào?

## Mở ngay để nộp bài

- `outputs/bao_cao_visual_analytics.pdf`: báo cáo tiếng Việt 10 trang, đủ 6 loại biểu đồ.
- `outputs/bao_cao_visual_analytics.docx`: bản Word với văn bản và bảng có thể chỉnh sửa; biểu đồ nhúng dạng ảnh.
- `visual_analytics.ipynb`: notebook giải thích từng bước, có kết quả đã chạy.
- `outputs/bao_cao_visual_analytics.md`: nội dung báo cáo có thể sửa.
- `outputs/thuyet_trinh.md`: kịch bản khoảng 6 phút và câu hỏi thường gặp.
- `outputs/figures/`: 6 ảnh PNG độ phân giải cao.
- `outputs/tables/`: bảng kiểm tra chất lượng, nhật ký xử lý, số liệu và chỉ số.
- `docs/phuong_phap.md`: quy tắc xử lý và công thức để đọc hiểu mã.

**Trước khi nộp:** điền tên, lớp, giảng viên trong `src/deliverables.py` (tìm `Sinh viên / Nhóm`), rồi chạy lại `python run.py`. Điền thông tin tương ứng ở ô đầu notebook. Đọc PDF và kịch bản để có thể tự giải thích các quyết định xử lý dữ liệu.

## Chạy lại trên máy hiện tại

Trong PowerShell tại thư mục dự án:

```powershell
python run.py
```

Các thư viện bổ sung đã được đặt trong `.packages/`, không sửa bộ thư viện Python toàn máy. `run.py` tự tìm thư mục này. Dữ liệu đã tải nên chạy lại không cần mạng. Script đọc Excel, tạo bảng/ảnh/PDF và tạo lại notebook nguồn; **script sẽ ghi đè notebook, xóa kết quả chạy và các sửa đổi trực tiếp trong notebook**. Nếu đã sửa notebook, hãy lưu bản sao trước. Sau khi chạy script, chạy lệnh dưới để thực thi notebook và bổ sung kết quả:

```powershell
python execute_notebook.py
python verify_outputs.py
```

## Cài trên máy mới

Cần Python 3.12 (khuyến nghị) và mạng cho lần tải/cài đầu tiên. PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
.\.venv\Scripts\python.exe execute_notebook.py
.\.venv\Scripts\python.exe verify_outputs.py
```

Mở notebook bằng VS Code với phần mở rộng Python và Jupyter, chọn kernel `.venv`, rồi **Run All**. Notebook tự tìm thư viện cục bộ nếu `.packages/` tồn tại. Không cần cài ứng dụng BI. PDF dùng font Arial trên Windows hoặc DejaVu Sans trên Linux.

## Cách sửa báo cáo

Bạn có thể mở trực tiếp `outputs/bao_cao_visual_analytics.docx` bằng Word để chỉnh sửa. Muốn tạo lại Word từ bản Markdown hiện tại, chạy `python export_docx.py`; lệnh này sẽ ghi đè file Word.

PDF được tạo từ `src/deliverables.py`, dựa trên số liệu phân tích. Sửa văn bản trong hàm `build_report`, sau đó chạy lại `run.py` và thực thi notebook. Bản `.md` có thể sửa tự do để dùng với Word hoặc trình soạn thảo Markdown, nhưng **sửa `.md` không tự cập nhật PDF**; chạy lại script sẽ ghi đè bản `.md`.

## Dữ liệu và cấu trúc

Nguồn: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online-retail). Chen, D. (2015), DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0. Bộ dữ liệu có 541.909 **dòng hàng**, 8 cột; trang UCI đếm 6 features và 2 ID. Ngày quan sát: 01/12/2010–09/12/2011. Metadata và SHA-256 của Excel nằm trong `data/raw/source.json`.

```text
data/raw/                 Excel và ZIP gốc, metadata nguồn
data/processed/           sales.csv, cancellations.csv, other.csv
src/analysis.py           Đọc, phân nhóm, tổng hợp, vẽ và đối soát
src/deliverables.py       Tạo PDF, Markdown, notebook và kịch bản
outputs/figures/          Sáu loại biểu đồ
outputs/tables/           Bảng số liệu và metrics.json
outputs/validation.txt    Kết quả kiểm tra nghiệp vụ
outputs/verification.json Kết quả kiểm tra PDF và notebook
```

## Lưu ý khi diễn giải

- Giá trị tiền là GBP; `1,234.56` nghĩa là một nghìn hai trăm ba mươi tư phẩy năm sáu.
- Doanh số bán **chưa trừ hủy**; không có giá vốn nên không tính lợi nhuận.
- Thiếu mã khách vẫn được tính doanh số; tỷ trọng top khách chỉ dùng tập khách có mã.
- Giữ dòng trùng và ngoại lệ trong số liệu chính, báo cáo độ nhạy và giới hạn hiển thị riêng.
- Hủy được ghi theo ngày chứng từ C; chưa đối soát với đơn bán gốc và có thể bao gồm điều chỉnh.
- Tháng 12/2011 chỉ quan sát đến ngày 09; không so như tháng đầy đủ.
- Kết quả là mô tả lịch sử, không khẳng định nguyên nhân hay phản ánh thị trường hiện tại.

## Đóng gói

Thư mục `submission/` chứa bản nộp: PDF, notebook đã chạy, 6 hình, bảng tổng hợp, mã nguồn, requirements, hướng dẫn, kịch bản và Excel gốc để chạy lại không cần tải dữ liệu. ZIP nằm tại `bai_nop_visual_analytics.zip`. Không đóng gói `.packages/`, `.venv/` hoặc các CSV dữ liệu xử lý lớn; chạy lại sẽ tái tạo CSV. Máy mới vẫn cần mạng để cài thư viện. Tạo lại gói sau khi sửa bằng `python package_submission.py`.
