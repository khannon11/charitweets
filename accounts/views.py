from django.shortcuts import render_to_response, redirect
from django import forms
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from accounts.models import UserForm

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
  return render_to_response('accounts/profile.html',
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
def settings(request):
  return render_to_response('accounts/settings.html',
                           context_instance=RequestContext(request))

@login_required
def editUserInfo(request):
  return render_to_response('accounts/edit_user_info.html',
                            context_instance=RequestContext(request))

@login_required
def changePassword(request):
  return render_to_response('accounts/change_password.html',
                            context_instance=RequestContext(request))
