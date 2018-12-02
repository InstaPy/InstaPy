"""
This template is written by @timgrossmann

What does this quickstart script aim to do?
- This script is automatically executed every 6h on my server via cron
"""


import random
from instapy import InstaPy
from instapy.util import smart_run

#This will import the login credentials
from instapy import secrets


# login credentials
insta_username = secrets.username
insta_password = secrets.password

dont_likes = ['sex','nude','naked','fisch','schwein','lamm',
		'rind','kuh','meeresfrüchte','schaf','ziege',
		'hummer','yoghurt','joghurt','essen','mahl',
		'truthahn','fur','leather','hunt','gun',
		'shoot','slaughter','pussy', 'funnymeme', 'meme', 'funnymemes',
		'memes','old','futbol','toluca','lmao','girl','italiangirl','14f',
		'fff']

friends = ['cjxgorman','patgreene07','transporterprotectiveservices','therealwonyteber',
		'hangryvet','michael_tps','dre__85','gunnerbravo03',
		'irishshawnpatricklessard','m.brancaccio','halexrivas','heylauber',
		'runningunny','callsign_hitch','remwoj_0311','moe_tee_2','dionf22',
		'tonycruz1115','greg_caron_','billd_987','joe__goot__25','lewis440311',
		'louisred3','brendough','djkhanvict','kattterear','lu_eats','brownstone1968',
		'cldavidson9','kundad19','ricktish','iamkennybok','kimmiebruss','usmcmark1982',
		'kbogle3','pelledean','vasq1215','jimqseng','into_the_wild_11','rodriguez319',
		'manny_fr3sh22','pew_hamoy','jmully75','nuno82mx','alexiverson123','ortiz782',
		'masri009','thornenyles','pat.espina','devokanivo','tgwl0322','herrlybird',
		'rms1812','dablez','neil1975','cpltommyboy','klaserhausen','yesi.sanchez',
		'avolfsonoftarth','thenickrayray','cristoph12','benjaminasch','senor_yuhas',
		'kazshamael','tlcplmax','terminallance','christopherpordon','seamusmcgui',
		'gauds42','themobilecigarlounge','vmanlalin','roadsendranchtx','k.witty217',
		'joseph.morgan.9256','manny_0311','don_valdez','nomadigan','sirmetbekinsurance',
		'whatfoodwasit','elloerin321']

like_tag_list = ['food','foodporn','foodgasm','foodphotography','foodie','foodstagram',
		'foodpics','foodpic','instafood']

# ignore_list prevents posts from being skipped
ignore_list = []

accounts = []



# get a session!
session = InstaPy(username=insta_username,
                      password=insta_password,
                      headless_browser=True)


with smart_run(session):
    # settings
    session.set_relationship_bounds(enabled=True,
				   max_followers=150)

    session.set_dont_include(friends)
    session.set_dont_like(dont_likes)
    session.set_ignore_if_contains(ignore_list)

    session.set_user_interact(amount=2, randomize=True, percentage=100)
    session.set_do_follow(enabled=True, percentage=40)
    session.set_do_like(enabled=True, percentage=80)

    # activity
    session.like_by_tags(random.sample(like_tag_list, 3), amount=random.randint(50, 100), interact=True)

    session.unfollow_users(amount=random.randint(75,150), InstapyFollowed=(True, "all"), style="FIFO", unfollow_after=90*60*60, sleep_delay=501)
