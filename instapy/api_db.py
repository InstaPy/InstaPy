import MySQLdb


def getConnection():
    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                         user="angie_app",  # your username
                         passwd="angiePasswordDB",  # your password
                         db="angie_app")
    db.set_character_set('utf8mb4')
    dbc = db.cursor()
    dbc.execute('SET NAMES utf8mb4;')
    dbc.execute('SET CHARACTER SET utf8mb4;')
    dbc.execute('SET character_set_connection=utf8mb4;')

    return db


def getCampaign(campaignId):
    if campaignId != False:
        row = fetchOne("select username,id_user,id_campaign,timestamp,id_account_type from campaign where id_campaign=%s", campaignId)
        return row
    else:
        return None


def getWebApplicationUser(id_user):
    if id_user != False:
        row = fetchOne("select * from users where id_user=%s", id_user)
        return row
    else:
        return False


def fetchOne(query, *args):
    db = getConnection()
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, args)
    db.close()
    return cur.fetchone()


def select(query, *args):
    db = getConnection()
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, args)
    rows = cur.fetchall()
    db.close()
    return list(rows)


def insert(query, *args):
    db = getConnection()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    id = cur.lastrowid
    db.close()
    return id

def updateCampaignChekpoint(key, value, id_campaign):
  query='INSERT INTO campaign_checkpoint (id_campaign, _key, value, timestamp) VALUES(%s, %s, %s, CURDATE()) ON DUPLICATE KEY UPDATE  value=%s'
  
  id = insert(query, id_campaign, key, value, value)
  
  return id
  
  
def insertBotAction(*args):
    query = "insert into bot_action (id_campaign, id_user, instagram_id_user, " \
            "full_name, username, user_image, post_id, post_image, " \
            "post_link,bot_operation,bot_operation_value,id_log,timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())"

    id = insert(query, *args)
    return id


def insertOwnFollower(*args):
    query = "insert into own_followers (id_user,instagram_id_user,full_name,username,user_image,is_verified,timestamp) " \
            " VALUES (%s,%s,%s,%s,%s,%s,now()) ON DUPLICATE KEY UPDATE instagram_id_user=instagram_id_user"

    id = insert(query, *args)
    return id


def insertUserFollower(*args):
    query = "insert into instagram_user_followers (fk,instagram_id_user,full_name,username,user_image,is_verified,timestamp) " \
            " VALUES (%s,%s,%s,%s,%s,%s,now()) ON DUPLICATE KEY UPDATE instagram_id_user=instagram_id_user"

    id = insert(query, *args)
    return id


def getBotIp(bot, id_user, id_campaign, is_bot_account):

    query = "select ip,type from  campaign left join ip_bot on campaign.id_ip_bot=ip_bot.id_ip_bot where id_campaign=%s"

    result = fetchOne(query, id_campaign)

    if result is None or result['ip'] is None:
        bot.logger.warning("getBotIp: Could not find an ip for user %s", id_user)
        raise Exception("getBotIp: Could not find an ip for user"+str(id_user))

    bot.logger.info("User %s, has ip: %s" % (id_user, result['ip']))
    return result