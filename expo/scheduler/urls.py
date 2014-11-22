from django.conf.urls import patterns, include, url

from django.contrib.auth.views import *
from scheduler import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'GBE_scheduler.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^scheduler/classes/?$',
        views.class_schedule, name = 'class_schedule'),
    url(r'^scheduler/events/?$',
        views.event_list, name = 'event_schedule'),
    url(r'^scheduler/panel/?$',
        views.panel_schedule, name = 'panel_schedule'),
    url(r'^scheduler/calendar/?$',
        views.calendar_view, name = 'calendar_view'),
    url(r'^/scheduler/calendar/(?P<cal_type>w+)/?$',
        views.calendar_view, name = 'calendar_view'),
    url(r'^scheduler/details/(\d+)/?$',
        views.detail_view, name = 'detail_view'),
    url(r'^scheduler/event/edit/(\d+)/?$', 
        views.edit_event, name = 'edit_event'),
    url(r'^scheduler/class_list/?$',
        views.class_list, name = 'class_list'),
    url(r'^scheduler/show_list/?$',
        views.show_list, name = 'show_list'),
            
                    
)
