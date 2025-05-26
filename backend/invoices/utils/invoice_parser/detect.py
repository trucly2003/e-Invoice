def detect_template(normalized_text: str) -> str:
    print("📌 DEBUG DETECT TEXT SNIPPET:", normalized_text[:1000])

    if (
        "hapag" in normalized_text  # Thay vì phải full hapag-lloyd
        or "serial no" in normalized_text
        or "so invoice no" in normalized_text
        or "ref no" in normalized_text
        or "customer code" in normalized_text
    ):
        print("✅ Detected Hapag layout")
        return "hapag_layout"

    elif "vinvoice.viettel.vn" in normalized_text or "tap doan cong nghiep - vien thong quan doi" in normalized_text:
        print("✅ Detected Viettel layout")
        return "viettel_layout"

    else:
        print("⚠️ Detected Generic layout")
        return "generic"
