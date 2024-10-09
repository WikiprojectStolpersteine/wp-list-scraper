import requests
import csv

# Define the URL of the MediaWiki API endpoint
API_URL = "https://de.wikipedia.org/w/api.php"

def get_category_members(category, cmcontinue=None):
    """Get members of a specified Wikipedia category."""
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "max",
        "format": "json",
    }
    if cmcontinue:
        params["cmcontinue"] = cmcontinue

    response = requests.get(API_URL, params=params)
    data = response.json()
    members = data.get("query", {}).get("categorymembers", [])
    next_continue = data.get("continue", {}).get("cmcontinue")

    return members, next_continue

def get_all_category_lists(category):
    """Recursively get all pages from a Wikipedia category and its subcategories."""
    all_pages = []
    pages, cmcontinue = get_category_members(category)
    all_pages.extend(pages)

    while cmcontinue:
        pages, cmcontinue = get_category_members(category, cmcontinue)
        all_pages.extend(pages)

    return all_pages

def save_to_csv(pages, filename="wikipedia_lists.csv"):
    """Save the list of pages to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Page ID", "Title", "Page URL"])
        for page in pages:
            page_id = page.get("pageid")
            title = page.get("title")
            page_url = f"https://de.wikipedia.org/wiki/{title.replace(' ', '_')}"
            writer.writerow([page_id, title, page_url])

def main():
    category = "Kategorie:Liste_(Stolpersteine)"
    all_pages = get_all_category_lists(category)
    save_to_csv(all_pages)
    print(f"Saved {len(all_pages)} pages to CSV.")

if __name__ == "__main__":
    main()
