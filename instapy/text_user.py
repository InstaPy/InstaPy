# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import Client


def text_msg(): 
  # Find these values at https://twilio.com/user/account
  account_sid = "pasteAccountSIDhere"
  auth_token = "pasteAuthTokenHere"
  client = Client(account_sid, auth_token)
 
  message = client.api.account.messages.create(to="+yourNumber",
                                             from_="+TwilioNumber",
                                             body="InstaPy completed successfully")
 
 
  print message.sid
