from django.shortcuts import render_to_response, redirect
from django import forms
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect

from accounts.models import UserForm, StripeCustomer
#from ccPay.models import StripeCustomer

import stripe
import stripe_helper
import twitter

import urlparse
import oauth2 as oauth

consumer_key='5g55QBgZPuiX7dGdZPoVg'
consumer_secret='07yF7MBTPnjHEsUmEjMUIWcz3BOFh56rjR9edamUxw'
request_token_url='https://api.twitter.com/oauth/request_token'
access_token_url='https://api.twitter.com/oauth/access_token'
authorize_url='https://api.twitter.com/oauth/authorize'
authenticate_url='https://api.twitter.com/oauth/authenticate'
request_token = None
default_password="default"
consumer=oauth.Consumer(consumer_key,consumer_secret)

def register_user(access_token):
  screen_name = access_token['screen_name']
  api = twitter.Api(consumer_key, consumer_secret, access_token['oauth_token'],
                    access_token['oauth_token_secret'])
  user = User.objects.create_user(screen_name, '', default_password,
                                  first_name=api.GetUser(screen_name).GetName())
  user.save()

def login_send(request):
  request.session['next'] = request.GET.get('next')
  client=oauth.Client(consumer)
  resp, content = client.request(request_token_url, "POST")

  if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])

  global request_token
  request_token = dict(urlparse.parse_qsl(content))
  return HttpResponseRedirect("%s?oauth_token=%s" % (authenticate_url, request_token['oauth_token']));

def login_receive(request):
  token = oauth.Token(request_token['oauth_token'],request_token['oauth_token_secret'])

  token.set_verifier(request.GET.get('oauth_verifier'))
  client = oauth.Client(consumer, token)

  resp, content = client.request(access_token_url, "POST")
  access_token = dict(urlparse.parse_qsl(content))

  if access_token['screen_name'] not in [user.username for user
                                         in User.objects.all()]:
    register_user(access_token)

  user = authenticate(username=access_token['screen_name'], password=default_password)
  if user is not None:
    if user.is_active:
      login(request, user)
    else:
      raise Exception('User not active')
  else:
    raise Exception('invalid credentials')
  next = request.session.get('next', None)
  if next:
    del request.session['next']
    return HttpResponseRedirect(request.session.get('next'))
  return view_profile(request)

def logout_user(request):
  logout(request)
  return render_to_response('index.html',
                            {'state': 'Please log in'},
                            context_instance=RequestContext(request))

@login_required
def view_profile(request):
  stripe_customers = StripeCustomer.objects.filter(user=request.user)
  customers = [stripe.Customer.retrieve(cus.customer_id) for cus in stripe_customers]
  return render_to_response('accounts/profile.html',
                            {'customers': customers},
                            context_instance=RequestContext(request))

class UserRegistrationForm(forms.Form):
  twitter_handle = forms.CharField(max_length=30)
  password = forms.CharField(widget=forms.PasswordInput)
  first_name = forms.CharField(max_length=20)
  last_name = forms.CharField(max_length=20)
  email = forms.EmailField()
    
@login_required
def settings(request, status=''):
  return render_to_response('accounts/settings.html',
                           {'status': status},
                           context_instance=RequestContext(request))

class EditUserInfoForm(forms.Form):
  # TODO propagate username changes
  #username = forms.CharField(label=u'Twitter Handle')
  email = forms.CharField(label=u'Email')
  first_name = forms.CharField(label=u'First Name')
  last_name = forms.CharField(label=u'Last Name')

@login_required
def editUserInfo(request):
  error = ''
  if request.method == 'POST':
    form = EditUserInfoForm(request.POST)
    if form.is_valid():
      if form.cleaned_data['email'] != request.user.email:
        request.user.email = form.cleaned_data['email']
      if form.cleaned_data['first_name'] != request.user.first_name:
        request.user.first_name = form.cleaned_data['first_name']
      if form.cleaned_data['last_name'] != request.user.last_name:
        request.user.last_name = form.cleaned_data['last_name']
      request.user.save()  
      return settings(request, 'User info changed successfully!')
  form = EditUserInfoForm(initial={'email': request.user.email,
                                   'first_name': request.user.first_name,
                                   'last_name': request.user.last_name})
  return render_to_response('accounts/edit_user_info.html',
                            {'form': form, 'error': error},
                            context_instance=RequestContext(request))

@login_required
def changePassword(request):
  error = ''
  if request.method == 'POST':
    form = PasswordChangeForm(request.POST)
    if form.is_valid():
      if form.cleaned_data['password1'] == form.cleaned_data['password2']:
        request.user.set_password(form.cleaned_data['password1'])
        request.user.save()
        return settings(request, 'Password changed successfully')
      else:
        error = 'The passwords must match!'
  form = PasswordChangeForm()
  return render_to_response('accounts/change_password.html',
                            {'form': form, 'error': error},
                            context_instance=RequestContext(request))


class PasswordChangeForm(forms.Form):
  password1 = forms.CharField(label=u'Password',
                              widget=forms.PasswordInput)
  password2 = forms.CharField(label=u'Confirm Password',
                              widget=forms.PasswordInput)

@login_required
def addCard(request):
  if request.method == 'POST':
    stripeToken = request.POST.get('stripeToken')
    customer = stripe.Customer.create(email=request.user.email,
                                      card=stripeToken)
    prev_cards = request.user.stripecustomer_set.all()
    is_primary = not any([card.primary for card in prev_cards])
    stripeCustomer = StripeCustomer(user=request.user,
                                    customer_id=customer.id,
                                    valid=True,
                                    primary=is_primary)
    stripeCustomer.save()
    email = request.POST.get('email', None)
    if email:
      user = request.user
      user.email = email
      user.save()
    return settings(request, 'Card Successfully Added')
  return render_to_response('accounts/add_card.html',
                            context_instance=RequestContext(request))
