import re


def process_inscription(inscription):
    formatted_inscription = inscription.replace("\n", " ").strip()
    year_pattern = re.compile(r"\b(\d{4})\b")
    dob_pattern = re.compile(r"JG\. (\d{4})")
    dod_pattern = re.compile(r"ERMORDET (\d{4})")
    death_place_pattern = re.compile(r"IN ([A-Z][a-z]+(?: [A-Z][a-z]+)*)")

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