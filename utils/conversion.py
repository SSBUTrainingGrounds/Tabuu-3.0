import re

#reads the input from the string and applies the appropriate conversion
def convert_input(input: str):
    #this block somehow gets the first floating point number or normal int found. no clue, i dont understand regex
    rx = re.compile('[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?', re.VERBOSE)
    nums = rx.findall(input)
    number = float(nums[0])

    #this block here gets you all the words in the input in a list, to compare those to the lists below
    input = input.lower()
    input = ''.join([i for i in input if not i.isdigit() and i not in ('+', '-')])
    input = input.split()

    miles_list = ["miles", "mi", "mile"]
    feet_list = ["foot", "feet", "ft" ,"'"]
    inches_list = ['inch', 'in', '"', 'inches']
    km_list = ['km', 'kilometer', 'kilometre', 'kilometers', 'kilometres', 'kms']
    meter_list = ['m', 'meter', 'metre', 'meters', 'meters']
    cm_list = ['cm', 'centimeter', 'centimetre', 'centimeters', 'centimetres', 'cms']

    kmh_list = ['kmh', 'kph', 'km/h']
    ms_list = ['ms', 'm/s', 'mps']
    mph_list = ['mph', 'mi/h']

    fahrenheit_list = ['f', '°f', 'fahrenheit']
    celsius_list = ['c', '°c', 'celsius']

    pounds_list = ['lbs', 'pounds', 'pound']
    ounces_list = ['oz', 'ounces', 'ounce']
    kg_list = ['kg', 'kilogram', 'kilograms', 'kilogrammes']
    grams_list = ['g', 'gram', 'grams', 'grammes']

    gallons_list = ['gallon', 'gal', 'gallons', 'gl']
    fluid_ounces_list = ['fluid ounce', 'fluid ounces', 'fl ounce', 'fl ounces', 'fl oz', 'fluid oz', 'fl. ounce', 'fl. ounces', 'fl. oz.', 'fluid oz.']
    liter_list = ['l', 'liter', 'liters', 'litre', 'litres']
    ml_list = ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres']
    
    for word in input:
        if word in miles_list:
            return(f"`{number} miles` is equal to `{Conversion.miles_to_km(number)} km`.")
        elif word in feet_list:
            return(f"`{number} feet` is equal to `{Conversion.feet_to_meter(number)} m.`")
        elif word in inches_list:
            return(f"`{number} inches` is equal to `{Conversion.inches_to_cm(number)} cm.`")

        elif word in km_list:
            return(f"`{number} km` is equal to `{Conversion.km_to_miles(number)} miles`.")
        elif word in meter_list:
            return(f"`{number} m` is equal to `{Conversion.meter_to_feet(number)} feet`.")
        elif word in cm_list:
            return(f"`{number} cm` is equal to `{Conversion.cm_to_inches(number)} inches.`")

        elif word in kmh_list:
            return(f"`{number} km/h` is equal to `{Conversion.km_to_miles(number)} mph`.")
        elif word in ms_list:
            return(f"`{number} m/s` is equal to `{Conversion.ms_to_mph(number)} mph`.")
        elif word in mph_list:
            return(f"`{number} mph` is equal to `{Conversion.miles_to_km(number)} km/h ({Conversion.mph_to_ms(number)} m/s)`.")

        elif word in fahrenheit_list:
            return(f"`{number}°F` is equal to `{Conversion.f_to_c(number)}°C.`")
        elif word in celsius_list:
            return(f"`{number}°C` is equal to `{Conversion.c_to_f(number)}°F.`")

        elif word in pounds_list:
            return(f"`{number} lbs` is equal to `{Conversion.lbs_to_kg(number)} kg.`")
        elif word in ounces_list:
            return(f"`{number} oz` is equal to `{Conversion.oz_to_g(number)} g.`")
        elif word in kg_list:
            return(f"`{number} kg` is equal to `{Conversion.kg_to_lbs(number)} lbs.`")
        elif word in grams_list:
            return(f"`{number} g` is equal to `{Conversion.g_to_oz(number)} oz.`")

        elif word in gallons_list:
            return(f"`{number} gal` is equal to `{Conversion.gal_to_l(number)} l.`")
        elif word in fluid_ounces_list:
            return(f"`{number} fl oz` is equal to `{Conversion.floz_to_ml(number)} ml.`")
        elif word in liter_list:
            return(f"`{number} l` is equal to `{Conversion.l_to_gal(number)} gal.`")
        elif word in ml_list:
            return(f"`{number} ml` is equal to `{Conversion.ml_to_floz(number)} fl oz.`")


    return("Invalid input! Please specify a valid measurement.")

#the conversion functions
class Conversion:
    def km_to_miles(km: float):
        return round((km * 0.6214), 2)

    def miles_to_km(miles: float):
        return round((miles * 1.609344), 2)

    def ms_to_mph(ms: float):
        return round((ms * 2.237), 2)

    def mph_to_ms(mph: float):
        return round((mph * 0.44704), 2)

    def cm_to_inches(cm: float):
        return round((cm * 0.3937), 2)

    def inches_to_cm(inches: float):
        return round((inches * 2.54), 2)

    def meter_to_feet(meter: float):
        return round((meter * 3.28084), 2)

    def feet_to_meter(feet: float):
        return round((feet * 0.3048), 2)

    def c_to_f(c: float):
        return round(((c * 9/5) + 32), 2)

    def f_to_c(f: float):
        return round(((f - 32) * 5/9), 2)

    def lbs_to_kg(lbs: float):
        return round((lbs * 0.454), 2)

    def kg_to_lbs(kg: float):
        return round((kg * 2.2046), 2)

    def oz_to_g(oz: float):
        return round((oz * 28.349523), 2)

    def g_to_oz(g: float):
        return round((g * 0.035274), 2)

    def gal_to_l(gal: float):
        return round((gal * 3.785412), 2)

    def l_to_gal(l: float):
        return round((l * 0.264172), 2)

    def floz_to_ml(floz: float):
        return round((floz * 29,574), 2)

    def ml_to_floz(ml: float):
        return round((ml * 0.033814), 2)