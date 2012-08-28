#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'               

USE_TZ = True
DEBUG = True
UPLOAD_DIR = '/var/www/placeless/lionface/whispering-anchorage-2296/uploads' 
MEDIA_ROOT = '/var/www/placeless/lionface/whispering-anchorage-2296/uploads'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/var/www/placeless/lionface/whispering-anchorage-2296/lionface.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

from os.path import abspath, dirname, join
import os
import sys

cwd = dirname(abspath(__file__))
sys.path.insert(0, join(cwd, "apps"))

sys.path.append('/var/www/placeless/lionface/whispering-anchorage-2296/')

os.environ["CELERY_LOADER"] = "django"
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'    
