import re
from pathlib import Path
from parseFiles import parse_metadata


def extract_dates(station):
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
    dates = []
    for key in ['dataUruchomienia', 'dataZamkniecia']:
        if station.get(key):
            matches = re.findall(date_pattern, station[key])
            dates.extend(matches)
    return dates


def extract_coordinates(station):
    coord_pattern = r'\b\d+\.\d{6}\b'
    coords = []
    for key in ['N', 'E']:
        if station.get(key):
            matches = re.findall(coord_pattern, station[key])
            coords.extend(matches)
    return coords


def get_two_part_names(station_name):
    if station_name and re.match(r'^[^-\n]+-[^-\n]+$', station_name):
        return station_name
    return None


def format_station_name(station_name):
    if not station_name:
        return ""

    pl_to_en = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }

    name_no_spaces = re.sub(r'\s+', '_', station_name)
    name_formatted = re.sub(
        r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]',
        lambda m: pl_to_en[m.group(0)],
        name_no_spaces
    )
    return name_formatted


def verify_mob_station(station):
    station_code = station.get('kodStacji')
    station_type = station.get('rodzajStacji')

    if re.search(r'MOB$', station_code):
        return station_type.strip().lower() == 'mobilna'
    return True


def get_three_part_locations(location_string):
    if location_string and re.match(r'^[^-\n]+-[^-\n]+-[^-\n]+$', location_string):
        return location_string
    return None


def get_comma_street_locations(location_string):
    if location_string and re.search(r'(?=.*,)(?=.*\b(ul\.|al\.))', location_string):
        return location_string
    return None


def process_stations(file_path: Path):
    results = {
        "dates": [],
        "coordinates": [],
        "two_part_names": [],
        "formatted_names": [],
        "mob_verification": True,
        "three_part_locations": [],
        "comma_street_locations": []
    }

    try:
        stations_data = parse_metadata(file_path)

        for station in stations_data:
            station_name = station.get('miasto', '')
            location = station.get('adres', '')

            results["dates"].extend(extract_dates(station))
            results["coordinates"].extend(extract_coordinates(station))

            two_part = get_two_part_names(station_name)
            if two_part:
                results["two_part_names"].append(two_part)

            formatted = format_station_name(station_name)
            if formatted:
                results["formatted_names"].append(formatted)

            if not verify_mob_station(station):
                results["mob_verification"] = False

            three_part = get_three_part_locations(location)
            if three_part:
                results["three_part_locations"].append(three_part)

            comma_street = get_comma_street_locations(location)
            if comma_street:
                results["comma_street_locations"].append(comma_street)

    except FileNotFoundError:
        pass

    return results


def main():
    file_path = Path('./stacje.csv')
    parsed_data = process_stations(file_path)

    for key, value in parsed_data.items():
        if isinstance(value, list):
            print(f"{key}: {len(value)} items found")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()