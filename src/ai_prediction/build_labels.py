
import argparse
import csv
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from contextlib import closing

from src.ai_prediction.grid import get_grid_cell


DEFAULT_DATA = Path("wildfire-datasets/FPA_FOD_20260615.gpkg")


def build_labels(data_path, start_date, end_date, latitude, longitude):
    # Get the 10 km grid cell for our selected location
    selected_cell = get_grid_cell(latitude, longitude)

    fire_counts = defaultdict(int)

    # Open the historical wildfire dataset
    with closing(sqlite3.connect(str(data_path))) as connection:
        cursor = connection.execute(
            """
            SELECT DISCOVERY_DATE, LATITUDE, LONGITUDE
            FROM Fires
            WHERE DISCOVERY_DATE >= ?
              AND DISCOVERY_DATE < ?
            """,
            (
                start_date.isoformat(),
                (end_date + timedelta(days=1)).isoformat()
            )
        )

        for discovery_date, fire_lat, fire_lon in cursor:
            if fire_lat is None or fire_lon is None:
                continue

            # Preserve the original discovery calendar date
            fire_date = date.fromisoformat(discovery_date[:10])

            cell = get_grid_cell(fire_lat, fire_lon)

            if cell == selected_cell:
                fire_counts[fire_date] += 1

    # Generate a record for every date
    rows = []
    current_date = start_date

    while current_date <= end_date:
        count = fire_counts[current_date]

        rows.append({
            "grid_cell": selected_cell,
            "date": current_date.isoformat(),
            "fire_count": count,
            "fire_label": int(count > 0)
        })

        current_date += timedelta(days=1)

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Generate wildfire occurrence labels"
    )

    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/ai/fire_labels.csv"))

    args = parser.parse_args()

    if not args.data.is_file():
        parser.error(f"Dataset not found: {args.data}")

    if args.start > args.end:
        parser.error("Start date must be before or equal to end date")

    if not (-90 <= args.lat <= 90 and -180 <= args.lon <= 180):
        parser.error("Invalid latitude or longitude")

    rows = build_labels(
        args.data, args.start, args.end, args.lat, args.lon
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["grid_cell", "date", "fire_count", "fire_label"]
        )
        writer.writeheader()
        writer.writerows(rows)

    positives = sum(row["fire_label"] for row in rows)

    print(f"Grid cell: {rows[0]['grid_cell']}")
    print(f"Total cell-days: {len(rows)}")
    print(f"Positive days: {positives}")
    print(f"Negative days: {len(rows) - positives}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
