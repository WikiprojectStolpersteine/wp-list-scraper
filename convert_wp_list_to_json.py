import requests
import json
import argparse
import wikitextparser as wtp

from coordinates import extract_coordinates
from image import extract_image
from inscription import process_inscription
from location import process_location
from person import process_person_info


def fetch_stolpersteine_data_wikitext(list_name, column_aliases):
    print(f"Fetching Wikitext for: {list_name}")
    
    response = requests.get(
        "https://de.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": list_name
        }
    )

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch the page. Status code: {response.status_code}")
    
    pages = response.json()["query"]["pages"]
    page_content = next(iter(pages.values()))["revisions"][0]["*"]

    parsed = wtp.parse(page_content)
    tables = parsed.tables
    sections = parsed.sections

    if not tables:
        raise ValueError("No tables found in the Wikitext.")

    data = []

    for table in tables:
        table_code = table.string
        section_title = find_section_title_for_table(sections, table_code)
        table_name = section_title or list_name
        if table_name == "Einzelnachweise":
            print("Skipping table 'Einzelnachweise'")
            continue

        print(f"Processing table: {table_name}")
        wikitable = wtp.parse(table_code).tables[0]
        headers = [h.strip() for h in wikitable.data()[0]]
        print("Headers found:", headers)

        column_indices = {}
        for key, aliases in column_aliases.items():
            for alias in aliases:
                if alias in headers:
                    column_indices[key] = headers.index(alias)
                    break

        for row in wikitable.data()[1:]:
            row_data = {}
            for key, index in column_indices.items():
                if index >= len(row):
                    continue
                cell = row[index].strip()

                if key == "image":
                    row_data["image"] = extract_image(cell)
                elif key == "coordinates":
                    row_data["coordinates"] = extract_coordinates(cell)
                elif key == "inscription":
                    row_data["inscription"] = process_inscription(cell)
                elif key == "person_info":
                    row_data["person_info"] = process_person_info(cell)
                elif key == "location":
                    row_data["location"] = process_location(cell)
                else:
                    row_data[key] = cell

            row_data["table_name"] = table_name
            data.append(row_data)

    return data


def find_section_title_for_table(sections, table_code):
    for section in sections:
        if table_code in section.string:
            return section.title.strip() if section.title else None
    return None


if __name__ == "__main__":
    default_list_name = "Liste_der_Stolpersteine_in_Pasewalk"

    parser = argparse.ArgumentParser(description="Fetch Stolpersteine data from a Wikipedia list using Wikitext")
    parser.add_argument(
        "--title",
        type=str,
        help="Wikipedia page title (e.g. Liste_der_Stolpersteine_in_Pasewalk). If not provided, default is used.",
    )

    args = parser.parse_args()
    list_name = args.title if args.title else default_list_name

    column_aliases = {
        "image": ["Stolperstein"],
        "inscription": ["Inschrift"],
        "location": ["Verlegeort", "Adresse"],
        "person_info": ["Name, Leben", "Person"],
        "coordinates": ["Verlegeort"],
    }

    try:
        stolpersteine_data = fetch_stolpersteine_data_wikitext(list_name, column_aliases)

        output_file = f"lists/stolpersteine_{list_name.replace(' ', '_')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stolpersteine_data, f, ensure_ascii=False, indent=4)

        print(f"Extracted {len(stolpersteine_data)} entries. Data saved to {output_file}.")
    except Exception as e:
        print(f"Error: {e}")
