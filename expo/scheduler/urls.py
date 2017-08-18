from django.conf.urls import patterns, include, url

from django.contrib.auth.views import *
from scheduler import views

event_types = ['All',
               'Show',
               'Special Event',
               'Class',
               'Volunteer Opportunity',
               'Lecture',
               'Workshop',
               'Panel',
               'Movement']
days_of_week = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday']

urlpatterns = patterns(
    '',
    url(r'^scheduler/list/?$',
        views.event_list, name='event_schedule'),
    url(r'^scheduler/list/([-\w]+)/?$',
        views.event_list, name='event_schedule'),
    url(r'^scheduler/calendar/?$',
        views.calendar_view, name='calendar_view'),
    #    url(r'^scheduler/(?P<event_type>Show|Class|Panel)/?$',
    #        views.calendar_view, name='calendar_view_event'),
    url(r'^scheduler/(?P<event_type>' +
        '|'.join(event_types) +
        ')/(?P<day>' +
        '|'.join(days_of_week) +
        ')/?$',
        views.calendar_view, name='calendar_view_day'),
    url(r'^scheduler/details/(\d+)/?$',
        views.detail_view, name='detail_view'),
    url(r'^scheduler/delete_schedule/(?P<scheduler_event_id>\d+)/?$',
        views.delete_schedule, name='delete_schedule'),
    url(r'^scheduler/delete_event/(?P<event_type>[-\w]+)/' +
        '(?P<eventitem_id>\d+)/?$',
        views.delete_event, name='delete_event'),
    url(r'^scheduler/view_list/?$',
        views.view_list, name='event_list'),
    url(r'^scheduler/view_list/([-\w]+)/?$',
        views.view_list, name='event_list'),
    url(r'^scheduler/acts/?$',
        views.schedule_acts, name='schedule_acts'),
    url(r'^scheduler/acts/(?P<show_id>\d+)/?$',
        views.schedule_acts, name='schedule_acts'),
    url(r'^scheduler/allocate/(\d+)/?$',
        views.allocate_workers, name='allocate_workers'),
    url(r'^scheduler/contactinfo/(\d+)/?$',
        views.contact_info, name='contact_info'),
    url(r'^scheduler/contactinfo/(\d+)/([-\w]+)/?$',
        views.contact_info, name='contact_info'),
    url(r'^scheduler/contact_by_role/([-\w]+)/?$',
        views.contact_by_role, name='contact_by_role'),
    url(r'^scheduler/export_calendar/?$',
        views.export_calendar, name='export_calendar'),
)
