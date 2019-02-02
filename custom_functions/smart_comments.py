import random
import emoji
# from itertools import permutations, repeat
# from quickstart import session

# see unicode emoji list
# http://unicode.org/emoji/charts/full-emoji-list.html
# @{} adds the Users Username
pre_comments = [
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Wow! ',
    'Hallo! :) ',
    'Hallo! ',
    'Hello! ',
    'Hey! ',
    'Hey! :waving_hand: ',
    'Hi! ',
    'Hey there :) ',
    'Hello there! '
    ':thumbs_up: ',
    'Howdy! ',
    ':green_heart: ',
    ':red_heart: ',
    ':man_raising_hand: ',
    'yeay! :heart: ',
    ':star-struck: ',
    'Shalom! ',
    'Whats up? ',
    'Holla! ',
    'Yo! ',
    'Hiya! '
]

add_user_name = [
    '',
    '',
    '',
    '',
    '',
    '',
    '@{} ',
]

comments = [
    'Beautiful',
    'Superb',
    'Amazing',
    'Excellent',
    'Magnificent',
    'Lovely',
    'Marvelous',
    'Thats a nice',
    'This is a nice',
    'Thats a sweet',
    'Sweet',
    'What a wonderful',
    'Wonderful',
    'What a beautiful',
    'What a sweet',
    'Great',
    'This is a great',
    'Good',
    'Admirable',
    'Gorgeous',
    'Glorious',
    'Good looking',
    'Such a beautiful',
    'Such a great',
    'Cool',
    'Nice',
]

sentence_endings = [
    '.',
    '.',
    '!',
    '!!',
]

# see unicode emoji list
# http://unicode.org/emoji/charts/full-emoji-list.html
emojis_1 = [
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    ':thumbs_up:',
    ':smile:',
    ':heart:',
    ':smile:',
    ':heart_eyes:',
    ':relaxed:',
    ':sunny:',
    ':hugging_face:',
    ':face_blowing_a_kiss:',
    ':hugging_face:',
    ':cowboy_hat_face:',
    ':nerd_face:',
    ':ghost:',
    ':victory_hand:',
    ':smiling_face_with_sunglasses:',
    ':star-struck:',
]

# see unicode emoji list
# http://unicode.org/emoji/charts/full-emoji-list.html
emojis_2 = [
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    ':thumbs_up:',
    ':smile:',
    ':blush:',
    ':ok_hand:'
    ':nerd_face:',
    ':nerd_face::red_heart:',
    ':heart:',
    ':heart::smile:',
    ':smile:',
    ':heart_eyes:',
    ':relaxed:',
    ':sunny:',
    ':love-you_gesture:',
    ':red_heart:',
    ':green_heart:',
    ':orange_heart:',
    ':yellow_heart:',
    ':red_heart:',
    ':hundred_points:',
]

# New and much faster smart comment function
def smart_comments(synonyms=['picture', 'image'], synonyms_before=[''], synonyms_after=[''], emojis=['']):

    comments_combined = []

    for x in range(0, 1000):

        # ----------->
        pre_comments_shuffeld = random.sample(pre_comments, 1)
        add_user_shuffeld = random.sample(add_user_name, 1)
        comments_shuffeld = random.sample(comments, 1)
        synonyms_before_shuffeld = random.sample(synonyms_before, 1)
        synonyms_shuffeld = random.sample(synonyms, 1)
        synonyms_after_shuffeld = random.sample(synonyms_after, 1)
        sentence_endings_shuffeld = random.sample(sentence_endings, 1)
        emojis_shuffeld = random.sample(emojis, 1)
        emojis_1_shuffeld = random.sample(emojis_1, 1)
        emojis_2_shuffeld = random.sample(emojis_2, 1)

        # Remove Spacing again if definition is an empty space
        # ----------->
        if synonyms_after_shuffeld == ['']:
            spacing = ''
        else:
            spacing = ' '

        # ----------->
        #
        if synonyms_before_shuffeld == ['']:
            spacing_synonyms_before = ''
        else:
            spacing_synonyms_before = ' '


        comment_combined = [
            a + b + c + ' ' + d + spacing_synonyms_before + e + spacing + f + g + ' ' + h + i + j
            for a in pre_comments_shuffeld
            for b in add_user_shuffeld
            for c in comments_shuffeld
            for d in synonyms_before_shuffeld
            for e in synonyms_shuffeld
            for f in synonyms_after_shuffeld
            for g in sentence_endings_shuffeld
            for h in emojis_shuffeld
            for i in emojis_1_shuffeld
            for j in emojis_2_shuffeld
        ]

        comments_combined.append(comment_combined[0])

    # comments sets
    # remove double
    # --------------------->
    comments_combined_set = set(comments_combined)

    seen = set()
    result = []
    for item in comments_combined_set:
        if item not in seen:
            seen.add(item)
            result.append(item)

    # print('\n'.join(result))

    return result

# See All Comments
# print('\n'.join(
#     smart_comments(
#         synonyms=['ocean', 'ocean', 'sea'],
#         synonyms_before=['lolsen', 'jo', 'whaaaat?', 'hell yeah!'],
#         synonyms_after=['shot', 'image', 'picture', 'photo'],
#         emojis=[':water_wave:',':droplet:',':person_surfing:',':smiling_face_with_sunglasses:', '', '']
#     )
# ))
