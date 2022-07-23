import unittest

from utils.conversion import convert_input


class TestTime(unittest.TestCase):
    def test_convert_input(self) -> None:
        # some common measurements
        self.assertEqual(convert_input("2 miles"), "`2.0 miles` is equal to `3.22 km`.")
        self.assertEqual(convert_input("4c"), "`4.0°C` is equal to `39.2°F`.")
        self.assertEqual(
            convert_input("70 mph"), "`70.0 mph` is equal to `112.65 km/h (31.29 m/s)`."
        )

        # some measurements with special chars
        self.assertEqual(convert_input("1.6 km"), "`1.6 km` is equal to `0.99 miles`.")
        self.assertEqual(
            convert_input("-4 kilogram"), "`-4.0 kg` is equal to `-8.82 lbs`."
        )
        self.assertEqual(convert_input("+4l"), "`4.0 l` is equal to `1.06 gal`.")

        # some dumb measurements
        self.assertEqual(
            convert_input("-0.9999999999999999999999999999999999999999 cm"),
            "`-1.0 cm` is equal to `-0.39 inches`.",
        )
        self.assertEqual(
            convert_input("6 feet 5 inches"), "`6.0 feet` is equal to `1.83 m`."
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
