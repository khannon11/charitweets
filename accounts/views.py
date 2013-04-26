from django.shortcuts import render_to_response, redirect
from django import forms
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from accounts.models import UserForm, StripeCustomer
#from ccPay.models import StripeCustomer

import stripe
import stripe_helper

def login_user(request):
  state = 'Please log in'
  username = password = ''
  if request.POST:
    username = request.POST.get('username')
    password = request.POST.get('password')
    next = request.GET.get('next')

    user = authenticate(username=username, password=password)

    if user is not None:
      if user.is_active:
        login(request, user)
        state = "Congratulations, you're logged in!"
        return render_to_response('accounts/profile.html',
                                  context_instance=RequestContext(request))
      else:
        state = "Your account is no longer active, please contact site admin"
    else:
      state = "Your username / password were incorrect"

    if next:
      return redirect(next)

  return render_to_response('accounts/login.html',
                            {'state':state, 'username': username},
                            context_instance=RequestContext(request))

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
    

def register(request):
  if request.method == 'POST':
    uf = UserRegistrationForm(request.POST)
    if uf.is_valid():
      # TODO check passwords against each other
      user = User.objects.create_user(uf.cleaned_data['twitter_handle'],
                                      uf.cleaned_data['email'],
                                      uf.cleaned_data['password'],
                                      first_name=uf.cleaned_data['first_name'],
                                      last_name=uf.cleaned_data['last_name'],)
      user.save()
      new_user = authenticate(username=uf.cleaned_data['twitter_handle'],
                   password=uf.cleaned_data['password'])
      login(request, new_user)
      return view_profile(request)
  else:
    uf = UserRegistrationForm()
  return render_to_response('accounts/register.html',
                            {'form': uf},
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
    stripeCustomer = StripeCustomer(user=request.user,
                                    customer_id=customer.id)
    stripeCustomer.save()
    return settings(request, 'Card Successfully Added')
  return render_to_response('accounts/add_card.html',
                            context_instance=RequestContext(request))
