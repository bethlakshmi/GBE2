from django.conf.urls import (
    patterns,
    url,
)

from gbe.scheduling.views import (
    CreateEventView,
    MakeOccurrenceView,
    ManageVolOpsView,
    ShowCalendarView,
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
        MakeOccurrenceView.as_view(), name='create_event_schedule'),
    url(r'^scheduling/edit/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/' +
        '(?P<occurrence_id>\d+)/?$',
        MakeOccurrenceView.as_view(), name='edit_event_schedule'),
    url(r'^scheduling/manage-opps/(?P<event_type>[-\w]+)/' +
        '(?P<eventitem_id>\d+)/(?P<parent_event_id>\d+)/?$',
        ManageVolOpsView.as_view(), name='manage_opps'),
    url(r'^calendar/?$',
        ShowCalendarView.as_view(), name='calendar'),
)
