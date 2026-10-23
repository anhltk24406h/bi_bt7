"""Tạo báo cáo PDF, bản Markdown, notebook và kịch bản trình bày từ cùng số liệu."""
from pathlib import Path
from html import escape
import json
import math
import pandas as pd


def money(v):
    return f'{v:,.2f} GBP'


def pct(v):
    return f'{v:.2f}%'


def chart_stories(t):
    s = t['stats']
    full = t['monthly'].loc[~t['monthly'].Partial]
    last_full = full.iloc[-1]
    prior = full.iloc[-2]
    growth = (last_full.Sales / prior.Sales - 1) * 100
    m = t['markets'].head(6)
    highest = m.CancellationToSalesPct.idxmax()
    box_countries = t['markets'].head(5).index
    medians = t['orders'][t['orders'].Country.isin(box_countries)].groupby('Country').OrderValue.median()
    high, low = medians.idxmax(), medians.idxmin()
    return [
        dict(title='01 · Xu hướng: xác định giai đoạn cần ưu tiên', file='01_line_monthly.png',
             purpose='Line chart nối các tháng đầy đủ để thể hiện biến động theo thời gian. Kỳ chưa đủ được đánh dấu riêng.',
             finding=f'Trong các tháng đầy đủ quan sát được, {s["peak_month"]} có doanh số cao nhất: {money(s["peak_sales"])}. '
                     f'Tháng đầy đủ cuối cùng có doanh số {money(last_full.Sales)}, thay đổi {growth:+.2f}% so với tháng đầy đủ trước đó.',
             meaning='Mức tăng gợi ý cần chuẩn bị năng lực phục vụ cho giai đoạn cuối năm, nhưng một năm dữ liệu chưa đủ chứng minh mùa vụ lặp lại. '
                     'Chưa có dữ liệu chiến dịch hoặc tồn kho để kết luận nguyên nhân tăng.',
             action='Ưu tiên kiểm tra kế hoạch hàng hóa và nhân lực trước giai đoạn cao điểm; kiểm chứng bằng dữ liệu nhiều năm. '
                    'Không diễn giải tháng 12/2011 thấp là suy giảm vì chỉ quan sát đến ngày 09.'),
        dict(title='02 · Sản phẩm: chọn nơi ưu tiên nguồn lực', file='02_bar_products.png',
             purpose='Bar chart ngang giúp so sánh và đọc tên sản phẩm dài; trục giá trị bắt đầu từ 0.',
             finding=f'Sản phẩm dẫn đầu là {s["top_product"]} (mã {s["top_product_code"]}), đạt {money(s["top_product_sales"])}. '
                     f'Top 10 mã sản phẩm chiếm {pct(s["top10_product_share_pct"])} tổng doanh số bán hợp lệ.',
             meaning=f'Xếp hạng theo mã, chưa trừ hủy. Mã 23843 có dòng bán 168,469.60 GBP và dòng C581484 hủy cùng giá trị; '
                     'chưa khẳng định ghép đơn chính xác, nhưng đây là tín hiệu cần kiểm tra trước khi xem doanh số gộp là nhu cầu bền vững. '
                     f'Các mã không bắt đầu bằng 5 chữ số, tổng {money(s["nonproduct_sales"])}, vẫn có trong KPI nhưng không vào xếp hạng. '
                     'Quy tắc nhận diện sản phẩm cần đối chiếu danh mục chính thức.',
             action='Rà soát khả năng đáp ứng của nhóm sản phẩm dẫn đầu. Chưa quyết định tăng nhập chỉ từ doanh số: cần bổ sung tồn kho, biên lợi nhuận và giá trị hủy theo sản phẩm.'),
        dict(title='03 · Thị trường: nhìn đồng thời quy mô và giá trị hủy', file='03_stacked_markets.png',
             purpose='Stacked bar 100% so sánh cơ cấu bán và trị tuyệt đối hủy giữa sáu thị trường có doanh số bán lớn nhất.',
             finding=f'United Kingdom đóng góp {pct(s["uk_share_pct"])} doanh số bán. Tổng giá trị hủy là {money(s["cancellation"])}, '
                     f'bằng {pct(s["cancel_to_sales_pct"])} doanh số bán. Trong sáu thị trường lớn, {highest} có |hủy|/bán cao nhất, '
                     f'{pct(m.loc[highest, "CancellationToSalesPct"])}. Hai chứng từ hủy lớn nhất chiếm '
                     f'{pct(s["top2_cancellation_share_pct"])} tổng giá trị hủy ({money(s["top2_cancellation_value"])}).',
             meaning='Nhãn đỏ trên hình dùng |hủy|/(bán + |hủy|), khác chỉ số |hủy|/bán trong phần diễn giải. '
                     'Hai mẫu số được ghi rõ để không nhầm cơ cấu với tỷ lệ hủy trên doanh số. Giao dịch hủy có thể thuộc đơn ngoài kỳ; '
                     'mã C có cả Manual/AMAZONFEE, vì vậy không coi đây là tỷ lệ khách trả hàng hoặc tỷ lệ đơn bị hủy. '
                     'Bảng cancellation_invoices.csv và large_cancellation_lines.csv lưu bằng chứng để đối soát.',
             action='Ưu tiên kiểm tra chứng từ hủy có giá trị lớn ở thị trường đóng góp chính. Muốn tìm nguyên nhân cần ghép chứng từ gốc, lý do hủy và thông tin vận chuyển.'),
        dict(title='04 · Phân phối: vì sao số trung bình dễ gây hiểu lầm?', file='04_hist_orders.png',
             purpose='Histogram thể hiện tần suất theo khoảng giá trị đơn. Mỗi InvoiceNo chỉ đóng góp một quan sát.',
             finding=f'Từ {s["orders"]:,} đơn bán, giá trị trung vị là {money(s["median_order"])} trong khi trung bình là {money(s["mean_order"])}. '
                     f'Đơn lớn nhất đạt {money(s["max_order"])}; phân vị 99 là {money(s["p99_order"])}.',
             meaning='Chênh lệch giữa trung bình và trung vị phản ánh đuôi phải dài: một số đơn lớn kéo trung bình lên. '
                     'Hình chỉ hiển thị các đơn không vượt P99 để đọc phần tập trung; mọi đơn lớn vẫn nằm trong KPI. '
                     'Dữ liệu nguồn có khách bán buôn, nhưng chưa thể xác định từng đơn lớn là bán buôn hay lỗi chỉ từ giá trị.',
             action='Theo dõi đồng thời trung vị, trung bình và đơn giá trị lớn; kiểm tra chứng từ ngoại lệ trước khi dùng chúng để lập mục tiêu giỏ hàng.'),
        dict(title='05 · Khác biệt thị trường: một mục tiêu không phù hợp cho tất cả', file='05_box_markets.png',
             purpose='Boxplot so sánh trung vị và độ phân tán giá trị đơn giữa năm thị trường có doanh số lớn nhất.',
             finding=f'Trong năm thị trường được chọn, trung vị giá trị đơn cao nhất ở {high}: {money(medians[high])}; '
                     f'thấp nhất ở {low}: {money(medians[low])}. Quy mô mẫu từng nước được lưu trong bảng orders.csv.',
             meaning='Hộp thể hiện Q1–Q3, vạch đỏ là trung vị, râu giới hạn theo 1,5 IQR. Điểm ngoài râu được ẩn để hình dễ đọc '
                     'nhưng vẫn tham gia tính phân vị và doanh số. Khác biệt có thể liên quan cơ cấu khách hàng hoặc sản phẩm; '
                     'chưa có kiểm định hay thiết kế nhân quả để khẳng định tác động của quốc gia.',
             action='Thử thiết lập mục tiêu giá trị đơn theo thị trường và kiểm tra cơ cấu khách hàng trước khi áp dụng ưu đãi chung. '
                    'Đối chiếu cả quy mô mẫu và số đơn khi so sánh.'),
        dict(title='06 · Khách hàng: ưu tiên chăm sóc dựa trên mức đóng góp', file='06_scatter_customers.png',
             purpose='Scatter plot thể hiện đồng thời số đơn và tổng chi tiêu. Hai trục log giữ được khách cực lớn mà vẫn đọc được phần còn lại.',
             finding=f'Có {s["customers"]:,} khách được định danh; doanh số của họ chiếm {pct(s["identified_share_pct"])} tổng doanh số. '
                     f'Nhóm {s["top10_customer_n"]:,} khách chi tiêu cao nhất (xấp xỉ 10%) đóng góp {pct(s["top10_customer_share_pct"])} '
                     f'doanh số trong tập khách được định danh. Tương quan Spearman giữa số đơn và chi tiêu là {s["spearman_orders_spending"]:.3f}.',
             meaning='Tổng chi tiêu được cộng từ đơn mua nên quan hệ với số đơn có thành phần cơ học; tương quan không chứng minh tăng tần suất sẽ gây tăng chi tiêu. '
                     'Màu đỏ chỉ nhóm chi tiêu từ P90 trở lên; ranh giới có thể bao gồm đồng hạng. Tỷ trọng top 10% trong lời dẫn dùng số khách làm tròn lên và xếp hạng xác định.',
             action='Ưu tiên chăm sóc khách đóng góp cao và theo dõi mức độ phụ thuộc doanh số vào họ. '
                    'Bổ sung dữ liệu mới nhất, giao dịch hủy và chi phí phục vụ trước khi xác định giá trị vòng đời hoặc chạy chương trình giữ chân.'),
    ]


def build_report(root, data, t, figures):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4

    root = Path(root)
    out = root / 'outputs'
    out.mkdir(exist_ok=True)
    # Windows trong lớp học; có thể chuyển sang DejaVu Sans trên Linux.
    candidates = [(Path('C:/Windows/Fonts/arial.ttf'), Path('C:/Windows/Fonts/arialbd.ttf')),
                  (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))]
    regular, bold = next((a, b) for a, b in candidates if a.exists() and b.exists())
    pdfmetrics.registerFont(TTFont('VN', str(regular)))
    pdfmetrics.registerFont(TTFont('VN-Bold', str(bold)))
    pdfmetrics.registerFontFamily('VN', normal='VN', bold='VN-Bold', italic='VN', boldItalic='VN-Bold')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='VNBody', fontName='VN', fontSize=10.3, leading=15.6,
                              textColor=colors.HexColor('#253B4C'), spaceAfter=10))
    styles.add(ParagraphStyle(name='VNTitle', fontName='VN-Bold', fontSize=23, leading=30,
                              textColor=colors.HexColor('#123D55'), spaceAfter=18))
    styles.add(ParagraphStyle(name='VNHead', fontName='VN-Bold', fontSize=16, leading=21,
                              textColor=colors.HexColor('#176B87'), spaceAfter=15))
    styles.add(ParagraphStyle(name='VNSmall', fontName='VN', fontSize=8, leading=11,
                              textColor=colors.HexColor('#526779'), spaceAfter=7))
    flow, md = [], []

    def p(text, kind='VNBody'):
        flow.append(Paragraph(escape(text).replace('\n', '<br/>'), styles[kind]))
        md.append(text + '\n')

    def heading(text):
        flow.append(Paragraph(escape(text), styles['VNHead']))
        md.append('## ' + text + '\n')

    def newpage():
        flow.append(PageBreak())
        md.append('\n---\n')

    def table(rows, widths):
        cells = [[Paragraph(escape(str(v)), styles['VNSmall']) for v in row] for row in rows]
        tab = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
        tab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E4F0F4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), .6, colors.HexColor('#A8B4BE')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        flow.append(tab)
        flow.append(Spacer(1, 10))
        md.append('\n| ' + ' | '.join(str(v) for v in rows[0]) + ' |\n'
                  + '| ' + ' | '.join('---' for _ in rows[0]) + ' |\n'
                  + '\n'.join('| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows[1:]) + '\n')

    s = t['stats']
    flow.append(Spacer(1, 25))
    p('VISUAL ANALYTICS · BÀI TẬP TRÊN LỚP', 'VNSmall')
    p('Doanh thu tập trung ở đâu?', 'VNTitle')
    p('Khách hàng, sản phẩm và giao dịch hủy trong UCI Online Retail', 'VNHead')
    p('Sinh viên / Nhóm: ........................................\nLớp: ........................................\nGiảng viên: ........................................')
    p('Ngày hoàn thiện: 23/10/2026 · Công cụ: Python, Pandas, Matplotlib', 'VNSmall')
    heading('Tóm tắt điều hành')
    p(f'Bài phân tích xem xét {s["raw_rows"]:,} dòng hàng thực tế để xác định nơi tập trung doanh số và những điểm cần kiểm tra về giá trị hủy. '
      f'Doanh số bán hợp lệ là {money(s["sales"])}; United Kingdom đóng góp {pct(s["uk_share_pct"])}. '
      f'Trong tập khách được định danh, nhóm xấp xỉ 10% khách chi tiêu cao nhất đóng góp {pct(s["top10_customer_share_pct"])} doanh số. '
      f'Giá trị hủy bằng {pct(s["cancel_to_sales_pct"])} doanh số bán; riêng hai chứng từ lớn nhất chiếm {pct(s["top2_cancellation_share_pct"])} giá trị hủy. '
      'Cần rà soát chứng từ thay vì mặc định coi toàn bộ là hàng trả lại.')
    p('Thông điệp: ưu tiên thị trường và khách hàng đóng góp lớn, đồng thời kiểm tra chứng từ hủy và đơn ngoại lệ trước khi ra quyết định. '
      'Đây là phân tích lịch sử mô tả, không phải dự báo hay kết luận nhân quả.')
    p('Lộ trình đọc: bối cảnh (trang 2) → xử lý dữ liệu (trang 3) → sáu góc nhìn (trang 4–9) → hành động (trang 10).', 'VNSmall')

    newpage()
    heading('Bối cảnh · Dữ liệu và câu hỏi kinh doanh')
    p('Đối tượng sử dụng: người phụ trách bán hàng và chăm sóc khách hàng của nhà bán lẻ trực tuyến. '
      'Câu hỏi trọng tâm: doanh số tập trung ở thị trường/sản phẩm nào, giá trị đơn phân bố ra sao và nhóm khách nào cần ưu tiên?')
    p('UCI Online Retail ghi nhận giao dịch của một doanh nghiệp bán lẻ không có cửa hàng tại Anh, chủ yếu bán quà tặng; có nhiều khách bán buôn. '
      f'Khoảng quan sát thực tế: {s["start"]} đến {s["end"]}. Mỗi dòng là dòng hàng trong hóa đơn, không phải một đơn độc lập.')
    table([
        ['Biến', 'Ý nghĩa và vai trò'],
        ['InvoiceNo / StockCode', 'Mã hóa đơn / mã sản phẩm; biến định danh. Tiền tố C chỉ hóa đơn hủy.'],
        ['Description / Country', 'Mô tả sản phẩm / quốc gia khách hàng; biến định tính.'],
        ['Quantity / UnitPrice', 'Số lượng / đơn giá theo GBP; biến định lượng.'],
        ['InvoiceDate / CustomerID', 'Thời điểm hóa đơn / mã khách hàng; thời gian và định danh.'],
    ], [140, 365])
    p('Dữ liệu có 541.909 dòng và 8 cột, vượt yêu cầu đề bài. Trang UCI ghi 6 features vì hai cột mã được phân vai ID; tệp gốc có đủ 8 biến.', 'VNSmall')
    heading('Định nghĩa chỉ số')
    p('Giá trị dòng = Quantity × UnitPrice. Doanh số bán = tổng giá trị các dòng bán hợp lệ, chưa trừ hủy. '
      'Giá trị hủy = tổng trị tuyệt đối các dòng mã C, số lượng âm và đơn giá dương. '
      'Đơn bán = số InvoiceNo khác nhau trong tập bán hợp lệ. Chi tiêu khách = tổng doanh số bán theo CustomerID có dữ liệu.')
    p('Nguồn: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5BW33. '
      'Giấy phép CC BY 4.0. Trang dữ liệu: https://archive.ics.uci.edu/dataset/352/online-retail. '
      'Tệp nguồn, ngày tải và SHA-256 được lưu trong data/raw/source.json.', 'VNSmall')

    newpage()
    heading('Tiền xử lý · Minh bạch trước khi diễn giải')
    table([['Bước / nhóm', 'Số dòng'], *[[r.Buoc, f'{r.So_dong:,}'] for r in data['audit'].itertuples()]], [365, 140])
    q = data['quality'].set_index('Cot')
    p(f'CustomerID thiếu {int(q.loc["CustomerID", "So_thieu"]):,} dòng; Description thiếu {int(q.loc["Description", "So_thieu"]):,} dòng. '
      'Không điền mã khách hàng giả. Thiếu mô tả không làm mất giá trị dòng nếu mã và số liệu vẫn hợp lệ. '
      'Bảng quality.csv ghi kiểu dữ liệu, tỷ lệ thiếu và số giá trị khác nhau cho mọi cột.')
    p(f'Có {s["quantity_negative"]:,} dòng số lượng âm; trong đó {s["negative_quantity_without_C"]:,} dòng không có mã C. '
      f'Đơn giá bằng 0: {s["price_zero"]:,} dòng; âm: {s["price_negative"]:,} dòng. '
      'Các dòng không đạt quy tắc được lưu vào other.csv; không chuyển tất cả số lượng âm thành hủy.')
    p(f'Giữ {s["duplicates"]:,} dòng trùng hoàn toàn sau lần xuất hiện đầu vì không có mã dòng hàng để xác nhận lỗi. '
      f'Nếu loại chúng, doanh số giảm {money(s["duplicate_sale_value"])}, tương đương {pct(s["duplicate_sale_value"]/s["sales"]*100)}, '
      f'và giá trị hủy giảm {money(s["duplicate_cancel_value"])}. Đây là phân tích độ nhạy, không phải số liệu chính.')
    p('Ngoại lệ lớn không bị xóa. Histogram giới hạn hiển thị ở P99; boxplot ẩn điểm ngoài râu; scatter dùng thang log. '
      'KPI vẫn tính trên toàn bộ dòng hợp lệ. Tháng 12/2011 chưa đầy đủ được tách khỏi đánh giá đỉnh theo tháng đầy đủ.')
    p(f'Chênh lệch bán trừ |hủy| trong kỳ: {money(s["period_balance"])}. Chỉ số này không phải lợi nhuận và không phải doanh thu thuần đã đối soát '
      'vì chưa ghép chứng từ hủy với đơn gốc; có thể có hóa đơn hủy thuộc ngoài kỳ.', 'VNSmall')

    stories = chart_stories(t)
    for st in stories:
        newpage()
        heading(st['title'])
        p(st['purpose'], 'VNSmall')
        image_path = root / 'outputs/figures' / st['file']
        from PIL import Image as PILImage
        with PILImage.open(image_path) as im:
            w, h = im.size
        flow.append(Image(str(image_path), width=505, height=505*h/w))
        md.append(f'![{st["title"]}](figures/{st["file"]})\n')
        p('Phát hiện — ' + st['finding'])
        p('Diễn giải — ' + st['meaning'])
        p('Hành động — ' + st['action'])

    newpage()
    heading('Hành động · Từ bằng chứng đến việc cần làm')
    table([
        ['Ưu tiên', 'Đề xuất / Cách kiểm chứng'],
        ['1. Kiểm tra giá trị hủy', 'Đối soát chứng từ hủy lớn, tách phí/điều chỉnh với hàng trả. Theo dõi |hủy|/bán và số chứng từ đã xác minh.'],
        ['2. Chăm sóc khách đóng góp cao', 'Lập danh sách top chi tiêu trong tập có mã; kiểm tra chi tiêu sau hủy và chi phí phục vụ. Theo dõi giữ chân trên dữ liệu cập nhật.'],
        ['3. Chuẩn bị giai đoạn cao điểm', 'Rà soát hàng hóa dẫn đầu và năng lực phục vụ. Bổ sung dữ liệu nhiều năm trước khi coi mức tăng cuối năm là mùa vụ.'],
        ['4. Điều chỉnh theo thị trường', 'Thử mục tiêu giá trị đơn phù hợp từng nước; đánh giá theo trung vị, quy mô mẫu và cơ cấu khách hàng.'],
    ], [145, 360])
    heading('Giới hạn và điều kiện áp dụng')
    p('Dữ liệu 2010–2011 không phản ánh thị trường hiện tại. Không có giá vốn, ngân sách quảng cáo, tồn kho, lý do hủy hay thông tin giao hàng. '
      'Không thể tính lợi nhuận, xác định tác động quảng cáo hoặc kết luận nguyên nhân hủy. '
      'Phân tích khách hàng chỉ đại diện cho phần có CustomerID; không ngoại suy tỷ trọng top khách cho phần không định danh.')
    p('Số liệu hủy chưa ghép với đơn gốc; dòng trùng được giữ và có phân tích độ nhạy. Đơn có một số dòng không hợp lệ chỉ được tính theo các dòng bán hợp lệ còn lại. '
      'Quy tắc nhận diện sản phẩm dựa vào cấu trúc StockCode cần được kiểm chứng với danh mục chính thức.')
    heading('Thiết kế và khả năng tái lập')
    p('Form follows Function: đường cho xu hướng, thanh cho so sánh, thanh chồng cho cơ cấu, histogram và boxplot cho phân phối, scatter cho tương quan. '
      'Data-ink ratio: bỏ hiệu ứng 3D, khung và lưới đậm; dùng xanh làm dữ liệu chính, đỏ nhấn phần cần chú ý. '
      'Mọi chỉ số được tạo từ cùng quy trình Python, có bảng tổng hợp và kiểm tra đối soát.')

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('VN', 8)
        canvas.setFillColor(colors.HexColor('#64748B'))
        canvas.drawString(45, 25, 'UCI ONLINE RETAIL  |  VISUAL ANALYTICS')
        canvas.drawRightString(A4[0] - 45, 25, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(out / 'bao_cao_visual_analytics.pdf'), pagesize=A4,
                            rightMargin=45, leftMargin=45, topMargin=40, bottomMargin=42,
                            title='Doanh thu tập trung ở đâu? | UCI Online Retail', author='Nhóm sinh viên')
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    (out / 'bao_cao_visual_analytics.md').write_text('\n'.join(md), encoding='utf-8')


def build_notebook(root):
    import nbformat as nbf
    root = Path(root)
    md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
    nb = nbf.v4.new_notebook()
    nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                   'language_info': {'name': 'python', 'version': '3.12'}}
    nb.cells = [
        md('# Doanh thu tập trung ở đâu?\n## Visual Analytics với UCI Online Retail\n'
           '**Sinh viên/Nhóm:** … · **Lớp:** …\n\n'
           'Mục tiêu: xác định mức tập trung doanh số theo thời gian, sản phẩm, thị trường và khách hàng; '
           'kiểm tra giá trị hủy. Chạy các ô từ trên xuống bằng **Run All**. '
           'Notebook dùng các hàm trong `src/`; mỗi bước bên dưới cho biết đầu vào, kết quả và cách đọc. '
           'Số liệu tiền dùng GBP; dấu phẩy phân tách hàng nghìn, dấu chấm phân tách thập phân.'),
        md('## 1. Chuẩn bị môi trường\nPandas làm việc với bảng; Matplotlib vẽ biểu đồ. '
           'Ô này tìm thư mục dự án và nạp các hàm xử lý. Cài thư viện theo README trước khi chạy.'),
        code("from pathlib import Path\nimport sys\nROOT = Path.cwd()\nif not (ROOT / 'src').exists():\n    ROOT = ROOT.parent\nassert (ROOT / 'src').exists(), 'Hãy mở notebook trong thư mục dự án.'\nsys.path.insert(0, str(ROOT))\nif (ROOT / '.packages').exists():\n    sys.path.insert(0, str(ROOT / '.packages'))\nimport pandas as pd\nfrom IPython.display import display, Image, Markdown\nfrom src.analysis import load_data, clean_data, summarize, save_tables, make_charts, validate\nfrom src.deliverables import build_report, build_presentation, chart_stories\nprint('Thư mục dự án:', ROOT)"),
        md('## 2. Đọc và hiểu dữ liệu\nNguồn: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online-retail), '
           'Chen (2015), DOI: 10.24432/C5BW33, CC BY 4.0. Có 541.909 dòng hàng và 8 cột; '
           '**một dòng không phải một đơn hàng**. `InvoiceNo` và `StockCode` là ID; '
           '`Quantity`, `UnitPrice` là số; `InvoiceDate` là thời gian; các cột còn lại mô tả sản phẩm, khách và thị trường.'),
        code("raw = load_data(ROOT)\nprint('Kích thước:', raw.shape)\ndisplay(raw.head())\ndisplay(raw.dtypes.to_frame('Kiểu dữ liệu'))"),
        md('## 3. Kiểm tra chất lượng và phân nhóm\n'
           '- Bán: không mã C, số lượng dương, đơn giá dương và đủ mã/ngày/quốc gia.\n'
           '- Hủy: mã C, số lượng âm, đơn giá dương và đủ mã/ngày/quốc gia.\n'
           '- Còn lại: lưu riêng, không cộng vào hai nhóm trên.\n\n'
           'Giữ dòng thiếu CustomerID trong doanh số, chỉ loại khỏi phân tích khách hàng. '
           'Giữ dòng trùng vì không có mã dòng hàng xác nhận lỗi. Các cờ kiểm tra có thể chồng lấn; '
           'chỉ ba nhóm bán/hủy/khác mới tạo thành phép phân hoạch dữ liệu.'),
        code("data = clean_data(raw)\ndisplay(data['quality'])\ndisplay(data['audit'])\ndisplay(pd.Series(data['issues'], name='Kết quả kiểm tra'))"),
        md('## 4. Tính chỉ số ở đúng cấp độ\n'
           '`LineValue = Quantity × UnitPrice`. Dùng `groupby(InvoiceNo)` để cộng giá trị đơn, '
           '`nunique(InvoiceNo)` để đếm số đơn. Khách hàng chỉ lấy CustomerID đã biết. '
           'Doanh số bán và giá trị hủy được báo cáo riêng; chưa ghép chứng từ nên không gọi chênh lệch là lợi nhuận. '
           'Tháng cuối chưa đủ được đánh dấu, không so như một tháng hoàn chỉnh.'),
        code("tables = summarize(data)\nsave_tables(ROOT, data, tables)\ndisplay(pd.Series(tables['stats'], name='Giá trị'))\ndisplay(tables['monthly'])\ndisplay(tables['markets'].head(6))"),
        md('## 5. Phân tích bằng sáu loại biểu đồ\n'
           'Các hình dùng chung màu và đơn vị; ghi rõ phạm vi hiển thị. Histogram chỉ hiện đến P99, '
           'boxplot ẩn điểm ngoài râu, scatter dùng log; **không xóa ngoại lệ khỏi KPI**.'),
        code("figures = make_charts(ROOT, data, tables)\nstories = chart_stories(tables)"),
    ]
    for i in range(6):
        nb.cells.append(md(f'### Góc nhìn {i+1}\nĐọc theo thứ tự: mục đích biểu đồ → bằng chứng → ý nghĩa → hành động.'))
        nb.cells.append(code(f"st = stories[{i}]\ndisplay(Markdown('**' + st['title'] + '**\\n\\n' + st['purpose']))\ndisplay(Image(filename=str(figures[{i}]), width=950))\nfor label, key in [('Phát hiện', 'finding'), ('Diễn giải', 'meaning'), ('Hành động', 'action')]:\n    display(Markdown('**' + label + ':** ' + st[key]))"))
    nb.cells += [
        md('## 6. Kiểm chứng và xuất sản phẩm\nKiểm tra tổng theo đơn, tháng và thị trường bằng tổng doanh số; '
           'tổng khách bằng phần doanh số có định danh. Kiểm tra đủ sáu ảnh và kỳ chưa đầy đủ. '
           'Ô cuối tạo báo cáo PDF, bản Markdown và kịch bản thuyết trình từ đúng số liệu vừa tính.'),
        code("result = validate(data, tables, figures)\nprint(result)\nbuild_report(ROOT, data, tables, figures)\nbuild_presentation(ROOT, tables)\n(ROOT / 'outputs/validation.txt').write_text(result + '\\n', encoding='utf-8')\nprint('Báo cáo:', ROOT / 'outputs/bao_cao_visual_analytics.pdf')"),
        md('## 7. Tự kiểm tra trước khi trình bày\n'
           '1. Tại sao 541.909 dòng không phải 541.909 đơn?\n'
           '2. Tại sao không bỏ mọi CustomerID thiếu?\n'
           '3. Mẫu số của thanh chồng và chỉ số giá trị hủy/doanh số khác nhau thế nào?\n'
           '4. Vì sao không kết luận tăng trưởng gây ra bởi quảng cáo?\n'
           '5. Biểu đồ có ẩn ngoại lệ không, và KPI có còn tính ngoại lệ không?\n\n'
           'Đáp án và kịch bản trình bày nằm trong `outputs/thuyet_trinh.md`. '
           'Có thể xem toàn bộ thuật toán qua `src/analysis.py` và tài liệu `docs/phuong_phap.md`.'),
    ]
    nbf.validate(nb)
    nbf.write(nb, root / 'visual_analytics.ipynb')


def build_presentation(root, t):
    s = t['stats']
    text = f'''# Kịch bản thuyết trình 5–7 phút

Điền tên nhóm, lớp và phân công người nói trước khi nộp. Mở PDF và trình bày theo trang, không cần slide riêng.

## 0:00–0:40 · Câu hỏi và thông điệp (trang 1)
Nhóm em phân tích dữ liệu bán lẻ trực tuyến để trả lời: doanh số tập trung ở đâu, khách hàng nào đóng góp nhiều và giá trị hủy cần được kiểm tra thế nào?
Ba điểm chính: UK chiếm {pct(s['uk_share_pct'])} doanh số; xấp xỉ 10% khách chi tiêu cao nhất đóng góp {pct(s['top10_customer_share_pct'])} doanh số có định danh; giá trị hủy bằng {pct(s['cancel_to_sales_pct'])} doanh số bán.

## 0:40–1:30 · Dữ liệu và làm sạch (trang 2–3)
Nguồn UCI Online Retail có {s['raw_rows']:,} dòng và 8 cột. Mỗi dòng là một dòng hàng, nên phải gộp InvoiceNo để tính đơn.
Nhóm tách bán, hủy theo mã C và dữ liệu bất thường. Giữ các giao dịch thiếu mã khách trong doanh số nhưng không đưa vào phân tích khách hàng.
Dòng trùng được giữ vì không có mã dòng hàng xác định lỗi; nếu loại thì doanh số thay đổi {money(s['duplicate_sale_value'])}. Ngoại lệ chỉ được xử lý cách hiển thị, không xóa tùy ý.

## 1:30–2:20 · Xu hướng và sản phẩm (trang 4–5)
Trong các tháng đầy đủ, {s['peak_month']} đạt doanh số cao nhất: {money(s['peak_sales'])}. Tháng 12/2011 chỉ có đến ngày 09, không thể dùng để kết luận suy giảm.
Sản phẩm dẫn đầu là {s['top_product']}, đạt {money(s['top_product_sales'])}. Nhóm dùng biểu đồ thanh để so sánh sản phẩm và biểu đồ đường cho thời gian.
Đề xuất là kiểm tra năng lực đáp ứng, chưa suy diễn nguyên nhân tăng do quảng cáo hay khẳng định tính mùa vụ từ một năm dữ liệu.

## 2:20–3:10 · Thị trường và hủy (trang 6)
Doanh số bán hợp lệ là {money(s['sales'])}; giá trị hủy là {money(s['cancellation'])}. UK đóng góp phần lớn doanh số nên cần ưu tiên kiểm tra theo tác động tuyệt đối.
Thanh chồng dùng mẫu số bán cộng trị tuyệt đối hủy để thể hiện cơ cấu; chỉ số hủy trên bán trong diễn giải có mẫu số khác.
Đây không phải tỷ lệ số đơn bị hủy, cũng chưa phải tỷ lệ trả hàng: cần ghép hóa đơn hủy với đơn gốc để xác minh.
Hai chứng từ hủy lớn nhất chiếm {pct(s['top2_cancellation_share_pct'])} tổng giá trị hủy, nên kiểm tra các chứng từ này trước. Mã 23843 xuất hiện trong cả dòng bán lớn 168,469.60 GBP và chứng từ hủy cùng giá trị; không nên xem thứ hạng doanh số trước hủy là bằng chứng đủ để tăng nhập hàng.

## 3:10–4:10 · Phân phối đơn hàng (trang 7–8)
Giá trị đơn trung vị là {money(s['median_order'])}, trung bình là {money(s['mean_order'])}. Đuôi phải dài khiến vài đơn lớn kéo trung bình lên.
Histogram cho biết phần tập trung; boxplot so sánh trung vị và phân tán giữa thị trường. Histogram chỉ hiện đến P99; boxplot ẩn điểm ngoài râu; KPI vẫn giữ toàn bộ giao dịch hợp lệ.
Vì khác biệt cơ cấu đơn, nên xem xét mục tiêu theo thị trường thay vì chỉ đặt một mức trung bình chung.

## 4:10–5:10 · Khách hàng (trang 9)
Có {s['customers']:,} khách được định danh, đóng góp {pct(s['identified_share_pct'])} doanh số. Nhóm top xấp xỉ 10% đóng góp {pct(s['top10_customer_share_pct'])} doanh số trong tập này.
Scatter sử dụng trục log để giữ cả khách chi tiêu lớn và nhỏ. Tương quan Spearman là {s['spearman_orders_spending']:.3f}, nhưng tổng chi tiêu vốn được cộng qua các đơn nên không thể diễn giải nhân quả.
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
'''
    (Path(root) / 'outputs/thuyet_trinh.md').write_text(text, encoding='utf-8')
