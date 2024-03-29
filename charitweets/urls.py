from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

  # Examples:
  url(r'^$', 'charitweets.views.home', name='home'),
  # Uncomment the admin/doc line below to enable admin documentation:
  # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

  # Uncomment the next line to enable the admin:
  url(r'^admin/', include(admin.site.urls)),
  url(r'^accounts/', include('accounts.urls')),
  url(r'^blog/', include('blog.urls')),
  url(r'^ccPay/', include('ccPay.urls')),
  url(r'^tlogin', 'charitweets.views.tlogin'),
  url(r'^treturn', 'charitweets.views.treturn'),
)
