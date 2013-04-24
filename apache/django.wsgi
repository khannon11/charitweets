import os
import sys

sys.path.append('/home/ec2-user/code/charitweets')
os.environ['DJANGO_SETTINGS_MODULE'] = 'charitweets.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
