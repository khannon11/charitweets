from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserForm(ModelForm):
  class Meta:
    model = User

class Donations(models.Model):
  user = models.ForeignKey(User)
  amount = models.DecimalField(max_digits=12, decimal_places=2)
  date = models.DateTimeField(auto_now=True)
  status = models.CharField(max_length=15)

class StripeCustomer(models.Model):
  user = models.ForeignKey(User, verbose_name='twitter handle of customer')
  customer_id = models.CharField(max_length=30)
