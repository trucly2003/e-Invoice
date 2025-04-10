import re
import unicodedata

def normalize_text_for_matching(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r"[^a-z0-9:/\-\s\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
