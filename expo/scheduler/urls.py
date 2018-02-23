from django.conf.urls import patterns, include, url

from django.contrib.auth.views import *
from scheduler import views

urlpatterns = patterns(
    '',
    url(r'^scheduler/list/?$',
        views.event_list, name='event_schedule'),
    url(r'^scheduler/list/([-\w]+)/?$',
        views.event_list, name='event_schedule'),
    url(r'^scheduler/acts/?$',
        views.schedule_acts, name='schedule_acts'),
    url(r'^scheduler/acts/(?P<show_id>\d+)/?$',
        views.schedule_acts, name='schedule_acts'),
    url(r'^scheduler/export_calendar/?$',
        views.export_calendar, name='export_calendar'),
)
