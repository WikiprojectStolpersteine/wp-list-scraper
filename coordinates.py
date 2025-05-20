import re


def extract_coordinates(cell):
    coord_pattern = re.compile(r"\{\{Coordinate\|.*?\|NS=([\d\.]+)\|EW=([\d\.]+)")
    match = coord_pattern.search(cell)
    if match:
        return {
            "latitude": float(match.group(1)),
            "longitude": float(match.group(2)),
        }
    return None