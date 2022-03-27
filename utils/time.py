import datetime
import re
from zoneinfo import ZoneInfo


def convert_to_utc(dtime: datetime.time, tz: str):
    """
    Converts the time from a given timezone to the UTC time.
    We have to use this since timed tasks for some reason do not work with tzinfo.
    I don't know why since the docs say it should work but it just straight up does not work.
    That's why we have to do ourselves.
    """
    offset = datetime.datetime.now(ZoneInfo(tz)).utcoffset()
    temp_dtime = datetime.datetime.combine(datetime.datetime.now(ZoneInfo(tz)), dtime)
    return (temp_dtime - offset).time()


def append_readable_time(readable_time: str, time: int, duration: str):
    """
    Appends to the readable_time string with the specified time and duration.
    """
    # if the string is empty
    if not readable_time:
        # checks if its just one or multiple for proper wording
        if int(time) == 1:
            # str(int(days)) looks stupid but it gets rid of leading zeroes. 00001d -> 1d
            readable_time = f"{str(int(time))} {duration}"
        # luckily the -s ending works out for every case
        else:
            readable_time = f"{str(int(time))} {duration}s"
    else:
        if int(time) == 1:
            readable_time = readable_time + f", {str(int(time))} {duration}"
        else:
            readable_time = readable_time + f", {str(int(time))} {duration}s"

    return readable_time


def convert_time(input_time: str):
    """
    Converts the given input into raw seconds, plus a readable string.
    Searches for matches using regex with commonly used names and abbreviations.
    Input does need to be in order.
    """

    # matching the input into the appropriate group
    compiled = re.compile(
        "(\s?)(?:(?P<days>[0-9]{1,5})(\s?)(?:days?|d))?(\s?,?)"
        "(\s?)(?:(?P<hours>[0-9]{1,5})(\s?)(?:hours?|h|hrs?))?(\s?,?)"
        "(\s?)(?:(?P<minutes>[0-9]{1,5})(\s?)(?:minutes?|m|mins?))?(\s?,?)"
        "(\s?)(?:(?P<seconds>[0-9]{1,5})(\s?)(?:seconds?|s|secs?))?(\s?,?)",
        re.VERBOSE,
    )

    total_seconds = 0
    readable_time = ""

    match = compiled.fullmatch(input_time)

    # if no match is found, we raise a ValueError
    if not match:
        raise ValueError("Invalid input! Please use a number followed by a duration.")

    # getting a dict of the match
    time_dict = match.groupdict()

    # extracting the values for each entry
    # checks if the values are None or "0"
    days = time_dict.get("days")
    if days and days != "0":
        total_seconds += int(days) * 60 * 60 * 24
        readable_time = append_readable_time(readable_time, int(days), "day")

    hours = time_dict.get("hours")
    if hours and hours != "0":
        total_seconds += int(hours) * 60 * 60
        readable_time = append_readable_time(readable_time, int(hours), "hour")

    minutes = time_dict.get("minutes")
    if minutes and minutes != "0":
        total_seconds += int(minutes) * 60
        readable_time = append_readable_time(readable_time, int(minutes), "minute")

    seconds = time_dict.get("seconds")
    if seconds and seconds != "0":
        total_seconds += int(seconds)
        readable_time = append_readable_time(readable_time, int(seconds), "second")

    return total_seconds, readable_time
