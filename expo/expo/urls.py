from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^', include('gbe.urls')), 
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^ticketing/', include('ticketing.urls')),
                       url(r'^scheduler/', include('scheduler.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
