import unittest
from utils.conversion import convert_input


class TestTime(unittest.TestCase):
    def test_convert_input(self):
        # some common measurements
        self.assertEqual(convert_input("2 miles"), "`2.0 miles` is equal to `3.22 km`.")
        self.assertEqual(convert_input("1.6 km"), "`1.6 km` is equal to `0.99 miles`.")
        self.assertEqual(convert_input("4c"), "`4.0°C` is equal to `39.2°F`.")
        self.assertEqual(
            convert_input("70 mph"), "`70.0 mph` is equal to `112.65 km/h (31.29 m/s)`."
        )

        # some errors
        self.assertEqual(
            convert_input("5 whatevers"),
            "Invalid input! Please specify a valid measurement.",
        )
        with self.assertRaises(IndexError):
            convert_input("f")


if __name__ == "__main__":
    unittest.main()
