from django.conf.urls import patterns, include, url

from accounts import views

urlpatterns = patterns(
  '',
  url(r'^login/',
      views.login_user,
      name='login'),
  url(r'^profile/',
    views.view_profile,
    name='view_user_profile'),
  url(r'^logout/',
    views.logout_user,
    name='logout'),
  url(r'^register/',
    views.register,
    name='register'),
  url(r'^settings',
    views.settings,
    name='settings'),
  url(r'^editUserInfo',
    views.editUserInfo,
    name='edit_user_info'),
  url(r'^changePassword',
    views.changePassword,
    name='change_password'),
)
