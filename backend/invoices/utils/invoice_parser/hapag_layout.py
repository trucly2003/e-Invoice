import re
from datetime import datetime

def parse_amount_ocr(text: str) -> float:
    try:
        return float(text.replace(".", "").replace(",", "").strip())
    except:
        return 0.0

def correct_ocr_code(code: str) -> str:
    code = code.upper()

    # Nếu mã có đúng pattern OCR hay sai: SGS → SG5
    code = code.replace("SGS", "SG5")

    # Các sửa lỗi phổ biến khác
    code = code.replace("1", "L")
    code = code.replace("0", "O")

    return code



def auto_correct_ocr(text: str) -> str:
    corrections = {
        "c0ng": "cong", "ll0yd": "lloyd", "v1et": "viet", "h0a": "hoa",
        "g1a": "gia", "tr1": "tri", "1en": "dien", "1nv01ce": "invoice",
        "5er1al": "serial", "addre55": "address", "cu5t0mer": "customer",
        "un1lever": "unilever", "tax 1d": "tax id", "ma 50 thue": "ma so thue",
        "ma 50": "ma so", "m5t": "mst", "ph0": "pho", "ch1": "chi",
        "h0": "ho", "m1nh": "minh", "5a1l1ng": "sailing", "d0lph1n": "dolphin",
        "p0l": "pol", "p0d": "pod", "0n": "on", "1a ch1": "dia chi"
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text




def normalize_ocr_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.lower()

def normalize_ocr_numbers(text: str) -> str:
    return re.sub(r"(?<=\d) (?=\d)", "", text)


def init_parsed_dict() -> dict:
    return {
        "invoice_number": "",
        "invoice_date": None,
        "seller_name": "",
        "seller_tax": "",
        "seller_address": "",
        "buyer_name": "",
        "buyer_tax": "",
        "buyer_address": "",
        "total_amount": 0.0,
        "vat_amount": 0.0,
        "grand_total": 0.0,
        "link_tra_cuu": "",
        "ma_tra_cuu": "",
        "serial": "",
        "items": []
    }

def parse_pdf(text: str) -> dict:
    parsed = init_parsed_dict()

    match_invoice = re.search(r"(so|invoice no)[^\d]{0,10}(\d{6,})", text)
    if match_invoice:
        parsed["invoice_number"] = match_invoice.group(2).strip()

    match_date = re.search(r"ngay (\d{1,2}) thang (\d{1,2}) nam (\d{4})", text)
    if match_date:
        day, month, year = match_date.groups()
        parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()

    match_serial = re.search(r"(serial[\s:\-]*)([a-zA-Z0-9]{4,})", text)
    if match_serial:
        parsed["serial"] = match_serial.group(2).upper()
    else:
        match_serial = re.search(r"\b(c\d{2}[a-z]{3})\b", text)
        if match_serial:
            parsed["serial"] = match_serial.group(1).upper()

    match_seller_name = re.search(r"(cong ty tnhh[^\n\r]{0,80})", text)
    if match_seller_name:
        name_raw = match_seller_name.group(1).strip()
        name_cut = re.split(r"(hoa|mst|ma so thue|ngay|serial)", name_raw)[0].strip()
        parsed["seller_name"] = name_cut

    match_seller_tax = re.search(r"(mst|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", text)
    if match_seller_tax:
        parsed["seller_tax"] = match_seller_tax.group(2).replace(" ", "").strip()

    match_seller_address = re.search(
        r"(?:serial no\.?\s*:\s*[a-z0-9]+)?\s*(\d{2,4}\s+(uong|duong|phuong)[^\n\r]{10,80}?)\s+(so invoice no|ref no|thanh pho|viet nam)",
        text
    )
    if match_seller_address:
        parsed["seller_address"] = match_seller_address.group(1).strip()

    match_buyer_name = re.search(
        r"(?:customer|nguoi mua|ben mua)\s*[:\-]?\s*(cong ty[^\n\r]*?)\s*(?=(address|dia chi|ma so thue|tax id|customer code|mst))",
        text
    )
    if match_buyer_name:
        parsed["buyer_name"] = re.sub(r"\bia chi\b", "", match_buyer_name.group(1).strip())

    match_mtc = re.search(r"ma tra cuu.*?[:\-]?\s*([a-z0-9]{8,})", text)
    if match_mtc:
        parsed["ma_tra_cuu"] = match_mtc.group(1).strip().upper()

    if "tracuu" in text and "ehoadon" in text:
        parsed["link_tra_cuu"] = "http://tracuu.ehoadon.vn"

    match_buyer_tax = re.search(r"(tax id|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(2).replace(" ", "").strip()

    match_buyer_address = re.search(
        r"(?:address|dia chi)\s*[:\-]?\s*([a-z0-9\s\,\.\-]{10,150}?)(?=\s+(ma so thue|tax id|customer code|mst|so invoice no|ref no|tong))",
        text
    )
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(1).strip()

    match_total = re.search(r"(total amount|cong tien hang.*?)\s*[:\-]?\s*([\d\.]+)", text)
    if match_total:
        parsed["total_amount"] = float(match_total.group(2).replace(".", ""))

    match_vat = re.search(r"(vat amount|tong cong tien thue)\s*[:\-]?\s*([\d\.]+)", text)
    if match_vat:
        parsed["vat_amount"] = float(match_vat.group(2).replace(".", ""))

    match_grand = re.search(r"(grand total|tong cong tien thanh toan)\s*[:\-]?\s*([\d\.]+)", text)
    if match_grand:
        parsed["grand_total"] = float(match_grand.group(2).replace(".", ""))

    return parsed

def parse_image(raw: str) -> dict:
    parsed = {
        "invoice_number": "",
        "invoice_date": None,
        "seller_name": "",
        "seller_tax": "",
        "seller_address": "",
        "buyer_name": "",
        "buyer_tax": "",
        "buyer_address": "",
        "total_amount": 0.0,
        "vat_amount": 0.0,
        "grand_total": 0.0,
        "link_tra_cuu": "",
        "ma_tra_cuu": "",
        "serial": "",
        "items": [],
    }

    raw_joined = raw.replace("\n", " ").lower()

    # ✅ Bắt ngày hóa đơn
    m = re.search(r"ngày\s*(\d{1,2})\s*(\d{1,2})\s*năm\s*(\d{4})", raw_joined)
    if m:
        d, mth, y = m.groups()
        try:
            parsed["invoice_date"] = datetime(int(y), int(mth), int(d)).date()
        except:
            raise ValueError("❌ Ngày không hợp lệ.")
    else:
        raise ValueError("❌ Không tìm được ngày hóa đơn.")

    # ✅ Invoice number
    m = re.search(r"s[ốo]\s*\(invoice\s*no\W*\)?\s*[:\-]?\s*(\d{6,})", raw.lower())
    if m:
        parsed["invoice_number"] = m.group(1).strip()

    # ✅ Serial
    m = re.search(r"Ký hiệu\s*\(Serial No\.\)\s*[\n:]?\s*([A-Z0-9]{4,})", raw, re.IGNORECASE)
    if m:
        parsed["serial"] = m.group(1).strip().upper()

    # ✅ Seller
    if "hapag-lloyd" in raw_joined:
        parsed["seller_name"] = "CÔNG TY TNHH HAPAG-LLOYD (VIỆT NAM)"

    m = re.search(r"mst\s*[:\-]?\s*([\d\s]{10,})", raw_joined)
    if m:
        parsed["seller_tax"] = m.group(1).replace(" ", "").strip()

    m = re.search(r"72\s*,?\s*đường[^\n]+phường[^\n]+quận[^\n]+thành phố.*?việt nam", raw_joined)
    if m:
        parsed["seller_address"] = m.group(0).strip()

    # ✅ Buyer
    m = re.search(r"Customer\):\s*(CONG TY TNHH[^\n\r]*)", raw, re.IGNORECASE)
    if m:
        parsed["buyer_name"] = m.group(1).strip()

    m = re.search(r"Address\):\s*([^\n\r]+)", raw, re.IGNORECASE)
    if m:
        parsed["buyer_address"] = m.group(1).strip()

    m = re.search(r"Tax ID\):\s*([\d\s]{10,})", raw, re.IGNORECASE)
    if m:
        parsed["buyer_tax"] = m.group(1).replace(" ", "").strip()

    # ✅ Amounts
    m = re.search(r"(total amount|cộng tiền hàng).*?[:\-]?\s*([\d\.]+)", raw_joined)
    if m:
        parsed["total_amount"] = parse_amount_ocr(m.group(2))

    m = re.search(r"(vat amount|tổng cộng tiền thuế).*?[:\-]?\s*([\d\.]+)", raw_joined)
    if m:
        parsed["vat_amount"] = parse_amount_ocr(m.group(2))

    m = re.search(r"(grand total|tổng cộng tiền thanh toán).*?[:\-]?\s*([\d\.]+)", raw_joined)
    if m:
        parsed["grand_total"] = parse_amount_ocr(m.group(2))

    for line in raw.split("\n"):
        if "mã tra cứu" in line.lower():
            print("📌 Mã tra cứu nằm trong dòng:", line)

    # ✅ Tra cứu
    m = re.search(r"mã tra cứu.*?([A-Z0-9]{10,})", raw, re.IGNORECASE)
    if m:
        raw_code = m.group(1).strip()
        parsed["ma_tra_cuu"] = correct_ocr_code(raw_code)

    if "tracuu.ehoadon.vn" in raw.lower():
        parsed["link_tra_cuu"] = "http://tracuu.ehoadon.vn"


    return parsed