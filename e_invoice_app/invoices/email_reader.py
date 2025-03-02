import imaplib
import email
import re
from django.utils.timezone import make_aware
from datetime import datetime
from invoices.models import Email, InvoiceData
import html2text

EMAIL_ACCOUNT = "nguyenly1204kh@gmail.com"
EMAIL_PASSWORD = "qxeh xznv ftqr hxcc" 
IMAP_SERVER = "imap.gmail.com"

def fetch_latest_email():
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

        mail.select("inbox")
        result, data = mail.search(None, "ALL") 

        email_ids = data[0].split()
        if not email_ids:
            print("⚠ Không có email nào mới.")
            return
        
        latest_email_id = email_ids[-1]  
        result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        sender = msg["From"]
        recipient = msg["To"]
        received_date_raw = msg["Date"]

        try:
            received_date = make_aware(datetime.strptime(received_date_raw, "%a, %d %b %Y %H:%M:%S %z"))
        except ValueError:
            received_date = None

        content = ""

        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                content = part.get_payload(decode=True).decode()
            elif part.get_content_type() == "text/html":  # Nếu email là HTML
                content = html2text.html2text(part.get_payload(decode=True).decode())

        # Lưu nội dung email vào database
        email_obj = Email.objects.create(
            sender=sender,
            recipient=recipient,
            received_date=received_date,
            content=content
        )
        
        print("✅ Email đã được lưu vào database!")

        # Trích xuất thông tin hóa đơn
        extract_invoice_data(email_obj, content)

        mail.logout()

    except Exception as e:
        print(f"❌ Lỗi: {e}")

def extract_invoice_data(email_obj, content):
    # Regex để lấy thông tin hóa đơn
    company_pattern = r"Cảm ơn quý khách hàng đã mua hàng tại (.+?)\."
    lookup_link_pattern = r"(https?://[^\s]+|tracuu\.ehoadon\.vn[^\s]*)"
    invoice_code_pattern = r"Mã tra\s*cứu(?: là)?\s*[:：]?\s*\n?([\w\d]+)"
    template_number_pattern = r"Mẫu số: (\d+)"
    symbol_pattern = r"Ký hiệu: (\S+)"
    invoice_number_pattern = r"Số Hóa đơn: (\d+)"
    invoice_date_pattern = r"Ngày Hóa đơn: (\d{2}/\d{2}/\d{4})"
    total_amount_pattern = r"Tổng thanh toán: ([\d,]+)"
    status_pattern = r"Trạng thái: (.+)"
    ref_no_pattern = r"RefNo: (\d+)"
    bl_number_pattern = r"Số vận đơn: (\S+)"
    bank_account_vnd_pattern = r"(\d{3}-\s*\d+)\s*\(VND\)"
    bank_account_usd_pattern = r"(\d{3}-\s*\d+)\s*\(USD\)"
    swift_code_pattern = r"Swift Code : (\S+)"

    def extract(pattern, text):
        match = re.search(pattern, text)
        return match.group(1) if match else None

    invoice_data = InvoiceData.objects.create(
        email=email_obj,
        company_name=extract(company_pattern, content),
        invoice_lookup_link=extract(lookup_link_pattern, content),
        invoice_code=extract(invoice_code_pattern, content),
        template_number=extract(template_number_pattern, content),
        symbol=extract(symbol_pattern, content),
        invoice_number=extract(invoice_number_pattern, content),
        invoice_date=datetime.strptime(extract(invoice_date_pattern, content), "%d/%m/%Y") if extract(invoice_date_pattern, content) else None,
        total_amount=float(extract(total_amount_pattern, content).replace(",", "")) if extract(total_amount_pattern, content) else 0,
        status=extract(status_pattern, content),
        ref_no=extract(ref_no_pattern, content),
        bl_number=extract(bl_number_pattern, content),
        bank_account_vnd=extract(bank_account_vnd_pattern, content),
        bank_account_usd=extract(bank_account_usd_pattern, content),
        swift_code=extract(swift_code_pattern, content)
    )