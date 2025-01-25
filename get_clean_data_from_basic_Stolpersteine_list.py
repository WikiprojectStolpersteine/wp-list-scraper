import requests
from bs4 import BeautifulSoup
import re
import json
import sys


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
        row_data = [cell.text.strip() for cell in td]
        if row_data:
            rows.append(row_data)
    # {{Coordinate|simple=y|text=ICON2|NS=53.503889|EW=13.991667|type=landmark|region=DE-MV|name=Stolpersteine für Benno Schlochauer, Lina Schlochauer, Siegbert Schlochauer, Jacob Steinberg, Max Steinberg, Gertrud Zobel und Max Zobel}}
    # Helper function to extract coordinates from template
    coord_pattern = re.compile(r"Coordinate\|simple=y\|NS=([\d\.]+)\|EW=([\d\.]+)")

    def extract_coordinates(cell):
        match = coord_pattern.search(cell)
        if match:
            return {
                "latitude": float(match.group(1)),
                "longitude": float(match.group(2)),
            }
        return None

    # Process rows into structured data
    data = []
    for row in rows:
        if len(row) >= 4:  # Ensure sufficient columns exist
            stolperstein_data = {
                "image": None,  # Image extraction can be added if needed
                "inscription": row[1],
                "location": row[2],
                "person_info": row[3],
                "coordinates": extract_coordinates(row[2]),
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
