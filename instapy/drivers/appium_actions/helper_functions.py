def _cleanup_count(count: str=None):
    if ',' in count:
        return count.replace(',','')
    else:
        minus_one = False
        if '.' in count:
            minus_one = True
            count = count.replace('.','')
        if 'K' in count:
            if minus_one:
                count = count.replace('K','00')
            else:
                count = count.replace('K','000')
            return count
        elif 'M' in count:
            if minus_one:
                count = count.replace('M','00000')
            else:
                count = count.replace('K','000000')
            return count
        return count
