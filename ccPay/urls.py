from django.conf.urls import patterns,  url

from ccPay import views

urlpatterns = patterns(
  '',
  url(r'^newCard/',
      views.get_new_card,
      name='getNewCard'),
  url(r'^chargeCard/',
      views.charge_card,
      name='chargeCard'),
)
