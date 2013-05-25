from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

import urlparse
import oauth2 as oauth

consumer_key='5g55QBgZPuiX7dGdZPoVg'  # Fill in your key 
consumer_secret='07yF7MBTPnjHEsUmEjMUIWcz3BOFh56rjR9edamUxw' # Fill in your secret
request_token_url='https://api.twitter.com/oauth/request_token'
access_token_url='https://api.twitter.com/oauth/access_token'
authorize_url='https://api.twitter.com/oauth/authorize'
authenticate_url='https://api.twitter.com/oauth/authenticate'
request_token = None
consumer=oauth.Consumer(consumer_key,consumer_secret)

def home(request):
  return render_to_response('index.html',
                            context_instance=RequestContext(request))

def tlogin(request):
  client=oauth.Client(consumer)
  resp, content = client.request(request_token_url, "GET")
   
  if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])
   
  global request_token
  request_token = dict(urlparse.parse_qsl(content))
  return HttpResponseRedirect("%s?oauth_token=%s" % (authenticate_url, request_token['oauth_token']));

def treturn(request):
  token = oauth.Token(request_token['oauth_token'],request_token['oauth_token_secret'])
   
  token.set_verifier(request.GET.get('oauth_verifier'))
  client = oauth.Client(consumer, token)
   
  resp, content = client.request(access_token_url, "POST")
  access_token = dict(urlparse.parse_qsl(content))
   
  return HttpResponse(str([access_token.keys(),access_token.values()]))
"""
def tlogin(request):
  return render_to_response('tlogin.html', context_instance=RequestContext(request))

def treturn(request):
  return HttpResponse(str(request))
"""
