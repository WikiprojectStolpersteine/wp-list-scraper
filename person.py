import re
from html import unescape

def process_person_info(person_info):
    # Unescape HTML entities and normalize whitespace
    text = unescape(person_info).replace("\n", " ").strip()
    
    # Remove HTML tags like <br>
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Try to match the {{PersonZelle|First|Last|...}} template
    personzelle_pattern = re.compile(r"\{\{PersonZelle\|([^|]+)\|([^|]+)")
    match = personzelle_pattern.search(text)
    if match:
        first_name = match.group(1).strip()
        last_name = match.group(2).strip()
        return {
            "name": f"{first_name} {last_name}",
            "date_of_birth": None,
            "date_of_death": None,
        }

    # Fallback: try to extract name with birth–death years (e.g., "John Doe (1890–1942)")
    pattern = re.compile(r"^(.*)\((\d{4})–(\d{4})\)$")
    match = pattern.match(text)
    if match:
        return {
            "name": match.group(1).strip(),
            "date_of_birth": match.group(2),
            "date_of_death": match.group(3),
        }

    # Default: return plain name if nothing else matches
    return {
        "name": text,
        "date_of_birth": None,
        "date_of_death": None,
    }
