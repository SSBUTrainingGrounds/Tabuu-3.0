import datetime
from zoneinfo import ZoneInfo

from discord.ext import commands


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


def convert_time(input_time: str):
    """
    Converts the given input into raw seconds, plus a readable string.
    Searches for the letters d/h/m/s, gets the int before it, appends the seconds and the string and repeat.
    Order of these does not matter.
    Example:
        Input: 5h20m
        Output: 19200, "5 hours, 20 minutes"
    Triggers a CommandInvokeError on an invalid Input.
    """
    total_seconds = 0
    readable_time = ""

    current_position = 0
    for char in input_time:
        if char == "d":
            # only gets the input before the d
            days = input_time.split("d")[0][-current_position:]
            total_seconds += int(days) * 60 * 60 * 24
            # dont want negative numbers, just raising the error that also gets raised on a BadConversion
            if int(days) < 0:
                raise commands.CommandInvokeError
            # ignores zeroes in the returning string. if you input 0d20h it wont display the days in the string
            if int(days) > 0:
                if readable_time == "":
                    # checks if its just one or multiple for proper wording
                    if int(days) == 1:
                        # str(int(days)) looks stupid but it gets rid of leading zeroes. 00001d -> 1d
                        readable_time = f"{str(int(days))} day"
                    else:
                        readable_time = f"{str(int(days))} days"
                else:
                    if int(days) == 1:
                        readable_time = readable_time + f", {str(int(days))} day"
                    else:
                        readable_time = readable_time + f", {str(int(days))} days"
            # resets the counter for the other inputs
            current_position = 0

        # its the same for every other type
        elif char == "h":
            hours = input_time.split("h")[0][-current_position:]
            total_seconds += int(hours) * 60 * 60
            if int(hours) < 0:
                raise commands.CommandInvokeError
            if int(hours) > 0:
                if readable_time == "":
                    if int(hours) == 1:
                        readable_time = f"{str(int(hours))} hour"
                    else:
                        readable_time = f"{str(int(hours))} hours"
                else:
                    if int(hours) == 1:
                        readable_time = readable_time + f", {str(int(hours))} hour"
                    else:
                        readable_time = readable_time + f", {str(int(hours))} hours"
            current_position = 0

        elif char == "m":
            mins = input_time.split("m")[0][-current_position:]
            total_seconds += int(mins) * 60
            if int(mins) < 0:
                raise commands.CommandInvokeError
            if int(mins) > 0:
                if readable_time == "":
                    if int(mins) == 1:
                        readable_time = f"{str(int(mins))} minute"
                    else:
                        readable_time = f"{str(int(mins))} minutes"
                else:
                    if int(mins) == 1:
                        readable_time = readable_time + f", {str(int(mins))} minute"
                    else:
                        readable_time = readable_time + f", {str(int(mins))} minutes"
            current_position = 0

        elif char == "s":
            secs = input_time.split("s")[0][-current_position:]
            total_seconds += int(secs)
            if int(secs) < 0:
                raise commands.CommandInvokeError
            if int(secs) > 0:
                if readable_time == "":
                    if int(secs) == 1:
                        readable_time = f"{str(int(secs))} second"
                    else:
                        readable_time = f"{str(int(secs))} seconds"
                else:
                    if int(secs) == 1:
                        readable_time = readable_time + f", {str(int(secs))} second"
                    else:
                        readable_time = readable_time + f", {str(int(secs))} seconds"
            current_position = 0

        else:
            current_position += 1

    # if the last char in the string is not either d/h/m/s we will just throw an error.
    # eg: good input: 1h49m, bad input: 1h20
    if current_position != 0:
        raise commands.CommandInvokeError

    return total_seconds, readable_time
