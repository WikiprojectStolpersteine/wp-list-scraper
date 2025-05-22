import pytest

from convert_wp_list_to_json import fetch_stolpersteine_data_wikitext

# Aliases used across all tested lists
column_aliases = {
    "image": ["Stolperstein"],
    "inscription": ["Inschrift"],
    "location": ["Verlegeort", "Adresse"],
    "person_info": ["Name, Leben", "Person"],
    "coordinates": ["Verlegeort"],
}


@pytest.mark.parametrize(
    "list_name",
    [
        "Liste_der_Stolpersteine_in_Pasewalk",  # basic format with templates
        "Liste der Stolpersteine in Krefeld",  # Tables are people
        "Liste der Stolpersteine in der Stadt Salzburg",  # Larger lists with multiple city parts
        "Liste der Stolpersteine in Duderstadt",  # Nested data, multi-row
    ],
)
def test_extraction_works_for_list(list_name):
    data = fetch_stolpersteine_data_wikitext(list_name, column_aliases)

    assert isinstance(data, list)
    assert len(data) > 0, f"No rows parsed for {list_name}"

    for row in data:
        assert "table_name" in row
        assert "person_info" in row
        assert isinstance(row["person_info"], dict)
        assert "name" in row["person_info"]

        if "inscription" in row:
            assert isinstance(row["inscription"], dict)
            assert "text" in row["inscription"]

        if "location" in row:
            assert isinstance(row["location"], str)

        if "coordinates" in row and row["coordinates"] is not None:
            assert "latitude" in row["coordinates"]
            assert "longitude" in row["coordinates"]
