# parse_utils/parse_invoice_by_layout.py
from .normalize import normalize_text_for_matching
from .detect import detect_template
from . import green_planet_layout, sankyu_layout, msc_layout, hapag_layout, generic, viettel_layout

def parse_invoice_by_layout(text: str) -> dict:
    normalized_text = normalize_text_for_matching(text)
    layout = detect_template(normalized_text)
    print(f"🧭 Detected layout: {layout}")

    if layout == "green_planet_layout":
        return green_planet_layout.parse(normalized_text)
    elif layout == "sankyu_layout":
        return sankyu_layout.parse(normalized_text)
    elif layout == "msc_layout":
        return msc_layout.parse(normalized_text)
    elif layout == "hapag_layout":
        return hapag_layout.parse(normalized_text)
    else:
        return generic.parse(normalized_text)


# def parse_invoice_by_layout(text: str) -> dict:
#     normalized_text = normalize_text_for_matching(text)
#
#     # Nếu chỉ dùng hóa đơn Viettel, bạn có thể bỏ detect_template hoàn toàn:
#     print(f"🧭 Using layout: viettel_layout")
#
#     return viettel_layout.parse(normalized_text)
