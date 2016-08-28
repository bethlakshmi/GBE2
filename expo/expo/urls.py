from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^', include('gbe.urls', namespace = 'gbe')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^', include('ticketing.urls', namespace = 'ticketing')),
                       url(r'^', include('scheduler.urls', namespace = 'scheduler')),
                       url(r'^', include('gbe.report_urls', namespace = 'reporting')),
                       url(r'^tinymce/', include('tinymce.urls')),
                       url(r'^hijack/', include('hijack.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# always, always leave the last two lines as the last two lines.
# The cms.urls are grabby and must always be the last include.
