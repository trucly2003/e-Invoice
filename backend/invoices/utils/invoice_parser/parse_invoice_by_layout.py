from .normalize import normalize_text_for_matching
from .detect import detect_template
from . import hapag_layout, viettel_layout

def parse_invoice_by_layout(text: str, file_type: str = "PDF") -> dict:
    # normalize chỉ để detect layout thôi
    layout = detect_template(normalize_text_for_matching(text))
    print(f"🧭 Detected layout: {layout} (file_type={file_type})")

    if layout == "hapag_layout":
        if file_type.upper() == "PDF":
            return hapag_layout.parse_pdf(normalize_text_for_matching(text))
        else:
            return hapag_layout.parse_image(text)