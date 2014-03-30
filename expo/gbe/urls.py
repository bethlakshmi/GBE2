from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout
from gbe import views

urlpatterns = patterns ('', 
                        url(r'^$', 
                            views.index),
                        url(r'index.html', 
                            views.index),
                        url(r'^event/(P<event_id>\d+)/$', 
                            views.event), 
                        url(r'^act/(?P<act_id>\d+)/$', 
                            views.act),
                        url(r'^bid/act', 
                            views.bid_act),
                        url(r'^bid/editact/(?P<actbid_id>\d+)/$', 
                            views.bid_act, {}),
                        url(r'^bid/thankact', 
                            views.bid_act_thanks),
                        url(r'^login/,*$', logout),
                        url(r'^accounts/profile/$', 
                            views.update_profile),
                        url(r'^accounts/register/$',
                            views.register),
                        url(r'accounts/login/$', login), 
                        url(r'accounts/logout/$', logout),
                        url(r'update_profile/$', views.update_profile),
                        ) 
