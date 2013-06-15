import re
from accounts.models import Charity

MY_TWITTER_HANDLE = "kh_tester"

class TwitterParser:

  def __init__(self):
    TWITTER_HANDLE_RE = re.compile(r"@(\w+)")
    DOLLAR_AMOUNT_RE = re.compile(r"\$(\d*\.\d{1,2}|\d+)")

  def read_tweet(self, tweet):
    self.tweet = tweet

  def parse_tweet(self):
    handles = TWITTER_HANDLE_RE.findall(tweet)
    if not handles:
      pass
    handles.remove(MY_TWITTER_HANDLE)
    charities = Charity.objects.filter(twitter_handle__in=handles)
    if not charities:
      pass
    donation_amount = DOLLAR_AMOUNT_RE.findall(tweet)
    if donation_amount:
      if len(donation_amount) == 1:
        pass
      else:
        pass
    else:
      pass
    
