def seconds_to_upper_minutes(s):
    """
    Takes a number of seconds and converts it to the number of minutes
    required to contain that number of seconds.
    """
    minutes = s / 60
    return s if not s % 60 else s + 1
