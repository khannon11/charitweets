import MySQLdb
import twitter
import time

import sys
sys.path.append('/home/ec2-user/code/charitweets')
from django.core.management import setup_environ
import charitweets.settings
setup_environ(charitweets.settings)

from django.contrib.auth.models import User

api = twitter.Api('5g55QBgZPuiX7dGdZPoVg',
                  '07yF7MBTPnjHEsUmEjMUIWcz3BOFh56rjR9edamUxw',
                  '1364466696-Ma1SP8u47oKsu7Dl9Kp3I0T9fTnidnqEeFxZuEn',
                  'CUA6YHD0rlqLcS4X9a4udOgQjcGcn5QPMx6SLHtWiX4')

with open('prev_tweet') as f:
  last_id = long(f.readlines()[0])

latest_tweets = api.GetReplies()#since_id = last_id)

if len(latest_tweets) > 0:
  for tweet in latest_tweets:
    print tweet.GetUser().GetScreenName(), "!!!!!", tweet.GetText()
    try:
      user = User.objects.filter(username=tweet.GetUser().GetScreenName())[0]
      stripe_cards = [card for card in user.stripecustomer_set.all()
                      if card.valid]
      message = "Thanks for the donation!"
      print stripe_cards
    except IndexError:
      print "Hey @%s, follow this link to complete your donation! %s" % \
        (tweet.GetUser().GetScreenName(), "http://charitweets.org:8000/accounts/addCard")
      # No user with that screen name yet


#  with open('prev_tweet', 'w') as f:
#    f.write(str(latest_tweets[0]._id))
