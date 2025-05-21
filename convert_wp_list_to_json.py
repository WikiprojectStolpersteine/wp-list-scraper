import requests
from bs4 import BeautifulSoup
import json
import argparse

from coordinates import extract_coordinates
from image import extract_image
from inscription import process_inscription
from person import process_person_info


def fetch_stolpersteine_data(url, list_name, column_aliases):
    print(f"Fetching data from: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(
            f"Failed to fetch the page. Status code: {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    if not tables:
        raise ValueError("No tables found on the page.")
    
    data = []

    for table in tables:
        header = table.find_previous("h2")
        table_name = header.text.strip() if header else list_name
        print(f"Processing table: {table_name}")
        if table_name == "Einzelnachweise":
            print("Skipping a table called: Einzelnachweise")
            continue

        headers = [th.text.strip() for th in table.find_all("th")]
        print("Headers found: " + str(headers))

        column_indices = {}
        for key, aliases in column_aliases.items():
            for alias in aliases:
                if alias in headers:
                    column_indices[key] = headers.index(alias)
                    break

        rows = table.find_all("tr")[1:]  # Skip header
        for row in rows:
            cells = row.find_all("td")

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


if __name__ == "__main__":
    default_list_name = "Liste_der_Stolpersteine_in_Pasewalk"
    default_url = f"https://de.wikipedia.org/wiki/{default_list_name}"

    parser = argparse.ArgumentParser(
        description="Fetch Stolpersteine data from a Wikipedia list"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Full URL of the Wikipedia list page (optional). If not provided, Pasewalk list is used.",
    )

    args = parser.parse_args()
    url = args.url if args.url else default_url
    list_name = url.split("/")[-1]

    column_aliases = {
        "image": ["Stolperstein"],
        "inscription": ["Inschrift"],
        "location": ["Verlegeort", "Adresse"],
        "person_info": ["Name, Leben", "Person"],
        "coordinates": ["Verlegeort"],
    }

    try:
        stolpersteine_data = fetch_stolpersteine_data(url, list_name, column_aliases)

        output_file = f"lists/stolpersteine_{list_name.replace(' ', '_')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stolpersteine_data, f, ensure_ascii=False, indent=4)

        print(
            f"Extracted {len(stolpersteine_data)} entries. Data saved to {output_file}."
        )
    except Exception as e:
        print(f"Error: {e}")
