from os.path import abspath, dirname, join
import os
import sys

cwd = dirname(abspath(__file__))

sys.path.insert(0, join(cwd, "apps"))

sys.path.append('/var/www/django/lionface')
sys.path.append('/var/www/django')

os.environ["CELERY_LOADER"] = "django"
os.environ['PYTHON_EGG_CACHE'] = '/var/www/django/lionface/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
