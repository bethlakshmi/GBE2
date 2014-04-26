from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout
from gbe import views


# NOTE: in general, url patterns should end with '/?$'. This 
# means "match the preceding patter, plus an optional final '?', 
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!". 
# Which is what we usually want. 

urlpatterns = patterns ('', 
                        url(r'^/?$', 
                            views.index),
                        url(r'index.html/?', 
                            views.index),
                        url(r'^techinfo/?$', 
                            views.techinfo),
                        url(r'^profile/?$',
                            views.view_profile),
                        url(r'^profile/(\d)/?$',
                            views.view_profile),
                        url(r'^act/create/?$',
                            views.bid_act),
                        url(r'^act/review/?$',
                            views.review_acts),
                        url(r'^performer/create/?$',
                            views.register_as_performer),
                        url(r'^event/(P<event_id>\d+)/?$', 
                            views.event), 
                        url(r'^act/(?P<act_id>\d+)/?$', 
                            views.act),
                        url(r'^class/create/?$',
                            views.bid_class),
                        url(r'^bid/(?P<type>\w+)-(?P<response>\w+)', 
                            views.bid_response),
                        url(r'^bid/index/?$', 
                            views.test),
                        url(r'^login/?$', 
                            login),
                        url(r'^logout/?$', 
                            views.logout_view),
                        url(r'^accounts/profile/?$', 
                            views.update_profile),
                        url(r'^accounts/register/?$',
                            views.register),
                        url(r'^accounts/login/?$', 
                            login), 
                        url(r'^accounts/logout/?$', 
                            logout),
                        url(r'update_profile/?$', 
                            views.update_profile),
                        ) 
