from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserForm(ModelForm):
  class Meta:
    model = User

class Charity(models.Model):
  name = models.CharField(max_length=30)
  twitter_handle = models.CharField(max_length=20)

class Donations(models.Model):
  user = models.ForeignKey(User)
  charity = models.ForeignKey(Charity)
  amount = models.DecimalField(max_digits=12, decimal_places=2)
  date = models.DateTimeField(auto_now=True)
  status = models.CharField(max_length=15)
  tweet = models.CharField(max_length=150)

class StripeCustomer(models.Model):
  user = models.ForeignKey(User)
  customer_id = models.CharField(max_length=30)
  primary = models.BooleanField()
  valid = models.BooleanField()
