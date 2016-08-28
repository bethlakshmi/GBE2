"""
Django settings for expo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# define deploy settings in a separate file
# Local settings should set
#  - db config
#  - LOGIN_REDIRECT
#  - ALLOWED_HOSTS
#  - debug mode (False for live site, True or False for dev/test)
#  - secret key if live site
# DO NOT commit local settings files to the repo!


try:
    from local_settings import *
except:
    pass

import os
gettext = lambda s: s
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
try:
    STATIC_ROOT
except:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
SITE_ID = 1

CMS_TEMPLATES = (
    ('big_block.tmpl', 'Big Block of Content'),
    ('three_column.tmpl', 'Three Column'),
    # ('template_2.tmpl', 'Template Two'),
)

LANGUAGES = [
    ('en-us', gettext('en-us')),

]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY
except:
    SECRET_KEY = '0sdq74686*ayl^0!tqlt*!mgsycr)h4h#*4*_x=2_dw9cq8d!i'

# SECURITY WARNING: don't run with debug turned on in production!
try:
    DEBUG
except:
    DEBUG = True

try:
    TEMPLATE_DEBUG
except:
    TEMPLATE_DEBUG = True

try:
    ALLOWED_HOSTS
except:
    ALLOWED_HOSTS = []

MEDIA_URL = '/media/'

try:
    MEDIA_ROOT
except:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOGIN_URL = '/login/'

try:
    LOGIN_REDIRECT_URL
except:
    LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'mptt',  # utilities for implementing a tree
    'south',  # Only needed for Django < 1.7
    'sekizai',  # for javascript and css management
    'django.contrib.messages',
    'treebeard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',  # tutorial
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'tinymce',
    'filer',
    'easy_thumbnails',
    #    'aldryn_bootstrap3',
    'reversion',  # for versioning in cms -- use easy install
    'scheduler',
    'ticketing',
    'gbe',
    'django_nose',
    'hijack',
    'compat',
    'debug_toolbar',
)
DEBUG_TOOLBAR_PATCH_SETTINGS = False

FIXTURE_DIRS = ('expo/tests/fixtures',)


THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    # 'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'hijack.middleware.HijackRemoteUserMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # added for django-cms
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # end of add for django-cms
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)



MIGRATION_MODULES = {

    # Add also the following modules if you're using these plugins:
}

SOUTH_MIGRATION_MODULES = {
    'image_gallery': 'image_gallery.south_migrations',
}

FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)


# uncomment this to take the site down
# ROOT_URLCONF = 'expo.downconf'
ROOT_URLCONF = 'expo.urls'

WSGI_APPLICATION = 'expo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

try:
    DATABASES
except:
    DATABASES = {
       'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
try:
    STATIC_URL
except:
    STATIC_URL = '/static/'

# Email settings for password reset

try:
    EMAIL_HOST
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS
    DEFAULT_FROM_EMAIL
except:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'gbetest@burlesque-expo.com'

DATETIME_FORMAT = "%I:%M %p"

# new for django-cms.  Don't know why yet.
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'expo', 'static'),
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

CMS_STYLE_NAMES = (
    ('info', ("info")),
    ('new', ("new")),
    ('hint', ("hint")),
    ('footer', ("footer")),
    ('subtitle', ("20th Century Poster")),
    ('font_large', ("Large, plain font")),
    ('font_regular', ("Regular Text"))
)


CMS_LANGUAGES = {
    # Customize this
    'default': {
        'public': True,
        'hide_untranslated': False,
        'redirect_on_fallback': True,
    },
    1: [
        {
            'public': True,
            'code': 'en-us',
            'hide_untranslated': False,
            'name': gettext('en-us'),
            'redirect_on_fallback': True,
        },
    ],
}

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

try:
    MC_API_KEY
except:
    MC_API_KEY = 'TEST'  # if not set, we won't try to hit mailchimp's API


#  Logging settings.
#  Local path and filename to write logs to
try:
    from expo.local_settings import LOG_FILE
except:
    LOG_FILE = 'logs/main.log'
#  Available levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
try:
    from expo.local_settings import LOG_LEVEL
except:
    LOG_LEVEL = 'INFO'
#  Format for the log file.  Should begin with a timestamp and the log level.
try:
    from expo.local_settings import LOG_FORMAT
except:
    LOG_FORMAT = '%(asctime)s::%(levelname)s::%(funcName)s - %(message)s'


# DJANGO-HIJACK
