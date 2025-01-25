import requests
from bs4 import BeautifulSoup
import re
import json
import sys
from urllib.parse import unquote


def fetch_stolpersteine_data(list_name):
    # Construct the Wikipedia URL
    base_url = "https://de.wikipedia.org/wiki/"
    url = base_url + list_name.replace(" ", "_")

    # Fetch the rendered HTML content
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(
            f"Failed to fetch the page. Status code: {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing Stolperstein data
    tables = soup.find_all("table")
    table = None
    for t in tables:
        if "Stolperstein" in t.text:
            table = t
            break

    if not table:
        raise ValueError("No relevant table found on the page.")

    # Extract table headers
    headers = [header.text.strip() for header in table.find_all("th")]

    # Extract table rows
    rows = []
    table_rows = table.find_all("tr")
    for row in table_rows:
        td = row.find_all("td")
        row_data = [str(cell) for cell in td]  # Keep raw HTML for coordinate extraction
        if row_data:
            rows.append(row_data)

    # Helper function to extract coordinates from template
    coord_pattern = re.compile(r"\{\{Coordinate\|.*?\|NS=([\d\.]+)\|EW=([\d\.]+)")

    def extract_coordinates(cell):
        match = coord_pattern.search(cell)
        if match:
            return {
                "latitude": float(match.group(1)),
                "longitude": float(match.group(2)),
            }
        return None

    # Helper function to process inscription text
    def process_inscription(inscription):
        # Replace line breaks with spaces
        formatted_inscription = inscription.replace("\n", " ").strip()

        # Extract years and places
        year_pattern = re.compile(r"\b(\d{4})\b")
        place_pattern = re.compile(r"[A-Z][a-z]+(?: [A-Z][a-z]+)*")

        years = year_pattern.findall(formatted_inscription)
        places = place_pattern.findall(formatted_inscription)

        # Extract specific dates and death places
        dob_pattern = re.compile(r"JG\. (\d{4})")
        dod_pattern = re.compile(r"ERMORDET (\d{4})")
        death_place_pattern = re.compile(r"IN ([A-Z][a-z]+(?: [A-Z][a-z]+)*)")

        date_of_birth = dob_pattern.search(formatted_inscription)
        date_of_death = dod_pattern.search(formatted_inscription)
        place_of_death = death_place_pattern.search(formatted_inscription)

        return {
            "text": formatted_inscription,
            "years": years,
            "places": places,
            "date_of_birth": date_of_birth.group(1) if date_of_birth else None,
            "date_of_death": date_of_death.group(1) if date_of_death else None,
            "place_of_death": place_of_death.group(1) if place_of_death else None,
        }

    # Helper function to process person info
    def process_person_info(person_info):
        pattern = re.compile(r"^(.*)\((\d{4})–(\d{4})\)$")
        match = pattern.match(person_info.strip())
        if match:
            name = match.group(1).strip()
            birth_year = match.group(2)
            death_year = match.group(3)
            return {
                "name": name,
                "date_of_birth": birth_year,
                "date_of_death": death_year,
            }
        return {
            "name": person_info.strip(),
            "date_of_birth": None,
            "date_of_death": None,
        }

    # Helper function to extract image filename
    def extract_image(cell):
        match = re.search(r"Datei:(.*?)(\")", cell)
        if match:
            return unquote(match.group(1))
        return None

    # Process rows into structured data
    data = []
    for row in rows:
        if len(row) >= 4:  # Ensure sufficient columns exist
            raw_image = row[0]
            raw_location = row[2]
            raw_inscription = BeautifulSoup(row[1], "html.parser").text.strip()
            raw_person_info = BeautifulSoup(row[3], "html.parser").text.strip()

            stolperstein_data = {
                "image": extract_image(raw_image),
                "inscription": process_inscription(raw_inscription),
                "location": BeautifulSoup(raw_location, "html.parser").text.strip(),
                "person_info": process_person_info(raw_person_info),
                "coordinates": extract_coordinates(raw_location),
            }
            data.append(stolperstein_data)

    return data


if __name__ == "__main__":
    list_name = ""
    if len(sys.argv) != 2:
        print("Usage: python script.py <list_name>")
        print("Using default list name: Liste_der_Stolpersteine_in_Pasewalk")
        list_name = "Liste_der_Stolpersteine_in_Pasewalk"
    else:
        list_name = sys.argv[1]

    try:
        stolpersteine_data = fetch_stolpersteine_data(list_name)

        # Save the data to a JSON file
        output_file = f"stolpersteine_{list_name.replace(' ', '_')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stolpersteine_data, f, ensure_ascii=False, indent=4)

        print(
            f"Extracted {len(stolpersteine_data)} entries. Data saved to {output_file}."
        )
    except Exception as e:
        print(f"Error: {e}")
