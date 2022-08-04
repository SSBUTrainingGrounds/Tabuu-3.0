import pytest

from utils.conversion import convert_input


def test_convert_input() -> None:
    # some common measurements
    assert convert_input("2 miles") == "`2.0 miles` is equal to `3.22 km`."
    assert convert_input("4c") == "`4.0°C` is equal to `39.2°F`."
    assert (
        convert_input("70 mph") == "`70.0 mph` is equal to `112.65 km/h (31.29 m/s)`."
    )

    # some measurements with special chars
    assert convert_input("1.6 km") == "`1.6 km` is equal to `0.99 miles`."
    assert convert_input("-4 kilogram") == "`-4.0 kg` is equal to `-8.82 lbs`."
    assert convert_input("+4l") == "`4.0 l` is equal to `1.06 gal`."

    # some dumb measurements
    assert (
        convert_input("-0.9999999999999999999999999999999999999999 cm")
        == "`-1.0 cm` is equal to `-0.39 inches`."
    )

    assert convert_input("6 feet 5 inches") == "`6.0 feet` is equal to `1.83 m`."

    # some errors
    assert (
        convert_input("5 whatevers")
        == "Invalid input! Please specify a valid measurement."
    )
    with pytest.raises(IndexError):
        convert_input("f")
