import re


def convert_input(conversion_input: str) -> str:
    """Converts your input between metric and imperial, and the other way around.
    Works for most commonly used measurements for distance, speed, temperatures, weight and so on.
    Gets the first float in the input and looks for the first matching string, then converts the input.
    """
    # This block gets the first floating point number or normal int found.
    rx = re.compile(
        r"[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?",
        re.VERBOSE,
    )
    nums = rx.findall(conversion_input)
    number = float(nums[0])

    # This block here gets you all the words in the input in a list, to compare those to the lists below.
    conversion_input = conversion_input.lower()
    conversion_input = "".join(
        [i for i in conversion_input if not i.isdigit() and i not in ("+", "-", ".")]
    )
    conversion_input_list = conversion_input.split()

    # Massive dictionary of converting the input to the equivalent.
    conversion_dict = {
        ("miles", "mi", "mile"): Conversion().miles_to_km,
        ("foot", "feet", "ft", "'"): Conversion().feet_to_meter,
        ("inch", "in", '"', "inches"): Conversion().inches_to_cm,
        (
            "km",
            "kilometer",
            "kilometre",
            "kilometers",
            "kilometres",
            "kms",
        ): Conversion().km_to_miles,
        ("m", "meter", "metre", "meters", "meters"): Conversion().meter_to_feet,
        (
            "cm",
            "centimeter",
            "centimetre",
            "centimeters",
            "centimetres",
            "cms",
        ): Conversion().cm_to_inches,
        ("kmh", "kph", "km/h"): Conversion().kmh_to_mph,
        ("ms", "m/s", "mps"): Conversion().ms_to_mph,
        ("mph", "mi/h"): Conversion().mph_to_ms_kmh,
        ("f", "°f", "fahrenheit"): Conversion().f_to_c,
        ("c", "°c", "celsius"): Conversion().c_to_f,
        ("lbs", "pounds", "pound"): Conversion().lbs_to_kg,
        ("oz", "ounces", "ounce"): Conversion().oz_to_g,
        ("kg", "kilogram", "kilograms", "kilogrammes"): Conversion().kg_to_lbs,
        ("g", "gram", "grams", "grammes"): Conversion().g_to_oz,
        ("gallon", "gal", "gallons", "gl"): Conversion().gal_to_l,
        (
            "fluid ounce",
            "fluid ounces",
            "fl ounce",
            "fl ounces",
            "fl oz",
            "fluid oz",
            "fl. ounce",
            "fl. ounces",
            "fl. oz.",
            "fluid oz.",
            "floz",
            "floz.",
            "fl.oz.",
            "fl.oz",
        ): Conversion().floz_to_ml,
        ("l", "liter", "liters", "litre", "litres"): Conversion().l_to_gal,
        (
            "ml",
            "milliliter",
            "milliliters",
            "millilitre",
            "millilitres",
        ): Conversion().ml_to_floz,
    }

    for word in conversion_input_list:
        for units, func in conversion_dict.items():
            if word in units:
                return func(number)

    return "Invalid input! Please specify a valid measurement."


class Conversion:
    """The actual conversion functions."""

    def km_to_miles(self, km: float) -> str:
        return f"`{km} km` is equal to `{round((km * 0.6214), 2)} miles`."

    def miles_to_km(self, miles: float) -> str:
        return f"`{miles} miles` is equal to `{round((miles * 1.609344), 2)} km`."

    def kmh_to_mph(self, kmh: float) -> str:
        return f"`{kmh} km/h` is equal to `{round((kmh * 0.6214), 2)} mph`."

    def ms_to_mph(self, ms: float) -> str:
        return f"`{ms} m/s` is equal to `{round((ms * 2.237), 2)} mph`."

    def mph_to_ms_kmh(self, mph: float) -> str:
        return f"`{mph} mph` is equal to `{round((mph * 1.609344), 2)} km/h ({round((mph * 0.44704), 2)} m/s)`."

    def cm_to_inches(self, cm: float) -> str:
        return f"`{cm} cm` is equal to `{round((cm * 0.3937), 2)} inches`."

    def inches_to_cm(self, inches: float) -> str:
        return f"`{inches} inches` is equal to `{round((inches * 2.54), 2)} cm`."

    def meter_to_feet(self, meter: float) -> str:
        return f"`{meter} m` is equal to `{round((meter * 3.28084), 2)} feet`."

    def feet_to_meter(self, feet: float) -> str:
        return f"`{feet} feet` is equal to `{round((feet * 0.3048), 2)} m`."

    def c_to_f(self, c: float) -> str:
        return f"`{c}°C` is equal to `{round(((c * 9 / 5) + 32), 2)}°F`."

    def f_to_c(self, f: float) -> str:
        return f"`{f}°F` is equal to `{round(((f - 32) * 5 / 9), 2)}°C`."

    def lbs_to_kg(self, lbs: float) -> str:
        return f"`{lbs} lbs` is equal to `{round((lbs * 0.454), 2)} kg`."

    def kg_to_lbs(self, kg: float) -> str:
        return f"`{kg} kg` is equal to `{round((kg * 2.2046), 2)} lbs`."

    def oz_to_g(self, oz: float) -> str:
        return f"`{oz} oz` is equal to `{round((oz * 28.349523), 2)} g`."

    def g_to_oz(self, g: float) -> str:
        return f"`{g} g` is equal to `{round((g * 0.035274), 2)} oz`."

    def gal_to_l(self, gal: float) -> str:
        return f"`{gal} gal` is equal to `{round((gal * 3.785412), 2)} l`."

    def l_to_gal(self, ltr: float) -> str:
        return f"`{ltr} l` is equal to `{round((ltr * 0.264172), 2)} gal`."

    def floz_to_ml(self, floz: float) -> str:
        return f"`{floz} fl oz` is equal to `{round((floz * 29.574), 2)} ml`."

    def ml_to_floz(self, ml: float) -> str:
        return f"`{ml} ml` is equal to `{round((ml * 0.033814), 2)} fl oz`."
