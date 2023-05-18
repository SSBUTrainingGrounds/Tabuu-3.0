import datetime
from math import ceil
from zoneinfo import ZoneInfo

from dateparser import parse

from utils.ids import TournamentReminders


def convert_to_utc(dtime: datetime.time, tz: str) -> datetime.time:
    """Converts the time from a given timezone to the UTC time.
    We have to use this since timed tasks for some reason do not work with tzinfo.
    I don't know why since the docs say it should work but it just does not work for me.
    That's why we have to do ourselves.
    """
    offset = datetime.datetime.now(ZoneInfo(tz)).utcoffset()
    temp_dtime = datetime.datetime.combine(datetime.datetime.now(ZoneInfo(tz)), dtime)
    return (temp_dtime - offset).time() if offset else temp_dtime.time()


def convert_time(input_time: str) -> tuple[int, str]:
    """Converts the given input into raw seconds, plus a readable string."""

    dt = parse(
        input_time,
        settings={
            "PREFER_DAY_OF_MONTH": "first",
            "PREFER_DATES_FROM": "future",
            "TIMEZONE": TournamentReminders.TIMEZONE,
            "RETURN_AS_TIMEZONE_AWARE": True,
            # We want the relative time to be parsed first, since it's the most common one.
            # Also there would be false positives with "1h" being parsed as 1:00am for example.
            "PARSERS": [
                "relative-time",
                "timestamp",
                "custom-formats",
                "absolute-time",
                "no-spaces-time",
            ],
        },
    )

    if dt:
        delta = ceil(dt.timestamp() - datetime.datetime.now().timestamp())

        return (delta, str(datetime.timedelta(seconds=delta)))

    return None, None
