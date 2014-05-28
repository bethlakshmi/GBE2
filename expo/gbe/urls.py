from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout
from gbe import views


# NOTE: in general, url patterns should end with '/?$'. This 
# means "match the preceding patter, plus an optional final '?', 
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!". 
# Which is what we usually want. 

urlpatterns = patterns ('', 

# landing page
                        url(r'^/?$', 
                            views.landing_page),
                        url(r'index.html/?', 
                            views.landing_page),

# profile
                        url(r'^profile/?$',
                            views.profile),
                        url(r'^profiles/?$',
                            views.profiles),
                        url(r'^profile/(\d)/?$',
                            views.profile),
                        url(r'^profile/admin/(\d)/?$',
                            views.admin_profile),
# acts
                        url(r'^act/create/?$',
                            views.bid_act),
                        url(r'^act/edit/(\d)/?$',
                            views.edit_act),
                        url(r'^act/review/?$',
                            views.review_acts),
                        url(r'^act/review/(\d)/?$',
                            views.review_act),
                        url(r'^act/reviewlist/?$',
                            views.review_act_list),
                        url(r'^act/(?P<act_id>\d+)/?$', 
                            views.act),
                        url(r'^act/submit/(\d)/?$',
                            views.submit_act),

# classes
                        url(r'^class/create/?$',
                            views.bid_class),
                        url(r'class/edit/(\d+)/?$', 
                            views.edit_class),                        
                        url(r'^class/propose/?$',
                            views.propose_class),


# personae
                        url(r'^performer/create/?$',
                            views.register_persona),
                        url(r'^persona/edit/(\d)/?$',
                            views.edit_persona),
                        url(r'^troupe/create/?$',
                            views.create_troupe),
                        url(r'^combo/create/?$',
                            views.create_combo),

# events   - not implemented, might not be
                        url(r'^event/(P<event_id>\d+)/?$', 
                            views.event), 


#volunteers
                        url(r'^volunteer/bid/?$',
                            views.create_volunteer),


#vendors 
                        url(r'^vendor/bid/?$',
                            views.create_vendor),

# site utility stuff
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
