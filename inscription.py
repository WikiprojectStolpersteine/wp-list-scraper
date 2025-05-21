import re
from html import unescape


def process_inscription(inscription):
    # Remove all HTML tags like <small>, <br>, etc.
    plain_text = re.sub(r"<[^>]+>", "\n", inscription)
    plain_text = unescape(plain_text)  # Convert HTML entities
    formatted_inscription = plain_text.replace("\n", " ").strip()
    formatted_inscription = re.sub(r"\s+", " ", formatted_inscription)  # Normalize whitespace

    # Extract useful metadata
    year_pattern = re.compile(r"\b(\d{4})\b")
    dob_pattern = re.compile(r"JG\. (\d{4})")
    dod_pattern = re.compile(r"ERMORDET (\d{4})")
    death_place_pattern = re.compile(r"IN ([A-ZÄÖÜ][A-Za-zÄÖÜäöüß\s\/\-]+)")

    years = year_pattern.findall(formatted_inscription)
    dob = dob_pattern.search(formatted_inscription)
    dod = dod_pattern.search(formatted_inscription)
    death_place = death_place_pattern.search(formatted_inscription)

    return {
        "text": formatted_inscription,
        "years": years,
        "date_of_birth": dob.group(1) if dob else None,
        "date_of_death": dod.group(1) if dod else None,
        "place_of_death": death_place.group(1) if death_place else None,
    }
