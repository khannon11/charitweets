from django.conf.urls import patterns, include, url

from accounts import views

urlpatterns = patterns(
  '',
  url(r'^login/',
    'django.contrib.auth.views.login',
    {'template_name': 'accounts/login.html'}),
  url(r'^profile/',
    views.view_profile,
    name='view_user_profile'),
  url(r'^logout/',
    views.logout_user,
    name='logout'),
)
