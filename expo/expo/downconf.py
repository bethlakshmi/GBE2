from django.conf.urls import patterns, url
from django.contrib.auth.views import *
from gbe import views
from django.conf import settings

# NOTE: "urlconf" for taking site down for maintenance


urlpatterns = patterns ('', 
                        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
                                 'document_root': settings.MEDIA_ROOT}),
# landing page
                        url(r'^.*$', 
                            views.down, name = 'down'),
                       )
