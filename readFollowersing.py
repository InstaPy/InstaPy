import pickle


with open('./logs/all_followers.pkl', 'rb') as input:
    all_followers = pickle.load(input)
with open('./logs/all_following.pkl', 'rb') as input:
    all_following = pickle.load(input)

print (len(all_followers), " ",len(all_following))