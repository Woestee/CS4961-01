
import math
from pyproj import Transformer

# Geographic coordinates (longitude, latitude) -> EPSG:5070 meters
transformer = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)

CELL_SIZE = 10000  # 10 km in meters


def get_grid_cell(latitude, longitude):
    # Convert latitude and longitude into projected x/y coordinates
    x, y = transformer.transform(longitude, latitude)

    # Divide coordinates into 10 km grid cells
    grid_x = math.floor(x / CELL_SIZE)
    grid_y = math.floor(y / CELL_SIZE)

    # Create a unique identifier for this grid cell
    cell_id = f"{grid_x}_{grid_y}"

    return cell_id


if __name__ == "__main__":
    # Test with two Los Angeles locations
    locations = [
        ("Downtown LA", 34.0522, -118.2437),
        ("Beverly Hills", 34.0736, -118.4004),
    ]

    for name, lat, lon in locations:
        cell = get_grid_cell(lat, lon)
        print(f"{name}: {cell}")
