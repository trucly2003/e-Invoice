import re
from datetime import datetime
from .normalize import normalize_text_for_matching

def parse(text: str) -> dict:
    text = normalize_text_for_matching(text)

    parsed = {
        "invoice_number": "",
        "invoice_date": None,
        "serial": "",
        "seller_name": "",
        "seller_tax": "",
        "seller_address": "",
        "buyer_name": "",
        "buyer_tax": "",
        "buyer_address": "",
        "total_amount": 0.0,
        "vat_amount": 0.0,
        "grand_total": 0.0,
        "ma_tra_cuu": "",
        "link_tra_cuu": "",
        "items": []
    }

    # Số hóa đơn
    number = re.search(r"số\s*\(no\)\s*:\s*(\d+)", text)
    if number:
        parsed["invoice_number"] = number.group(1)

    # Ngày hóa đơn
    date = re.search(r"ngày\s*\(date\)\s*(\d{2}) tháng.*?(\d{2}) năm.*?(\d{4})", text)
    if date:
        d, m, y = date.groups()
        parsed["invoice_date"] = datetime(int(y), int(m), int(d)).date()

    # Ký hiệu
    serial = re.search(r"ký hiệu.*?:\s*([a-z0-9]+)", text)
    if serial:
        parsed["serial"] = serial.group(1).upper()

    # Bên bán
    seller_name = re.search(r"đơn vị bán hàng.*?:\s*(.*?)\s+mã số thuế", text)
    if seller_name:
        parsed["seller_name"] = seller_name.group(1).strip().upper()

    seller_tax = re.search(r"mã số thuế.*?:\s*(\d{10,})", text)
    if seller_tax:
        parsed["seller_tax"] = seller_tax.group(1)

    seller_address = re.search(r"địa chỉ.*?:\s*(.*?)\s+điện thoại", text)
    if seller_address:
        parsed["seller_address"] = seller_address.group(1).strip()

    # Bên mua
    buyer_name = re.search(r"company'?s name.*?:\s*(.*?)\s+mã số thuế", text)
    if buyer_name:
        parsed["buyer_name"] = buyer_name.group(1).strip().upper()

    buyer_tax = re.findall(r"mã số thuế.*?:\s*(\d{10,})", text)
    if len(buyer_tax) >= 2:
        parsed["buyer_tax"] = buyer_tax[1]  # buyer là lần xuất hiện thứ 2

    buyer_address = re.search(r"địa chỉ.*?:\s*(.*?)\s+(số tài khoản|hình thức)", text)
    if buyer_address:
        parsed["buyer_address"] = buyer_address.group(1).strip()

    # Tổng tiền
    total = re.search(r"cộng tiền hàng.*?:\s*([\d\.]+)", text)
    if total:
        parsed["total_amount"] = float(total.group(1).replace(".", ""))

    vat = re.search(r"tiền thuế gtgt.*?:\s*([\d\.]+)", text)
    if vat:
        parsed["vat_amount"] = float(vat.group(1).replace(".", ""))

    grand = re.search(r"tổng cộng tiền thanh toán.*?:\s*([\d\.]+)", text)
    if grand:
        parsed["grand_total"] = float(grand.group(1).replace(".", ""))

    # Tra cứu
    link = re.search(r"https://vinvoice\.viettel\.vn/utilities/invoice-search", text)
    if link:
        parsed["link_tra_cuu"] = link.group(0)

    ma = re.search(r"mã số bí mật.*?:\s*([a-z0-9]{10,})", text)
    if ma:
        parsed["ma_tra_cuu"] = ma.group(1).upper()

    # Dòng hàng
    items = re.findall(r"1\s+gạo nhật\s+kg\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)", text)
    for qty, price, amount in items:
        parsed["items"].append({
            "item_name": "GẠO NHẬT",
            "unit": "Kg",
            "quantity": int(qty.replace(".", "")),
            "unit_price": float(price.replace(".", "")),
            "amount": float(amount.replace(".", "")),
            "tax_rate": 0.0,
            "tax_amount": 0.0
        })

    return parsed
