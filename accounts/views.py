import oauth2 as oauth
import stripe
import twitter
import urlparse

from accounts.models import StripeCustomer
from accounts.constants import CONSUMER_KEY, CONSUMER_SECRET, REQUEST_TOKEN, \
  REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHENTICATE_URL, DEFAULT_PASSWORD

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


def register_user(access_token):
  screen_name = access_token['screen_name']
  api = twitter.Api(CONSUMER_KEY, CONSUMER_SECRET, access_token['oauth_token'],
      access_token['oauth_token_secret'])
  user = User.objects.create_user(screen_name, '', DEFAULT_PASSWORD,
      first_name=api.GetUser(screen_name).GetName())
  user.save()

def login_send(request):
  request.session['next'] = request.GET.get('next')
  client = oauth.Client(CONSUMER)
  resp, content = client.request(REQUEST_TOKEN_URL, "POST")

  if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])

  global REQUEST_TOKEN
  REQUEST_TOKEN = dict(urlparse.parse_qsl(content))
  return HttpResponseRedirect("%s?oauth_token=%s" % (AUTHENTICATE_URL,
                                                  REQUEST_TOKEN['oauth_token']))

def login_receive(request):
  token = oauth.Token(REQUEST_TOKEN['oauth_token'],
                      REQUEST_TOKEN['oauth_token_secret'])

  token.set_verifier(request.GET.get('oauth_verifier'))
  client = oauth.Client(CONSUMER, token)

  content = client.request(ACCESS_TOKEN_URL, "POST")[1]
  access_token = dict(urlparse.parse_qsl(content))

  if access_token['screen_name'] not in [user.username for user
                                         in User.objects.all()]:
    register_user(access_token)

  user = authenticate(username=access_token['screen_name'],
                      password=DEFAULT_PASSWORD)
  if user is not None:
    if user.is_active:
      login(request, user)
    else:
      raise Exception('User not active')
  else:
    raise Exception('invalid credentials')
  next_page = request.session.get('next', None)
  if next_page:
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
  customers = [stripe.Customer.retrieve(cus.customer_id) for cus
               in stripe_customers]
  return render_to_response('accounts/profile.html',
                            {'customers': customers},
                            context_instance=RequestContext(request))

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
