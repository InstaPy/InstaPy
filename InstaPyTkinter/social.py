import tkinter 
from instapy import InstaPy

from tkinter import ttk 
  
top = tkinter.Tk()

'''  
WELCOME TO InstaPy

THIS PROGRAM WAS DESIGNED BY RICHARD NIEVES, 

THE PROGRAM IS A GUI APPLICATION THAT JUST InstaPy FOR THE AUTOMATION BY USING TKINTER 
I WAS ABLE TO SIMPLEIFY INTO A SIMPLE A GUI APPLICATION THAT CAN BE ACTIVATED 
ON ANY COMPUTER WITH A FIREFOX BROWSER WITHOUT THE USE OF PROGRAMMING SKILLS.


 '''


txt = tkinter.Label(top, text= "Welcome to Insta Automation")

usertxt = tkinter.Label(top, text="Enter Username:")
user = tkinter.Entry(top, bd=1, width=27)

passtxt = tkinter.Label(top, text="Enter Password:")
passt = tkinter.Entry(top, show="*", bd=1, width=27,)

setting = ttk.Combobox(top, width = 27, textvariable =1 ) 
  
# Adding combobox drop down list 
setting['values'] = ('Choose Your Function', ' Like by Tags',  
                          ' Like by Feeds', 
                          ' Like by Locations', 
                          ' Follow by Tags', 
                          ' Follow by Locations', 
                          ' Follow someone elses followers', 
                          ' Unfollowing') 
  
setting.current(0)

tagtxt = tkinter.Label(top, text="Tag:")
tagt = tkinter.Entry(top, bd=1, width=27)
tagt['state'] = tkinter.NORMAL

locationtxt = tkinter.Label(top, text="Location:")
locationt = tkinter.Entry(top, bd=1, width=27)
locationt['state'] = tkinter.DISABLED

def aV():
   u = user.get()
   usertxt = len(u)
   p = user.get()
   t = tagt.get()
   x = t.split()

   if len(u) < 4 :
      setting['state'] = tkinter.DISABLED
      errtxt.pack()
   else:
      setting['state'] = tkinter.NORMAL
      errtxt.pack_forget()
   if len(p) < 4 :
      setting['state'] = tkinter.DISABLED
      errtxt.pack()
   else:
      setting['state'] = tkinter.NORMAL
      errtxt.pack_forget()




def helloCallBack():
   u = user.get()
   usertxt = len(u)
   p = user.get()
   t = tagt.get()
   x = t.split()
   
   aV()

   if setting.get() == ' Like by Tags':
      if len(t) == 0:
         tagt['state'] = tkinter.NORMAL
         
      session = InstaPy(username=u, password=p)
      session.login()
      session.like_by_tags(x, amount=100)
      session.end()
   
   if setting.get() == ' Like by Locations':
      if len(t) == 0:
         locationt['state'] = tkinter.NORMAL
         
      session = InstaPy(username=u, password=p)
      session.login()
      session.like_by_locations(['https://www.instagram.com/explore/locations/224177040/kingston-kingston-upon-thames-united-kingdom/'], amount=100)
      session.end()

   if setting.get() == ' Like by Feeds':
      session = InstaPy(username=u, password=p)
      session.login()
      session.like_by_feed(amount=100, randomize=True, unfollow=False, interact=True)
      session.end()

   if setting.get() == ' Follow someone elses followers':
      session = InstaPy(username=u, password=p)
      session.login()
      session.follow_user_followers(x, amount=10, randomize=False, sleep_delay=60)
      session.end()   

   if setting.get() == ' Unfollowing':
      session = InstaPy(username=u, password=p)
      session.login()
      session.unfollow_users(amount=126, nonFollowers=True, style="RANDOM", unfollow_after=42*60*60, sleep_delay=655)
      session.end()   


errtxt = tkinter.Label(top, fg="red",text="*****Check Details***")
sendbutton = tkinter.Button(top, text="Send", width=20, command=helloCallBack)





txt.pack()
usertxt.pack()
user.pack()

passtxt.pack()
passt.pack()
setting.pack()
tagtxt.pack()
tagt.pack()
sendbutton.pack()
top.mainloop()
