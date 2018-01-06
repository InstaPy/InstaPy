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
#session.get_follow_list_from_user(following=True, followers=False)
#session.get_follow_list_from_user(following=False, followers=True)

userFollowlist = ["makiniregaldesigns", "anndanger", "astarosher", "bia.anotaai","bubri","insta.ludii","jannekevanraaf","oprah", "loveandlibby", "matan_sensel", "einadesign", "tweelingendesign", "nkahalon", "yaelyaniv", "pulkepanama" ,"lihihod", "galisjewelry", "shooka.stores", "ms_sweet_dreams", "danielyona", "peterandwolf.kids", "anattal03", "michaelabercu", "limortiroche", "danaungerfashion", "hilarahav", "kerenshpilsher", "petitedorisofficial", "jem_sharonbenzaray", "kerenbargil", "sivansternbach", "maria_rodsant", "misskyreeloves", "zucoulisses", "petit.os", "nyani_kids", "kidsinteriors_com", "adikastyle"]
for user in userFollowlist:
    session.get_follow_list_from_user(following=False, followers=True, username=user)

# end the bot session
session.end()
