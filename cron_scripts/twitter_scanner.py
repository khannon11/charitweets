import twitter
import time

api = twitter.Api('5g55QBgZPuiX7dGdZPoVg',
                  '07yF7MBTPnjHEsUmEjMUIWcz3BOFh56rjR9edamUxw',
                  '1364466696-Ma1SP8u47oKsu7Dl9Kp3I0T9fTnidnqEeFxZuEn',
                  'CUA6YHD0rlqLcS4X9a4udOgQjcGcn5QPMx6SLHtWiX4')

with open('prev_tweet') as f:
  last_id = long(f.readlines()[0])

latest_tweets = api.GetReplies(since_id = last_id)

if len(latest_tweets) > 0:
  with open('output', 'a') as f:
    for tweet in latest_tweets:
      api.PostUpdate("Thanks for tweeting @%s, %s" % (tweet._user._screen_name, str(time.time())))
      f.write("%s\n" % tweet._text)

  with open('prev_tweet', 'w') as f:
    f.write(str(latest_tweets[0]._id))
