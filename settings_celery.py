#SETTING PY
import os, os.path

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'lionface.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False
USE_L10N = False

MEDIA_ROOT = ''
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+d*krjq(iz@43ru=%1t9ko9edr$5@a#wg%@m8)ac9ztkdhtudp'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'mediagenerator.middleware.MediaMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'current_user.middleware.CurrentUserMiddleware',
    'account.middleware.TimezoneMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "public.context_processors.current_site",
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'kombu.transport.django',
    'django.contrib.comments',

    'south',
    'mediagenerator',
    'haystack',
    'djcelery',

    'current_user',
    'search',
    'public',
    'account',
    'profile',
    'notification',
    'post',
    'tags',
    'messaging',
    'smileys',
    'oembed',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
COMMENT_MAX_LENGTH = '1000'

MEDIA_DEV_MODE = False
DEV_MEDIA_URL = '/devmedia/'
PRODUCTION_MEDIA_URL = '/lionface/media/'
GLOBAL_MEDIA_DIRS = (os.path.join(os.path.dirname(__file__), 'static'),)
# Configure yuicompressor if available
"""
YUICOMPRESSOR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'yuicompressor.jar')
if os.path.exists(YUICOMPRESSOR_PATH):
    ROOT_MEDIA_FILTERS = {
        'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
        'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
    }
"""

MEDIA_BUNDLES = (
    ('main.css',
        'css/reset.css',
        'css/style.css',
        'css/public.css',
        'css/jquery-ui-1.8.23.custom.css',
    ),
    ('main.js',
        'js/jquery-1.8.0.min.js',
        'js/jquery.metadata.js',
        'js/jquery.autosize-min.js',
        'js/jquery-ui-1.8.24.custom.min.js',
    ),
    ('common.js',
        'js/site.js',
    ),
    ('feed.js',
        'js/feed.js',
    ),
    ('timeline.js',
        'js/timeline.js',
    ),
    ('profile.js',
        'js/profile.js',
    ),
    ('notification.js',
        'js/notification.js',
    ),
    ('messages.js',
        'js/messages.js',
    ),
    ('related.js',
        'js/related.js',
    ),
    ('settings.js',
        'js/settings.js',
    ),
    ('jstz.min.js',
        'js/jstz.min.js',
    ),
)

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')

SITE_ID = 1
BROKER_URL = "django://"

if os.environ.get('production'):
	try:
	    from settings_production import *
	except ImportError:
	    pass
else:

	try:
	    from settings_local import *
	except ImportError:
	    pass

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/user/profile/%s/" % o.username,
}

CELERY_QUEUES = {"lionface": {"exchange": "lionface", "binding_key": "lionface"}}
CELERY_DEFAULT_QUEUE = "lionface"

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    "update_search_index": {
        "task": "search.tasks.UpdateSearchIndex",
        "schedule": timedelta(seconds=120),
    },
}

import djcelery
djcelery.setup_loader()

DEBUG=False
