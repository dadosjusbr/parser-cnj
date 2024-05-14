import re

def is_nan(string):
    return string != string

def format_element(element):
    # A value was found with incorrect formatting. (3,045.99 instead of 3045.99)
    if is_nan(element) or not re.search(r'\d', str(element)):
        return 0.0
    if type(element) == str:
        if "." in element and "," in element:
            element = element.replace(".", "").replace(",", ".")
        elif "," in element:
            element = element.replace(",", ".")
        elif "-" in element:
            element = 0.0

    return float(element)