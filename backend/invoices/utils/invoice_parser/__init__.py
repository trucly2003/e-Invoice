from .detect import detect_template
from . import green_planet_layout, sankyu_layout, msc_layout, hapag_layout, generic

def parse_invoice_by_layout(text: str) -> dict:
    layout = detect_template(text)
    print(f"🧭 Detected layout: {layout}")

    if layout == "green_planet_layout":
        return green_planet_layout.parse(text)
    elif layout == "sankyu_layout":
        return sankyu_layout.parse(text)
    elif layout == "msc_layout":
        return msc_layout.parse(text)
    elif layout == "hapag_layout":
        return hapag_layout.parse(text)
    else:
        return generic.parse(text)
