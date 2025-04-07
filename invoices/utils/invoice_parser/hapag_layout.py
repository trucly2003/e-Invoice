from datetime import datetime
import re

def parse(text: str) -> dict:
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
        "serial": "",
        "items": []
    }

    match_invoice = re.search(r"(so|invoice no)[^\d]{0,10}(\d{6,})", text)
    if match_invoice:
        parsed["invoice_number"] = match_invoice.group(2).strip()

    match_date = re.search(r"ngay (\\d{1,2}) thang (\\d{1,2}) nam (\\d{4})", text)
    if not match_date:
        match_date = re.search(r"ngay.*?(\\d{1,2}).*?thang.*?(\\d{1,2}).*?nam.*?(\\d{4})", text)

    match_serial = re.search(r"ky hieu serial\s*([a-z0-9\-]+)", text)
    if match_serial:
        parsed["serial"] = match_serial.group(1).upper()

    match_seller = re.search(r"cong ty tnhh hapag-lloyd.*?mst[:\-\s]*?(\d+[\d\s]*)", text)
    if match_seller:
        parsed["seller_name"] = "CÔNG TY TNHH HAPAG-LLOYD (VIỆT NAM)"
        parsed["seller_tax"] = match_seller.group(1).replace(" ", "").strip()
        parsed["seller_address"] = "72, Đường Lê Thánh Tôn, Phường Bến Nghé, Quận 1, TP.HCM"

    match_buyer_name = re.search(
        r"(?:customer|nguo[iy] mua|ben mua)\s*[:\-]?\s*(cong ty[^\n]*?)\s+(?:ia chi|dia chi|address|ma so thue|tax id)",
        text
    )
    if match_buyer_name:
        parsed["buyer_name"] = match_buyer_name.group(1).strip()

    match_buyer_tax = re.search(r"(tax id|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(2).replace(" ", "").strip()

    match_buyer_address = re.search(
        r"(dia chi|ia chi|address)\s*[:\-]?\s*(.+?)(ma so thue|tax id|customer code)", text
    )
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(2).strip()

    match_total = re.search(r"total amount\s*[:\-]?\s*([\d\.]+)", text)
    if match_total:
        parsed["total_amount"] = float(match_total.group(1).replace(".", ""))

    match_vat = re.search(r"vat amount\s*[:\-]?\s*([\d\.]+)", text)
    if match_vat:
        parsed["vat_amount"] = float(match_vat.group(1).replace(".", ""))

    match_grand = re.search(r"grand total\s*[:\-]?\s*([\d\.]+)", text)
    if match_grand:
        parsed["grand_total"] = float(match_grand.group(1).replace(".", ""))

    return parsed
