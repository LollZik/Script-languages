import csv


def parse_metadata(file_path):
    stations = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')

        for row in reader:
            station_data = {
                'nr': row.get('Nr'),
                'kodStacji': row.get('Kod stacji'),
                'kodMiedzynarodowy': row.get('Kod miedzynarodowy'),
                'staryKod': row.get('"Stary Kod stacji (o ile inny od aktualnego)"'),
                'dataUruchomienia': row.get('Data uruchomienia'),
                'dataZamkniecia': row.get('Data zamknięcia'),
                'typStacji': row.get('Typ stacji'),
                'typObszaru': row.get('Typ obszaru'),
                'rodzajStacji': row.get('Rodzaj stacji'),
                'wojewodztwo': row.get('Województwo'),
                'miasto': row.get('Miejscowość'),
                'adres': row.get('Adres'),
                'N': row.get('WGS84 φ N'),
                'E': row.get('WGS84 λ E')
            }
            stations.append(station_data)
    return stations


def parse_measurements(file_path):
    measurements = []

    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')

        header_nr = next(reader)
        header_kody_stacji = next(reader)
        header_wskazniki = next(reader)
        header_czas_sr = next(reader)
        header_jednostki = next(reader)
        header_kody_stanowisk = next(reader)

        for row in reader:
            if not row or len(row) < 2:
                continue

            czas = row[0]

            for i in range(1, len(row)):
                stacja = header_kody_stacji[i]
                wielkosc = header_wskazniki[i]

                if row[i] != '':
                    wartosc = float(row[i].strip())
                else:
                    wartosc = None

                measurements.append((czas, wartosc, stacja, wielkosc))

    return measurements


def main():
    pomiary = parse_measurements('measurements/2023_PM10_1g.csv')
    for a in pomiary:
        print(a)
    #data_stacji = parse_metadata('stacje.csv')
    #for stacja in data_stacji:
    #    print(stacja)

if __name__ == "__main__":
    main()