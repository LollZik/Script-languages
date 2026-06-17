from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Stop(Base):
    __tablename__ = 'stops'

    stop_id: Mapped[str] = mapped_column(String, primary_key=True)
    stop_code: Mapped[Optional[str]] = mapped_column(String)
    stop_name: Mapped[str] = mapped_column(String, nullable=False)
    stop_lat: Mapped[float] = mapped_column(Float, nullable=False)
    stop_lon: Mapped[float] = mapped_column(Float, nullable=False)

    stop_times: Mapped[List["StopTime"]] = relationship(back_populates="stop")


class Route(Base):
    __tablename__ = 'routes'

    route_id: Mapped[str] = mapped_column(String, primary_key=True)
    agency_id: Mapped[Optional[int]] = mapped_column(Integer)
    route_short_name: Mapped[str] = mapped_column(String, nullable=False)
    route_long_name: Mapped[Optional[str]] = mapped_column(String)
    route_desc: Mapped[Optional[str]] = mapped_column(String)
    route_type: Mapped[Optional[int]] = mapped_column(Integer)
    route_type2_id: Mapped[Optional[int]] = mapped_column(Integer)
    valid_from: Mapped[Optional[str]] = mapped_column(String)
    valid_until: Mapped[Optional[str]] = mapped_column(String)

    trips: Mapped[List["Trip"]] = relationship(back_populates="route")


class Calendar(Base):
    __tablename__ = 'calendar'

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    monday: Mapped[int] = mapped_column(Integer, nullable=False)
    tuesday: Mapped[int] = mapped_column(Integer, nullable=False)
    wednesday: Mapped[int] = mapped_column(Integer, nullable=False)
    thursday: Mapped[int] = mapped_column(Integer, nullable=False)
    friday: Mapped[int] = mapped_column(Integer, nullable=False)
    saturday: Mapped[int] = mapped_column(Integer, nullable=False)
    sunday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[str] = mapped_column(String, nullable=False)
    end_date: Mapped[str] = mapped_column(String, nullable=False)

    trips: Mapped[List["Trip"]] = relationship(back_populates="calendar")


class Trip(Base):
    __tablename__ = 'trips'

    trip_id: Mapped[str] = mapped_column(String, primary_key=True)
    route_id: Mapped[str] = mapped_column(String, ForeignKey('routes.route_id'), nullable=False)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey('calendar.service_id'), nullable=False)
    trip_headsign: Mapped[Optional[str]] = mapped_column(String)
    direction_id: Mapped[Optional[int]] = mapped_column(Integer)
    shape_id: Mapped[Optional[str]] = mapped_column(String)
    brigade_id: Mapped[Optional[int]] = mapped_column(Integer)

    route: Mapped["Route"] = relationship(back_populates="trips")
    calendar: Mapped["Calendar"] = relationship(back_populates="trips")
    stop_times: Mapped[List["StopTime"]] = relationship(back_populates="trip")


class StopTime(Base):
    __tablename__ = 'stop_times'

    trip_id: Mapped[str] = mapped_column(String, ForeignKey('trips.trip_id'), primary_key=True)
    stop_sequence: Mapped[int] = mapped_column(Integer, primary_key=True)

    arrival_time: Mapped[str] = mapped_column(String, nullable=False)
    departure_time: Mapped[str] = mapped_column(String, nullable=False)
    stop_id: Mapped[str] = mapped_column(String, ForeignKey('stops.stop_id'), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="stop_times")
    stop: Mapped["Stop"] = relationship(back_populates="stop_times")