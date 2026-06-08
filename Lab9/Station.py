class Station:
    def __init__(self, station_code: str, station_name: str = "", voivodeship: str = "", city: str = "", address: str = "") -> None:
        self.station_code = station_code
        self.station_name = station_name
        self.voivodeship = voivodeship
        self.city = city
        self.address = address

    def __str__(self) -> str:
        if self.station_name:
            return f"Stacja {self.station_name} (Kod: {self.station_code})"
        return f"Stacja pomiarowa (Kod: {self.station_code})"

    def __repr__(self) -> str:
        return (f"Station(station_code={self.station_code!r}, station_name={self.station_name!r}, "
                f"voivodeship={self.voivodeship!r}, city={self.city!r}, address={self.address!r})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Station):
            return NotImplemented
        return self.station_code == other.station_code


if __name__ == "__main__":
    stacja1 = Station(station_code="DzWroBarto", station_name="Wrocław - Bartnicza", voivodeship="Dolny Śląsk", city="Wrocław", address="ul. Traugutta")
    stacja2 = Station(station_code="DzWroBarto", station_name="Inna Nazwa")
    stacja3 = Station(station_code="DzWroKorze", station_name="Wrocław - Korzeniowskiego")

    print(str(stacja1))
    print(repr(stacja1))

    print(f"stacja1 == stacja2: {stacja1 == stacja2}")
    print(f"stacja1 == stacja3: {stacja1 == stacja3}")