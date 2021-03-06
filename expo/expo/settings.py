"""
Django settings for expo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
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
SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
        'OPTIONS': {
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader'
                ),
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',  # used in tutorial
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',   # tutorial
                'django.template.context_processors.static',
                'django.template.context_processors.tz',     # tutorial
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                ],
        },
    },
]

CMS_TEMPLATES = (
    ('big_block.tmpl', 'Big Block of Content'),
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
    'cms',
    'mptt',  # utilities for implementing a tree
    'treebeard',
    'menus',
    'sekizai',  # for javascript and css management
    'djangocms_admin_style',
    'django.contrib.messages',
    'djangocms_text_ckeditor',
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
    'djangocms-placeholder-attr',
    'djangocms_style',
    'djangocms_snippet',
    'djangocms_googlemap',
    'djangocms_inherit',
    'djangocms_video',
    'djangocms_column',
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_link',
    'cmsplugin_filer_image',
    'cmsplugin_filer_teaser',
    'aldryn_bootstrap3',
    'snowpenguin.django.recaptcha2',
    'reversion',  # for versioning in cms -- use easy install
    'scheduler',
    'ticketing',
    'gbe',
    'django_nose',
    'hijack',
    'compat',
    'debug_toolbar',
    'ad_rotator',
    'post_office',
    'import_export',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

FIXTURE_DIRS = ('expo/tests/fixtures',)

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

MIDDLEWARE_CLASSES = (
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'hijack.middleware.HijackRemoteUserMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #    added for django-cms
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    #    end of add for django-cms
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'gbe.auth.EmailUsernameAuth',
)

TEXT_SAVE_IMAGE_FUNCTION = \
    'cmsplugin_filer_image.integrations.ckeditor.create_image_plugin'


'''
SOUTH_MIGRATION_MODULES = {
    'image_gallery': 'image_gallery.south_migrations',
    "post_office": "post_office.south_migrations",
}
'''

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

# TIME_FORMAT is often used for ending times of events, or when you
# do not need to give the date, such as in calendar grids
try:
    TIME_FORMAT
except:
    TIME_FORMAT = "%-I:%M %p"

try:
    DATE_FORMAT
except:
    DATE_FORMAT = "%a, %b %-d"
    URL_DATE = "%m-%d-%Y"
try:
    DATETIME_FORMAT
except:
    # Default DATETIME_FORMAT - see 'man date' for format options
    # DATETIME_FORMAT = "%I:%M %p"
    DATETIME_FORMAT = DATE_FORMAT+" "+TIME_FORMAT

try:
    SHORT_DATETIME_FORMAT
except:
    SHORT_DATETIME_FORMAT = "%a, "+TIME_FORMAT

try:
    DURATION_FORMAT
except:
    DURATION_FORMAT = "%-I:%M"

try:
    DAY_FORMAT
except:
    DAY_FORMAT = "%A"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
try:
    STATIC_URL
except:
    STATIC_URL = '/static/'

# Email settings for password reset

try:
    EMAIL_BACKEND
    DEFAULT_FROM_EMAIL
except:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'gbetest@burlesque-expo.com'
    EMAIL_BACKEND = 'post_office.EmailBackend'

# new for django-cms.  Don't know why yet.
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'expo', 'static'),
)
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,paste,searchreplace, insertdatetime",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'theme_advanced_buttons1': "bold,italic,underline,|,justifyleft," +
    "justifycenter,justifyright,fontselect,fontsizeselect,formatselect," +
    "forecolor,backcolor",
    'theme_advanced_buttons2': "cut,copy,paste,|,bullist,numlist,|," +
    "outdent,indent,|,undo,redo,|,link,unlink,anchor,image,|,code,preview," +
    "|,search, replace",
    'theme_advanced_buttons3': "insertdate,inserttime,|,advhr,,removeformat," +
    "|,sub,sup,|,charmap,emotions, tablecontrols",
}

DJANGOCMS_STYLE_CHOICES = ['subtitle',
                           'font_large',
                           'container',
                           'content',
                           'teaser']
CKEDITOR_SETTINGS = {
    'stylesSet': 'default:/static/styles/styles.js',
}

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


#  This block is for using local_settings.py to control which external
#  apps are setup and configured to execute within this installation
#  of GBE2.  Only alter this if you read through local_settings.py
#  and urls.py to see how this works.

try:
    APP_DJANGOBB
except:
    APP_DJANGOBB = False

if APP_DJANGOBB is True:
    INSTALLED_APPS = INSTALLED_APPS + ('djangobb_forum',)
    TEMPLATE_CONTEXT_PROCESSORS = TEMPLATE_CONTEXT_PROCESSORS + \
        ('djangobb_forum.context_processors.forum_settings',)

    # HAYSTACK settings, for DjangoBB_Forum
    HAYSTACK_DEFAULT_OPERATOR = 'OR'
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': '/vagrant/expo/whoosh/whoosh_index',
            'TIMEOUT': 60 * 5,
            'INCLUDE_SPELLING': True,
            'BATCH_SIZE': 100,
            'EXCLUDED_INDEXES': [
                    'thirdpartyapp.search_indexes.BarIndex'],
        },
        'autocomplete': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': '/vagrant/expo/whoosh_index',
            'STORAGE': 'file',
            'POST_LIMIT': 128 * 1024 * 1024,
            'INCLUDE_SPELLING': True,
            'BATCH_SIZE': 100,
            'EXCLUDED_INDEXES': [
                    'thirdpartyapp.search_indexes.BarIndex'],
        },
        # 'slave': {
        #     'ENGINE': 'xapian_backend.XapianEngine',
        #     'PATH': '/home/search/xapian_index',
        #     'INCLUDE_SPELLING': True,
        #     'BATCH_SIZE': 100,
        #     'EXCLUDED_INDEXES': [ \
        #         'thirdpartyapp.search_indexes.BarIndex'],
        #     },
        'db': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
            'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
        }
    }

try:
    EVALUATION_WINDOW
except:
    EVALUATION_WINDOW = 4

# DJANGO-HIJACK

HIJACK_LOGIN_REDIRECT_URL = '/gbe/'
HIJACK_LOGOUT_REDIRECT_URL = '/admin/auth/user/'
HIJACK_ALLOW_GET_REQUESTS = True
