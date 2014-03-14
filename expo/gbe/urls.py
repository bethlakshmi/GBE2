from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout
from gbe import views


urlpatterns = patterns ('', 
                        url(r'^$', 
                            views.index),
                        url(r'^event/(P<event_id>\d+)/$', 
                            views.event), 
                        url(r'^act/(?P<act_id>\d+)/$', 
                            views.act),
                        url(r'^login/.*$', login), 
                        url(r'^login/,*$', logout),
                        url(r'^accounts/profile/$', 
                            views.profile),
                        url(r'^accounts/register/$',
                            views.register),
                        url(r'accounts/login/$', login), 
                        url(r'accounts/logout/$', logout),
                        url(r'update_profile/$', views.update_profile),
                        )
