from django.conf.urls import (
    patterns,
    url,
)

from gbe.scheduling.views import (
    CreateEventScheduleView,
    CreateEventView,
)

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding patter, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.

urlpatterns = patterns(
    '',
    url(r'^scheduling/create_event/(?P<event_type>[-\w]+)/?$',
        CreateEventView, name='create_event'),
    url(r'^scheduling/create/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/?$',
        CreateEventScheduleView.as_view(), name='create_event_schedule'),
)
