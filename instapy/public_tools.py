"""
Public tools to be able to be imported to everywhere.
Earlier util.py was doing this job but now it has some private imports
    that causes circular dependent import errors. That's why this file is born.
In future can clean-up util.py - to only have utilities, dismissing
    services; And then move the funtions here back to util.py and close the file.
"""


def truncate_float(number, precision, round=False):
    """ Truncate (shorten) a floating point value at given precision """

    # don't allow a negative precision [by mistake?]
    precision = abs(precision)

    if round:
        # python 2.7+ supported method [recommended]
        short_float = round(number, precision)

        # python 2.6+ supported method
        """short_float = float("{0:.{1}f}".format(number, precision))
        """

    else:
        operate_on = 1  # returns the absolute number (e.g. 11.0 from 11.456)

        for _ in range(precision):
            operate_on *= 10

        short_float = float(int(number * operate_on)) / operate_on

    return short_float
