from django.conf.urls import (
    patterns,
    url,
)

from gbe.scheduling.views import (
    AllocateWorkerView,
    ClassWizardView,
    CopyOccurrenceView,
    CreateEventView,
    EventDetailView,
    EventWizardView,
    ListEventsView,
    MakeOccurrenceView,
    ManageEventsView,
    ManageVolOpsView,
    SetFavoriteView,
    ShowCalendarView,
    TicketedClassWizardView,
)

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding patter, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.

urlpatterns = patterns(
    '',
    url(r'^scheduling/manage/?$',
        ManageEventsView.as_view(), name='manage_event_list'),
    url(r'^scheduling/manage/(?P<conference_slug>[-\w]+)/?$',
        ManageEventsView.as_view(), name='manage_event_list'),
    url(r'^scheduling/create_event/(?P<event_type>[-\w]+)/?$',
        CreateEventView, name='create_event'),
    url(r'^scheduling/create_class_wizard/(?P<conference>[-\w]+)/?$',
        ClassWizardView.as_view(), name='create_class_wizard'),
    url(r'^scheduling/create_class_wizard/(?P<conference>[-\w]+)/' +
        '(?P<event_type>[-\w]+)/?$',
        TicketedClassWizardView.as_view(),
        name='create_ticketed_class_wizard'),
    url(r'^scheduling/create_event_wizard/(?P<conference>[-\w]+)/?$',
        EventWizardView.as_view(), name='create_event_wizard'),
    url(r'^scheduling/create/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/?$',
        MakeOccurrenceView.as_view(), name='create_event_schedule'),
    url(r'^scheduling/edit/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/' +
        '(?P<occurrence_id>\d+)/?$',
        MakeOccurrenceView.as_view(), name='edit_event_schedule'),
    url(r'^scheduling/copy/(?P<occurrence_id>\d+)/?$',
        CopyOccurrenceView.as_view(), name='copy_event_schedule'),
    url(r'^scheduling/manage-opps/(?P<event_type>[-\w]+)/' +
        '(?P<eventitem_id>\d+)/(?P<parent_event_id>\d+)/?$',
        ManageVolOpsView.as_view(), name='manage_opps'),
    url(r'^calendar/(?P<calendar_type>[-\w]+)/?$',
        ShowCalendarView.as_view(), name='calendar'),
    url(r'^scheduling/favorite/(?P<occurrence_id>\d+)/(?P<state>on|off)/?$',
        SetFavoriteView.as_view(), name='set_favorite'),
    url(r'^scheduling/allocate/(?P<event_type>[-\w]+)/' +
        '(?P<eventitem_id>[-\w]+)/(?P<occurrence_id>\d+)/?$',
        AllocateWorkerView.as_view(), name='allocate_workers'),
    url(r'^scheduling/view_list/?$',
        ListEventsView.as_view(), name='event_list'),
    url(r'^scheduling/view_list/([-\w]+)/?$',
        ListEventsView.as_view(), name='event_list'),
    url(r'^scheduling/details/(?P<eventitem_id>\d+)/?$',
        EventDetailView.as_view(), name='detail_view'),
)
