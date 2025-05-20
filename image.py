import re
from urllib.parse import unquote


def extract_image(cell):
    match = re.search(r"Datei:(.*?)(\||\]\])", cell)
    if match:
        return unquote(match.group(1))
    return None