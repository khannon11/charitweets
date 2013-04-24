# Create your views here.

from django.shortcuts import render_to_response
from django.template import RequestContext

import stripe_helper

def get_new_card(request):
  return render_to_response('ccPay/new_card.html',
    context_instance=RequestContext(request)
  )

def charge_card(request):
  # TODO handle case of GET response
  if request.method == 'POST':
    charge_amount = int(float(request.POST['amount']) * 100)
    token = request.POST['stripeToken']
    charge_result = stripe_helper.chargeCreditCard(charge_amount, 'usd', token)
    return render_to_response('ccPay/charge_result.html',
                              {'result': charge_result},
                              context_instance=RequestContext(request))
