#CELERY
#BROKER_URL = "django://"
USE_TZ = True
#PREPEND_WWW = True
#DEBUG = True

MEDIA_ROOT = '/var/www/whispering-anchorage-2296/'
UPLOAD_DIR = '/var/www/whispering-anchorage-2296/uploads/'

from os.path import abspath, dirname, join
import os
import sys

cwd = dirname(abspath(__file__))

sys.path.insert(0, join(cwd, "apps"))

sys.path.append('/var/www/whispering-anchorage-2296/')

os.environ["CELERY_LOADER"] = "django"
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mydb',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '1Lion8face.',                  # Not used with sqlite3.
        'HOST': 'mydb.c9iodczmwien.us-east-1.rds.amazonaws.com',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
        'TEST_NAME': 'auto_tests',
    }
}

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#        'LOCATION': 'cache_table',
#    }
#}
