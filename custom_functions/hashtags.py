# ------------------------------------------->
# Function for Custom hashtags
# ------------------------------------------->
import random
import emoji
from itertools import permutations, repeat
# random.shuffle(emojis)

# Nature Lover
# ---------------->
nature = [
    'nature',
    'wildlife',
    'wildness',
    'adventures',
    'animal'
    'ocean',
    'sky',
    'clouds',
    'sun',
    'beachlife',
    'mountains',
]

# Travel
# ---------------->
travel = [
    'travel',
    'journey',
    'weltreise',
    'reiselust',
]

# Sports & Activities
# ---------------->
activities = [
    'skating',
    'climbing',
    'diving',
    'longboard',
    'longboarding',
]

# Cities
# ---------------->
cities = [
    'berlin',
    'techno',
    'ostkreuz',
    'electronicmusic',
    'vienna',
    'friedrichshain',
    'venedig',
    'barcelona',
    'marseille',
]

# Media
# ---------------->
media = [
    'digital',
    'technology',
    'digitalart',
    'media',
    'webdesign'
]

hashtags_combined = [
    nature,
    travel,
    activities,
    cities,
    media
]

hashtags_combined_flat = []

# Basic Flatten lists https://coderwall.com/p/rcmaea/flatten-a-list-of-lists-in-one-line-in-python
# The Loop Way
for sublist in hashtags_combined:
    for item in sublist:
        hashtags_combined_flat.append(item)

# See All Comments
print('\n'.join(hashtags_combined_flat))
