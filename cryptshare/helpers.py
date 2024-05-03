from datetime import datetime, timedelta


def clean_expiration(date_string_value, default_days=2):
    """
    This function is used to clean and standardize the expiration date values.

    :param date_string_value: The input date value as a string. It can be in various formats.
    :param default_days: The default number of days to add to the current date if the input date value is empty.
    :return: The cleaned date value as a datetime object.

    The function handles various formats of expiration dates and also relative expiration dates like "tomorrow", "2d" (2 days), "3w" (3 weeks), "4m" (4 months).
    """

    now = datetime.now()
    date_value = None

    # Handle empty expiration dates
    if date_string_value is None or date_string_value == "":
        return now + timedelta(days=default_days)  # "2028-10-09T11:51:46+02:00"

    if type(date_string_value) is datetime:
        return date_string_value

    # Handle various formats of expiration dates
    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d %H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%YT%H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y %H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y %H:%M:%S %z")
    except ValueError:
        pass
    else:
        return date_value

    # Handle relative expiration dates
    if date_string_value == "tomorrow":
        return now + timedelta(days=1)

    if date_string_value.endswith("d"):
        days = int(date_string_value[:-1])
        return now + timedelta(days=days)

    if date_string_value.endswith("w"):
        weeks = int(date_string_value[:-1])
        return now + timedelta(weeks=weeks)

    if date_string_value.endswith("m"):
        months = int(date_string_value[:-1])
        return now + timedelta(weeks=months * 4)
    return date_value


def clean_string_list(string_list):
    """
    This function is used to clean and standardize the input string list.

    :param string_list: The input string list. It can be a list or a string seperated by spaces.
    :return: The cleaned string list as a list of strings.

    The function handles various formats of string lists and also removes duplicates.
    """

    if string_list is None or string_list == "":
        return []
    try:
        string_list = string_list.split(" ")
    except AttributeError:
        pass
    except Exception as e:
        print(type(e))
        print(e)
    if type(string_list) is not list:
        string_list = [string_list]

    # remove duplicates
    string_list = list(dict.fromkeys(string_list))
    return string_list
