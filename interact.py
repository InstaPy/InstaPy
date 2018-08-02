#!/usr/bin/python

import os
import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException

from instapy import InstaPy

from instapy import Settings

insta_username = 'meinerttt'
insta_password = 'pdSA1202'
dont_include = ['teamkaisersport', 'julsoeultra', 'northcoastultra', '9000running', 'goldbearrunners', 'lifeofsportdk', 'camilladuncker', 'karolinekschmidt', 'dennisvelasquez_', 'braae85', 'thomsenrasmus', 'pnorthcott', 'kristina_dalstrup', 'kvistlone', 'sarahretboell', 'janhilding', 'dorthe1977', 'inaamramlose', 'fynshave', 'mrkallehave', 'rikkerosenvinge', 'hannewis', 'ursulahasselbalch', 'christvete', 'stafford2956', 'cillebechmoller', 'ibrainsstreaming', 'bisgaardvin', 'eliasson_rasmus', 'louisegaarden', 'kristinaholstjuul', 'pia.r.boedker', 'pernilleherold', 'lisbethraekby', 'thomasbergholt', 'ibrains', 'heidi_bergholt_madsen', 'annekatrinejo', 'christianlpedersen', 'camillapandekage', 'sabinejjaatog', 'troelsboeche', 'finnkock', 'royalfrederik', 'mierytterhedegaard', 'gitte_ks', 'allanbjorn75', 'liselotte1405', 'pshoeg', 'h.h.ultra66', 'jhandberg', 'q_courage', 'mlbirkehoj', 'niels_buus', 'klaus.bodker', 'tuxen1', 'lykkeburmoelle', 'ceciliealletorp', 'romtotten', 'kathrinekschmidt', 'foghaps', 'larsfeldthaus', 'donna_anne_chadwick', 'rebildporten', 'anna_moeller97', 'kristinaextremerunning', 'runnersdk_mark', 'carowozniacki', 'lineguldhammer', 'trailrunningsilkeborg', 'stinatroest', 'kilianjornet', '9000running', 'marathonsportdk', 'simongrimstrup', 'salomon_danmark', 'monikabenserud', 'jon.bertelsen', 'runnersdk.dk', 'mjenneke93', 'salomonrunning', 'triatland_rebild', 'gingerrunner', 'aalborg_kommune', 'aalborgrunners', 'aarhus_motion', 'kimberleydt', 'vesterbytri', 'julsoeultra', 'rebildkommune', 'sisstiss', 'trail_heart', 'dgnrun', 'strava', 'saraslott', 'trailrunningdenmark', 'juliecarl.dk', 'atletikdk', 'ultracup']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

Settings.log_location = os.path.join(BASE_DIR, 'myLogs')
Settings.database_location = os.path.join(BASE_DIR, 'myLogs', insta_username+'.db')

# set headless_browser=True if you want to run InstaPy on a server

# set these in instapy/settings.py if you're locating the
# library in the /usr/lib/pythonX.X/ directory:
#   Settings.database_location = '/path/to/instapy.db'
#   Settings.chromedriver_location = '/path/to/chromedriver'

session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False,
                  multi_logs=True,
                  bypass_suspicious_attempt=False)

try:
    session.login()

    # settings
    session.set_relationship_bounds(enabled=True,
                                    potency_ratio=-1.0,
                                    delimit_by_numbers=True,
                                    max_followers=9000,
                                    max_following=5555,
                                    min_followers=30,
                                    min_following=40)

    session.set_dont_include(dont_include)
    session.set_ignore_users(['SunsetDate'])
    session.set_dont_like(['pizza', 'girl','islænder','gay'])

    session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
    session.set_do_follow(enabled=False, percentage=70)
    session.set_do_like(enabled=True, percentage=70)
    session.set_comments(["Cool", "Super!"])
    session.set_do_comment(enabled=False, percentage=80)
    session.interact_user_followers(['meinerttt'], amount=5, randomize=True)

except Exception as exc:
    # if changes to IG layout, upload the file to help us locate the change
    if isinstance(exc, NoSuchElementException):
        file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
        with open(file_path, 'wb') as fp:
            fp.write(session.browser.page_source.encode('utf8'))
        print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
            '*' * 70, file_path))
    # full stacktrace when raising Github issue
    raise

finally:
    # end the bot session
    session.end()
