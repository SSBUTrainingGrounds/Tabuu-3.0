import datetime
import re
from zoneinfo import ZoneInfo


def convert_to_utc(dtime: datetime.time, tz: str) -> datetime.time:
    """
    Converts the time from a given timezone to the UTC time.
    We have to use this since timed tasks for some reason do not work with tzinfo.
    I don't know why since the docs say it should work but it just straight up does not work.
    That's why we have to do ourselves.
    """
    offset = datetime.datetime.now(ZoneInfo(tz)).utcoffset()
    temp_dtime = datetime.datetime.combine(datetime.datetime.now(ZoneInfo(tz)), dtime)
    return (temp_dtime - offset).time()


def append_readable_time(readable_time: str, time: int, duration: str) -> str:
    """
    Appends to the readable_time string with the specified time and duration.
    """

    # if the string is empty
    if readable_time:
        # checks if its just one or multiple for proper wording
        # luckily the -s ending works out for every case
        return (
            f"{readable_time}, {time} {duration}"
            if time == 1
            else f"{readable_time}, {time} {duration}s"
        )

    return f"{time} {duration}" if time == 1 else f"{time} {duration}s"


def convert_time(input_time: str) -> tuple[int, str]:
    """
    Converts the given input into raw seconds, plus a readable string.
    Searches for matches using regex with commonly used names and abbreviations.
    Input does need to be in order.
    """

    # matching the input into the appropriate group
    compiled = re.compile(
        r"(\s?)(?:(?P<days>[0-9]{1,5})(\s?)(?:days?|d))?(\s?(,|and)?)"
        r"(\s?)(?:(?P<hours>[0-9]{1,5})(\s?)(?:hours?|hrs?|h))?(\s?(,|and)?)"
        r"(\s?)(?:(?P<minutes>[0-9]{1,5})(\s?)(?:minutes?|mins?|m))?(\s?(,|and)?)"
        r"(\s?)(?:(?P<seconds>[0-9]{1,5})(\s?)(?:seconds?|secs?|s))?(\s?(,|and)?)",
        re.VERBOSE,
    )

    total_seconds = 0
    readable_time = ""

    match = compiled.fullmatch(input_time)

    # if no match is found, we raise a ValueError
    if not match:
        raise ValueError("Invalid input! Please use a number followed by a duration.")

    # getting a dict of the match
    time_dict = match.groupdict(default="0")

    # extracting the values for each entry
    # checks if the user hasnt entered anything for the value,
    # or if they entered "0" manually.
    days = time_dict.get("days")
    if days != "0":
        total_seconds += int(days) * 60 * 60 * 24
        readable_time = append_readable_time(readable_time, int(days), "day")

    hours = time_dict.get("hours")
    if hours != "0":
        total_seconds += int(hours) * 60 * 60
        readable_time = append_readable_time(readable_time, int(hours), "hour")

    minutes = time_dict.get("minutes")
    if minutes != "0":
        total_seconds += int(minutes) * 60
        readable_time = append_readable_time(readable_time, int(minutes), "minute")

    seconds = time_dict.get("seconds")
    if seconds != "0":
        total_seconds += int(seconds)
        readable_time = append_readable_time(readable_time, int(seconds), "second")

    return total_seconds, readable_time
