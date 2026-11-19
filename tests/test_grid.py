
import unittest

from src.ai_prediction.grid import get_grid_cell


class TestGrid(unittest.TestCase):

    def test_same_location(self):
        # Same coordinates should always return the same cell
        cell1 = get_grid_cell(34.0522, -118.2437)
        cell2 = get_grid_cell(34.0522, -118.2437)

        self.assertEqual(cell1, cell2)

    def test_expected_cells(self):
        # Check against our initial LA coordinate results
        downtown = get_grid_cell(34.0522, -118.2437)
        beverly_hills = get_grid_cell(34.0736, -118.4004)

        self.assertEqual(downtown, "-202_145")
        self.assertEqual(beverly_hills, "-204_146")

    def test_different_locations(self):
        # Two known locations should map to different cells
        downtown = get_grid_cell(34.0522, -118.2437)
        beverly_hills = get_grid_cell(34.0736, -118.4004)

        self.assertNotEqual(downtown, beverly_hills)


if __name__ == "__main__":
    unittest.main()
