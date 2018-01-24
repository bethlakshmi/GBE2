from django.conf.urls import (
    patterns,
    url,
)

from gbe.scheduling.views import (
    AllocateWorkerView,
    ClassWizardView,
    CopyOccurrenceView,
    CreateEventView,
    EditEventView,
    EditStaffAreaView,
    EvalEventView,
    EventDetailView,
    EventWizardView,
    ListEventsView,
    MakeOccurrenceView,
    ManageEventsView,
    ManageVolOpsView,
    ManageVolWizardView,
    SetFavoriteView,
    ShowCalendarView,
    StaffAreaWizardView,
    TicketedEventWizardView,
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
    url(r'^scheduling/create_staff_area_wizard/(?P<conference>[-\w]+)/?$',
        StaffAreaWizardView.as_view(), name='staff_area_wizard'),
    url(r'^scheduling/create_ticketed_wizard/(?P<conference>[-\w]+)/' +
        '(?P<event_type>[-\w]+)/?$',
        TicketedEventWizardView.as_view(),
        name='create_ticketed_event_wizard'),
    url(r'^scheduling/create_event_wizard/(?P<conference>[-\w]+)/?$',
        EventWizardView.as_view(), name='create_event_wizard'),
    url(r'^scheduling/edit/(?P<conference>[-\w]+)/(?P<occurrence_id>\d+)/?$',
        EditEventView.as_view(),
        name='edit_event'),
    url(r'^scheduling/staff_edit/(?P<staff_id>\d+)/?$',
        EditStaffAreaView.as_view(),
        name='edit_staff'),
    url(r'^scheduling/manage-opps/(?P<conference>[-\w]+)/' +
        '(?P<occurrence_id>\d+)/?$',
        EditEventView.as_view(), name='manage_vol'),
    url(r'^scheduling/manage-opps/(?P<staff_slug>[-\w]+)/?$',
        EditStaffAreaView.as_view(), name='manage_vol'),

    url(r'^scheduling/copy/(?P<occurrence_id>\d+)/?$',
        CopyOccurrenceView.as_view(), name='copy_event_schedule'),

    url(r'^scheduling/create/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/?$',
        MakeOccurrenceView.as_view(), name='create_event_schedule'),
    url(r'^scheduling/edit/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/' +
        '(?P<occurrence_id>\d+)/?$',
        MakeOccurrenceView.as_view(), name='edit_event_schedule'),
    url(r'^scheduling/manage-opps/(?P<event_type>[-\w]+)/' +
        '(?P<eventitem_id>\d+)/(?P<parent_event_id>\d+)/?$',
        ManageVolOpsView.as_view(), name='manage_opps'),
    url(r'^calendar/(?P<calendar_type>[-\w]+)/?$',
        ShowCalendarView.as_view(), name='calendar'),
    url(r'^scheduling/evaluate/(?P<occurrence_id>\d+)/?$',
        EvalEventView.as_view(), name='eval_event'),
    url(r'^scheduling/favorite/(?P<occurrence_id>\d+)/(?P<state>on|off)/?$',
        SetFavoriteView.as_view(), name='set_favorite'),
    url(r'^scheduling/allocate/(?P<event_type>[-\w]+)/' +
        '(?P<eventitem_id>[-\w]+)/(?P<occurrence_id>\d+)/?$',
        AllocateWorkerView.as_view(), name='allocate_workers'),
    url(r'^scheduling/view_list/?$',
        ListEventsView.as_view(), name='event_list'),
    url(r'^scheduling/view_list/(?P<event_type>[-\w]+)/?$',
        ListEventsView.as_view(), name='event_list'),
    url(r'^scheduling/details/(?P<eventitem_id>\d+)/?$',
        EventDetailView.as_view(), name='detail_view'),
)
