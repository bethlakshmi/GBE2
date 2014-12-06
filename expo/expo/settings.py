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
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
SITE_ID=1

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

MEDIA_URL = '/'
LOGIN_URL = '/login/'

try:
   LOGIN_REDIRECT_URL
except:
   LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'gbe',
    'ticketing',
    'scheduler',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",)


#uncomment this to take the site down
#ROOT_URLCONF = 'expo.downconf'
ROOT_URLCONF = 'expo.urls'

WSGI_APPLICATION = 'expo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

try:
   DATABASES
except:
   DATABASES = {
      'default': {        'ENGINE': 'django.db.backends.sqlite3',
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

STATIC_URL = '/static/'


#Email settings for password reset

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





