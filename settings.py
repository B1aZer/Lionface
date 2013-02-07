#SETTING PY
import os, os.path

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
        ('Admin', 'blaze.imba@gmail.com'),
)

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = "webmaster@lionface.org"

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admin@lionface.org'
EMAIL_HOST_PASSWORD = '1Lion8fac31'


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

# this is re valued in local
MIDDLEWARE_CLASSES = (
    'mediagenerator.middleware.MediaMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'current_user.middleware.CurrentUserMiddleware',
    'account.middleware.TimezoneMiddleware',
    'account.middleware.ActiveUserMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
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

# this is re valued in local
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'kombu.transport.django',
    'django.contrib.comments',
    'registration',

    'south',
    'mediagenerator',
    'haystack',
    'djcelery',

    'current_user',
    'search',
    'public',
    'images',
    'account',
    'profile',
    'notification',
    'post',
    'tags',
    'messaging',
    'smileys',
    'oembed',
    'degrees',
    'pages',
    'agenda',
    'ecomm',
    'schools',
    'chat',
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
PRODUCTION_MEDIA_URL = '/media/'
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
        #'css/jquery-ui-1.9.1.custom.css',
        'css/jquery-ui-1.8.24.css',
    ),
    ('main.js',
        'js/jquery-1.8.0.min.js',
        'js/jquery.metadata.js',
        #'js/jquery.autosize-1.13.min.js',
        'js/jquery.autosize-1.15.4.js',
        #'js/jquery-ui-1.9.1.min.js',
        'js/jquery-ui-1.8.24.min.js',
        'js/handlebars-1.0.rc.1.min.js',
        'js/binaryajax.js',
        'js/exif.js',
        'js/load_image_mod.js',
        'js/jquery.form.js',
        'js/socket.io.js',
        'js/chat.js',
        'js/site.js',
    ),
    ('user.js',
        'js/user.js',
    ),
    ('feed.js',
        'js/feed.js',
        'js/post.js',
    ),
    ('images.js',
        'js/images.js',
    ),
    ('post.js',
        'js/post.js',
    ),
    ('public.js',
        'js/public.js',
    ),
    ('schools.js',
        'js/schools.js',
    ),
    ('profile.js',
        'js/profile.js',
    ),
    ('notification.js',
        'js/notification.js',
        'js/post.js',
        'js/images.js',
    ),
    ('messages.js',
        'js/messages.js',
    ),
    ('related.js',
        'js/related.js',
    ),
    ('pages.js',
        'js/pages.js',
    ),
    ('pages.settings.js',
        'js/pages.settings.js',
    ),
    ('pages.browse.js',
        'js/pages.browse.js',
    ),
    ('settings.js',
        'js/settings.js',
    ),
    ('search.js',
        'js/search.js',
    ),
    ('jstz.min.js',
        'js/jstz.min.js',
    ),
    ('fullcalendar.css',
        'css/fullcalendar.css',
    ),
    ('fullcalendar.print.css',
        'css/fullcalendar.print.css',
    ),
    ('fullcalendar.js',
        'js/fullcalendar.min.js',
    ),
    ('timePicker.css',
        'css/timePicker.css',
    ),
    ('timePicker.js',
        'js/jquery.timePicker.min.js',
    ),
    ('raphael.js',
        'js/graphs/raphael-min.js',
        'js/graphs/g.raphael-min.js',
        'js/graphs/g.line-min.js',
    ),
    ('jquery.validate.js',
        'js/jquery.validate.min.js',
    ),
)

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 7

STRIPE_API_KEY = '5IFFCmgHYrLqVm6ISBhhtq1Va7I80J9J'

SITE_ID = 1

# caelery django db queue
#BROKER_URL = "django://"

ACCOUNT_ACTIVATION_DAYS = 7
# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 300

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

WEBSOCKET_REDIS_BROKER = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0
}

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
    'auth.user': lambda o: "/%s/" % o.username,
}

CELERY_QUEUES = {"lionface": {"exchange": "lionface", "binding_key": "lionface"}}
CELERY_DEFAULT_QUEUE = "lionface"

from celery.schedules import crontab
from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    "update_search_index": {
        "task": "search.tasks.UpdateSearchIndex",
        "schedule": timedelta(seconds=120),
    },
    "rebuld_search_index": {
        "task": "search.tasks.RebuildSearchIndex",
        "schedule": timedelta(minutes=1440),
    },
    "update_page_event": {
        "task": "pages.tasks.UpdatePageEvent",
        "schedule": timedelta(minutes=30),
    },
    "delete_page": {
        "task": "pages.tasks.DeletePage",
        "schedule": timedelta(minutes=1440),
    },
    "delete_inactive_users": {
        "task": "account.tasks.DeleteInactiveUsers",
        "schedule": timedelta(minutes=1440),
    },
    "process_bids": {
        'task': 'pages.tasks.ProcessBids',
        'schedule': crontab(hour=1, minute=0, day_of_week=6),
        #'schedule': crontab(hour='*', minute=[20,50]),
    },
    "reprocess_bids": {
        'task': 'pages.tasks.ReprocessBids',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),
        #'schedule': crontab(hour='*', minute=[25,55]),
    },
    "update_pages_from_bids": {
        'task': 'pages.tasks.UpdatePagesFromBids',
        'schedule': crontab(hour=5, minute=0, day_of_week=1),
        #'schedule': crontab(hour='*', minute=[0,30]),
    },
}

import djcelery
djcelery.setup_loader()

IMAGES_DEFAULT_QUOTE = 'Whose woods these are I think I know, his house is ' \
    'in the village though.'
IMAGES_DEFAULT_QUOTE_AUTHOR = 'Robert Frost'
