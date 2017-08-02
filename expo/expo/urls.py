from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from cms.sitemaps import CMSSitemap
from expo.settings import APP_DJANGOBB
from django.contrib import admin
admin.autodiscover()

LOCAL_APPS_URLS = ()

# The indentation on this is FUGLY and BAD, but PEP8
if APP_DJANGOBB is True:
    LOCAL_APPS_URLS = LOCAL_APPS_URLS + (url(r'^forum/',
                                         include('djangobb_forum.urls',
                                                 namespace='djangobb')),)
if settings.DEBUG:
    import debug_toolbar
    LOCAL_APPS_URLS += (
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )


urlpatterns = (
    '',
    url(r'^', include('gbe.urls', namespace='gbe')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('ticketing.urls', namespace='ticketing')),
    url(r'^', include('scheduler.urls', namespace='scheduler')),
    url(r'^', include('gbe.reporting.urls', namespace='reporting')),
    url(r'^', include('gbe.scheduling.urls', namespace='scheduling')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^hijack/', include('hijack.urls')),
    ) + LOCAL_APPS_URLS + (
    url(r'^', include('cms.urls')),
)

urlpatterns = patterns(*urlpatterns) + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# always, always leave the last two lines as the last two lines.
# The cms.urls are grabby and must always be the last include.
