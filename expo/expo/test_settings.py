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
    from settings import *
except:
    pass


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
    'snowpenguin.django.recaptcha2',
    'scheduler',
    'ticketing',
    'gbe',
    'django_nose',
    'hijack',
    'hijack_admin',
    'compat',
    'ad_rotator',
    'post_office',
    'import_export',
)
