import os
import random
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple

AIRPORTS = [
    "GRU",
    "GIG",
    "BSB",
    "CGH",
    "SDU",
    "VCP",
    "POA",
    "SSA",
    "FOR",
    "REC",
]

AIRLINES = [
    "Azul",
    "Gol",
    "LATAM",
    "Passaredo",
    "Itapemirim",
    "Voepass",
]

STATUSES = [
    "Scheduled",
    "Boarding",
    "Departed",
    "Arrived",
    "Cancelled",
    "Delayed",
]


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS flights (
    flight_id INTEGER PRIMARY KEY,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival DATE NOT NULL,
    arrival_time TIME NOT NULL,
    airline TEXT NOT NULL,
    status TEXT NOT NULL,
    aircraft TEXT NOT NULL,
    distance_km INTEGER NOT NULL,
    passengers INTEGER NOT NULL
);
"""


INSERT_SQL = """
INSERT INTO flights (
    flight_id,
    origin,
    destination,
    departure,
    departure_time,
    arrival,
    arrival_time,
    airline,
    status,
    aircraft,
    distance_km,
    passengers
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def get_connection(database_path: str) -> sqlite3.Connection:
    return sqlite3.connect(database_path)


def init_database(database_path: str, *, rows: int = 10_000) -> None:
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM flights")
        current_rows = cursor.fetchone()[0]
        if current_rows >= rows:
            return

        cursor.execute("DELETE FROM flights")
        connection.commit()

        seed_data = _generate_seed_data(rows)
        cursor.executemany(INSERT_SQL, seed_data)
        connection.commit()
    finally:
        connection.close()


def list_tables(database_path: str) -> List[str]:
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        connection.close()


def describe_table(database_path: str, table_name: str) -> List[Tuple[str, str]]:
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [(row[1], row[2]) for row in cursor.fetchall()]
    finally:
        connection.close()


def _generate_seed_data(rows: int) -> List[Tuple]:
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data: List[Tuple] = []
    for flight_id in range(1, rows + 1):
        origin, destination = random.sample(AIRPORTS, 2)
        departure_offset_days = random.randint(-30, 30)
        departure_date = base_date + timedelta(days=departure_offset_days)
        departure_time = (datetime.min + timedelta(minutes=random.randint(0, 23 * 60 + 59))).time()
        flight_duration = timedelta(minutes=random.randint(60, 240))
        arrival_date_time = datetime.combine(departure_date, departure_time) + flight_duration
        arrival_date = arrival_date_time.date()
        arrival_time = arrival_date_time.time()
        airline = random.choice(AIRLINES)
        status = random.choices(STATUSES, weights=[25, 10, 25, 20, 5, 15])[0]
        aircraft = f"{random.choice(['A', 'B', 'E'])}{random.randint(100, 999)}"
        distance_km = random.randint(200, 3500)
        passengers = random.randint(50, 250)

        data.append(
            (
                flight_id,
                origin,
                destination,
                departure_date.strftime("%Y-%m-%d"),
                departure_time.strftime("%H:%M:%S"),
                arrival_date.strftime("%Y-%m-%d"),
                arrival_time.strftime("%H:%M:%S"),
                airline,
                status,
                aircraft,
                distance_km,
                passengers,
            )
        )
    return data

