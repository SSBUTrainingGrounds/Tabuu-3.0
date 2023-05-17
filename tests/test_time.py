from datetime import datetime, time
from zoneinfo import ZoneInfo

from utils.time import convert_time, convert_to_utc


def test_convert_time() -> None:
    # Common use
    assert convert_time("3h") == (10800, "3:00:00")
    # Bit more special
    assert convert_time("0d20h5m1s") == (72301, "20:05:01")

    # With regex
    assert convert_time("3days0hrs30sec") == (259230, "3 days, 0:00:30")
    # With the ignored spaces and commas
    assert convert_time("3days 0 hrs, 30sec"), (259230, "3 days, 0:00:30")  # type: ignore
    assert convert_time(" 30 d , 20 hr 1 minutes, 20secs") == (
        2664080,
        "30 days, 20:01:20",
    )
    assert convert_time("30 days and 20 hrs and 1 m and 20 second") == (
        2664080,
        "30 days, 20:01:20",
    )

    assert convert_time("00001m") == (60, "0:01:00")


def test_convert_to_utc() -> None:
    # Checking for some timezones with DST within the same day.
    timezones = ["Europe/Berlin", "US/Eastern", "Pacific/Auckland"]
    expected_times = [1, -5, 12]

    for zone, offset in zip(timezones, expected_times):
        if ZoneInfo(zone).dst(datetime.now(ZoneInfo(zone))):
            offset = offset + 1

        assert convert_to_utc(time(14, 0, 0, 0), zone) == time((14 - offset), 0, 0, 0)

    # Checking for rollback times.
    # Tokyo does not observe DST.
    assert convert_to_utc(time(2, 0, 0, 0), "Asia/Tokyo") == time(17, 0, 0, 0)
