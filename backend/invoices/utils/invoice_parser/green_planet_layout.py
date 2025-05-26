import re
from datetime import datetime

def parse_amount_ocr(s: str) -> float:
    return float(s.replace(",", "").replace(".", "").strip())

def correct_ocr_code(text: str) -> str:
    return text.upper().replace("S", "5").replace("O", "0").replace("I", "1")

def remove_spaces(text: str) -> str:
    return re.sub(r"\s+", "", text).strip()

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

def parse_common(text: str, is_image=False) -> dict:
    parsed = init_parsed_dict()

    if is_image:
        text = normalize_ocr_text(text)
        text = normalize_ocr_numbers(text)

    invoice_pattern = r"(invoice no\.?|so)(?:[:\-\s])?\s*([\d\s]{5,20})"
    serial_pattern = r"(serial no\.?|ky hieu)(?:[:\-\s])?\s*([a-z0-9\s]{4,20})"
    seller_tax_pattern = r"(mst|tax code|ma so thue)(?:[:\-\s])?\s*([\d\s]{8,})"

    match_invoice = re.search(invoice_pattern, text, re.IGNORECASE)
    if match_invoice:
        parsed["invoice_number"] = remove_spaces(match_invoice.group(2))

    match_date = re.search(r"ngay (\d{1,2}) thang (\d{1,2}) nam (\d{4})", text)
    if match_date:
        day, month, year = match_date.groups()
        parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()

    match_serial = re.search(serial_pattern, text, re.IGNORECASE)
    if match_serial:
        parsed["serial"] = remove_spaces(match_serial.group(2)).upper()

    match_seller_tax = re.search(seller_tax_pattern, text, re.IGNORECASE)
    if match_seller_tax:
        parsed["seller_tax"] = remove_spaces(match_seller_tax.group(2))

    match_seller_name = re.search(r"(cong ty tnhh[^\n\r]{0,80})", text, re.IGNORECASE)
    if match_seller_name:
        name_raw = match_seller_name.group(1).strip()
        name_cut = re.split(r"(hoa|mst|ma so thue|ngay|serial)", name_raw)[0].strip()
        parsed["seller_name"] = name_cut

    if not is_image:
        match_seller_address = re.search(r"(?:serial no\.?\s*:\s*[a-z0-9]+)?\s*(\d{2,4}\s+(uong|duong|phuong)[^\n\r]{10,80}?)\s+(so invoice no|ref no|thanh pho|viet nam)", text)
    else:
        match_seller_address = re.search(r"(\d{2,4}\s+(duong|uong|phuong)[^\n\r]{10,80})", text)
    if match_seller_address:
        parsed["seller_address"] = match_seller_address.group(1).strip()

    match_buyer_name = re.search(r"(?:customer|nguoi mua|ben mua)(?:[:\-\s])?\s*(cong ty[^\n\r]*?)\s*(?=(address|dia chi|ma so thue|tax id|customer code|mst))", text)
    if match_buyer_name:
        parsed["buyer_name"] = match_buyer_name.group(1).strip()

    match_buyer_tax = re.search(r"(tax id|ma so thue)(?:[:\-\s])?\s*([\d\s]{8,})", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = remove_spaces(match_buyer_tax.group(2))

    match_buyer_address = re.search(r"(?:address|dia chi)(?:[:\-\s])?\s*([a-z0-9\s\,\.\-]{10,150})(?=\s+(ma so thue|tax id|customer code|mst|so invoice no|ref no|tong))", text)
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(1).strip()

    match_total = re.search(r"(total amount|cong tien hang.*?)\s*[:\-\s]?\s*([\d\.,]+)", text)
    if match_total:
        parsed["total_amount"] = parse_amount_ocr(match_total.group(2))

    match_vat = re.search(r"(vat amount|tong cong tien thue)\s*[:\-\s]?\s*([\d\.,]+)", text)
    if match_vat:
        parsed["vat_amount"] = parse_amount_ocr(match_vat.group(2))

    match_grand = re.search(r"(grand total|tong cong tien thanh toan|cong tien thanh toan)\s*[:\-\s]?\s*([\d\.,]+)", text)
    if match_grand:
        parsed["grand_total"] = parse_amount_ocr(match_grand.group(2))

    match_mtc = re.search(r"ma tra cuu.*?[:\-\s]?\s*([a-z0-9\s]{8,20})", text, re.IGNORECASE)
    if match_mtc:
        parsed["ma_tra_cuu"] = correct_ocr_code(remove_spaces(match_mtc.group(1)))

    if "tracuu.ehoadon.vn" in text:
        parsed["link_tra_cuu"] = "http://tracuu.ehoadon.vn"

    return parsed

def parse_pdf(text: str) -> dict:
    return parse_common(text, is_image=False)

def parse_image(text: str) -> dict:
    return parse_common(text, is_image=True)
