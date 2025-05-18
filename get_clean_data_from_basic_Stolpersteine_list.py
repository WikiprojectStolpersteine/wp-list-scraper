import requests
from bs4 import BeautifulSoup
import re
import json
import sys
from urllib.parse import unquote


def fetch_stolpersteine_data(list_name, column_aliases):
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

    # Find all tables
    tables = soup.find_all("table")
    if not tables:
        raise ValueError("No tables found on the page.")
    
    data = []

    # Iterate over tables
    for table in tables:
        # Get the table name from the header above the table
        header = table.find_previous("h2")
        table_name = header.text.strip() if header else list_name
        print(table_name)
        if table_name == "Einzelnachweise":
            # Skip unusable tables
            print("Skipping a table called: " + table_name)
            continue
        # Extract headers
        headers = [th.text.strip() for th in table.find_all("th")]
        print("Headers: " + str(headers))

        # Map headers to column indices based on aliases
        column_indices = {}
        for key, aliases in column_aliases.items():
            for alias in aliases:
                if alias in headers:
                    column_indices[key] = headers.index(alias)
                    break

        # Process table rows
        rows = table.find_all("tr")[1:]  # Skip the header row
        for row in rows:
            cells = row.find_all("td")
            #if len(cells) < len(column_indices):
            #    print(cells)
            #    continue

            row_data = {}
            for key, index in column_indices.items():
                cell_html = str(cells[index])
                cell_text = BeautifulSoup(cell_html, "html.parser").text.strip()

                if key == "image":
                    row_data["image"] = extract_image(cell_html)
                elif key == "coordinates":
                    row_data["coordinates"] = extract_coordinates(cell_html)
                elif key == "inscription":
                    row_data["inscription"] = process_inscription(cell_text)
                elif key == "person_info":
                    row_data["person_info"] = process_person_info(cell_text)
                else:
                    row_data[key] = cell_text

            row_data["table_name"] = table_name
            data.append(row_data)
    

    return data


# Helper function to extract coordinates
def extract_coordinates(cell):
    coord_pattern = re.compile(r"\{\{Coordinate\|.*?\|NS=([\d\.]+)\|EW=([\d\.]+)")
    match = coord_pattern.search(cell)
    if match:
        return {
            "latitude": float(match.group(1)),
            "longitude": float(match.group(2)),
        }
    return None


# Helper function to extract image filename
def extract_image(cell):
    match = re.search(r"Datei:(.*?)(\||\]\])", cell)
    if match:
        return unquote(match.group(1))
    return None


# Helper function to process inscription text
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


# Helper function to process person info
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


if __name__ == "__main__":
    list_name = "Liste_der_Stolpersteine_in_Pasewalk"
    column_aliases = {
        "image": ["Stolperstein"],
        "inscription": ["Inschrift"],
        "location": ["Verlegeort", "Adresse"],
        "person_info": ["Name, Leben", "Person"],
        "coordinates": ["Verlegeort"],
    }

    try:
        stolpersteine_data = fetch_stolpersteine_data(list_name, column_aliases)

        # Save the data to a JSON file
        output_file = f"stolpersteine_{list_name.replace(' ', '_')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stolpersteine_data, f, ensure_ascii=False, indent=4)

        print(
            f"Extracted {len(stolpersteine_data)} entries. Data saved to {output_file}."
        )
    except Exception as e:
        print(f"Error: {e}")
