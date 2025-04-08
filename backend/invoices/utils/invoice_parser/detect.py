def detect_template(normalized_text: str) -> str:
    if "awb" in normalized_text and "luu kho hang" in normalized_text:
        return "green_planet_layout"
    elif "so bill" in normalized_text and "phi chung tu" in normalized_text:
        return "sankyu_layout"
    elif "so van don" in normalized_text and "thu ho phi xep do" in normalized_text:
        return "msc_layout"
    elif "hapag-lloyd" in normalized_text and "vat amount" in normalized_text:
        return "hapag_layout"
    else:
        return "generic"
