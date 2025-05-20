import re


def process_person_info(person_info):
    pattern = re.compile(r"^(.*)\((\d{4})–(\d{4})\)$")
    match = pattern.match(person_info.strip())
    if match:
        return {
            "name": match.group(1).strip(),
            "date_of_birth": match.group(2),
            "date_of_death": match.group(3),
        }
    return {"name": person_info.strip(), "date_of_birth": None, "date_of_death": None}