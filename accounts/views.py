from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_user(request):
  state = 'Please log in'
  username = password = ''
  if request.POST:
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
      if user.is_active:
        login(request, user)
        state = "Congratulations, you're logged in!"
      else:
        state = "Your account is no longer active, please contact site admin"
    else:
      state = "Your username / password were incorrect"

  return render_to_response('login.html',
                            {'state':state, 'username': username},
                            context_instance=RequestContext(request))

def logout_user(request):
  logout(request)
  return render_to_response('index.html',
                            {'state': 'Please log in'})

@login_required
def view_profile(request):
  return render_to_response('accounts/profile.html',
                            {'user': request.user})
