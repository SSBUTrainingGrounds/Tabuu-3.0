from datetime import time, datetime
import unittest
from zoneinfo import ZoneInfo

from utils.time import convert_time, convert_to_utc


class TestTime(unittest.TestCase):
    def test_convert_time(self):
        # common use
        self.assertEqual(convert_time("3h"), (10800, "3 hours"))
        # bit more special
        self.assertEqual(
            convert_time("0d20h5m1s"), (72301, "20 hours, 5 minutes, 1 second")
        )
        self.assertEqual(convert_time("3days0hrs30sec"), (259230, "3 days, 30 seconds"))

        # some error checking
        with self.assertRaises(ValueError):
            convert_time("-1d")

        with self.assertRaises(ValueError):
            convert_time("whatever invalid string here")

    def test_convert_to_utc(self):
        # checking for some timezones with DST within the same day
        timezones = ["Europe/Berlin", "US/Eastern", "Pacific/Auckland"]
        expected_times = [1, -5, 12]

        for zone, offset in zip(timezones, expected_times):
            if ZoneInfo(zone).dst(datetime.now()):
                offset = offset + 1
            self.assertEqual(
                convert_to_utc(time(14, 0, 0, 0), zone),
                time((14 - offset), 0, 0, 0),
            )

        # checking for rollback times
        # tokyo does not observe DST
        self.assertEqual(
            convert_to_utc(time(2, 0, 0, 0), "Asia/Tokyo"), time(17, 0, 0, 0)
        )


if __name__ == "__main__":
    unittest.main()
