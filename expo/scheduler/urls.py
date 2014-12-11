from django.conf.urls import patterns, include, url

from django.contrib.auth.views import *
from scheduler import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'GBE_scheduler.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^scheduler/list/?$',
        views.event_list, name = 'event_schedule'),    
    url(r'^scheduler/list/([-\w]+)/?$',
        views.event_list, name = 'event_schedule'),
    url(r'^scheduler/calendar/?$',
        views.calendar_view, name = 'calendar_view'),
    url(r'^/scheduler/calendar/(?P<cal_type>w+)/?$',
        views.calendar_view, name = 'calendar_view'),
    url(r'^scheduler/details/(\d+)/?$',
        views.detail_view, name = 'detail_view'),
    url(r'^scheduler/edit/(?P<event_type>[-\w]+)/(?P<eventitem_id>\d+)/?$', 
        views.edit_event, name = 'edit_event'),
   url(r'^scheduler/view_list/?$',
        views.view_list, name = 'event_list'),
    url(r'^scheduler/view_list/([-\w]+)/?$',
        views.view_list, name = 'event_list'),
 
    url(r'^scheduler/acts/?$',
        views.schedule_acts, name = 'schedule_acts')

                    
)
