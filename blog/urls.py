from django.conf.urls import patterns, include, url

from blog import views

urlpatterns = patterns(
  '',
  (r'^$', views.index),
  url(r'^view/(?P<slug>[^\.]+)',
      views.view_post,
      name='view_blog_post'),
  url(r'^category/(?P<slug>[^\.]+)',
      views.view_category,
      name='view_blog_category'),
  url(r'^new/',
      views.new_post,
      name='new_blog_post'),
)
