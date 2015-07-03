from django.conf.urls import patterns, url
from django.contrib.auth.views import *
from gbe import views

# NOTE: "urlconf" for taking site down for maintenance

urlpatterns = patterns('',
                       url(r'^.*$',
                           views.down, name='down'),
                      )
