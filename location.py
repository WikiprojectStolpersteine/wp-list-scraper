import re
from html import unescape

def process_location(cell):
    # Unescape HTML entities and normalize
    cell = unescape(cell)

    # Remove coordinate templates and any <br> or other HTML tags
    cleaned = re.sub(r"\{\{Coordinate[^\}]+\}\}", "", cell, flags=re.IGNORECASE)
    cleaned = re.sub(r"<br\s*/?>", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)  # remove any other tags

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned
