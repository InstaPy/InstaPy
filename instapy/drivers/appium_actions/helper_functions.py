def _cleanup_count(count: str = None):
    """
    transform the string given on followers/following into int
    :param count:
    :return:
    """
    if "," in count:
        return int(count.replace(",", ""))
    else:
        if "K" in count:
            count = count.replace("K", "")
            return int(float(count) * 1000)
        elif "M" in count:
            count = count.replace("M", "")
            return int(float(count) * 1000000)
