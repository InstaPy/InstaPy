from langdetect import detect

profile_description = '''Sewing goods for KIDS\u0026BABY rooms\n100%handmade\nwall art decor \ud83d\udc30\ud83e\udd8c\ud83d\udc18\n\u05e2\u05d9\u05e6\u05d5\u05d1 \u05d8\u05e7\u05e1\u05d8\u05d9\u05dc \u05d9\u05d9\u05d7\u05d5\u05d3\u05d9 \u05d5\u05de\u05e7\u05d5\u05e8\u05d9\n\u05dc\u05d0\u05d5\u05d5\u05d9\u05e8\u05d4 \u05e7\u05e1\u05d5\u05de\u05d4 \u05d5\u05d7\u05dc\u05d5\u05de\u05d9\u05ea \n\ud83e\udd84Be a UNICORN \ud83e\udd84\n\ud83d\udc47\ud83c\udffbshop NOW\ud83d\udc47\ud83c\udffb'''
profile_description = profile_description.encode('utf-8', 'ignore')
print(profile_description)
print (detect(profile_description))