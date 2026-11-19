
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from contextlib import closing

from src.ai_prediction.build_labels import build_labels


class TestBuildLabels(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "test.gpkg"

        with closing(sqlite3.connect(self.data_path)) as connection:
            connection.execute("""
                CREATE TABLE Fires (
                    DISCOVERY_DATE TEXT,
                    LATITUDE REAL,
                    LONGITUDE REAL
                )
            """)

            # Two fires in the same cell on June 28
            connection.executemany(
                "INSERT INTO Fires VALUES (?, ?, ?)",
                [
                    ("2004-06-28T00:00:00.0Z", 38.559167, -119.913333),
                    ("2004-06-28T00:00:00.0Z", 38.559167, -119.933056),
                    ("2004-06-28T00:00:00.0Z", 34.0522, -118.2437)
                ]
            )

            connection.commit() # Save our test records before closing the connection


    def tearDown(self):
        self.temp_dir.cleanup()

    def test_positive_and_negative_days(self):
        rows = build_labels(
            self.data_path,
            date(2004, 6, 27),
            date(2004, 6, 29),
            38.559167,
            -119.913333
        )

        self.assertEqual(len(rows), 3)
        self.assertEqual(
            [row["fire_label"] for row in rows],
            [0, 1, 0]
        )

    def test_multiple_fires_one_day(self):
        rows = build_labels(
            self.data_path,
            date(2004, 6, 27),
            date(2004, 6, 29),
            38.559167,
            -119.913333
        )

        self.assertEqual(rows[1]["fire_count"], 2)

    def test_other_location_excluded(self):
        rows = build_labels(
            self.data_path,
            date(2004, 6, 28),
            date(2004, 6, 28),
            34.0522,
            -118.2437
        )

        self.assertEqual(rows[0]["fire_count"], 1)


if __name__ == "__main__":
    unittest.main()
