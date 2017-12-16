from instapy import InstaPy

with open('./logs/user.txt', 'r') as file:
    insta_username = file.readline()
    print(insta_username)
with open('./logs/password.txt', 'r') as file:
    insta_password = file.readline()

session = InstaPy(username=insta_username, password=insta_password)
print("1")

# set up all the settings
session.login()
#session.getFollowerList_user(following=True, followers=False)
#session.getFollowerList_user(following=False, followers=True)

userFollowlist = ["oprah", "loveandlibby", "matan_sensel", "einadesign", "tweelingendesign", "nkahalon", "yaelyaniv", "pulkepanama" ,"lihihod", "galisjewerly", "shooka.stores", "ms_sweet_dreams", "danielyona", "ronitshler", "peterandwolf.kids", "anattal03", "michaelbercu", "limortiroche", "danaungerfashion", "hilarahav", "kerenshpilsher", "petitedorisofficial", "jem_sharonbenzaray", "kerenbargil", "sivansternbach", "maria_rodsant", "misskyreeloves", "zucoulisses", "petit.os", "foxsheartbeat", "nyani_kids", "littleops_", "kidsinteriors_com", "mytrendtroom", "adikastyle"]
for user in userFollowlist:
    session.getFollowerList_user(following=False, followers=True, username=user)

# end the bot session
session.end()
