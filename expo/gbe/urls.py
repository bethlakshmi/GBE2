from django.conf.urls import patterns, url
from django.contrib.auth.views import *
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
                        url(r'^profile/(\d+)/?$',
                            views.profile),
                        url(r'^profile/admin/(\d+)/?$',
                            views.admin_profile),
# acts
                        url(r'^act/create/?$',
                            views.bid_act),
                        url(r'^act/edit/(\d+)/?$',
                            views.edit_act),
                        url(r'^act/view/(\d+)/?$',
                            views.view_act),
                        url(r'^act/review/?$',
                            views.review_act_list),
                        url(r'^act/review/(\d+)/?$',
                            views.review_act),
                        url(r'^act/reviewlist/?$',
                            views.review_act_list),
                        url(r'^act/(?P<act_id>\d+)/?$', 
                            views.act),
                        url(r'^act/submit/(\d+)/?$',
                            views.submit_act),

# classes
                        url(r'^class/create/?$',
                            views.bid_class),
                        url(r'class/edit/(\d+)/?$', 
                            views.edit_class),                        
                        url(r'^class/propose/?$',
                            views.propose_class),
                        url(r'^class/review/?$',
                            views.review_class_list),
                        url(r'^class/review/(\d+)/?$',
                            views.review_class),
                        url(r'^class/reviewlist/?$',
                            views.review_class_list),


# personae
                        url(r'^performer/create/?$',
                            views.register_persona),
                        url(r'^persona/edit/(\d+)/?$',
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
                        url(r'^volunteer/review/?$',
                            views.review_volunteer_list),
                        url(r'^volunteer/review/(\d+)/?$',
                            views.review_volunteer),
                        url(r'^volunteer/reviewlist/?$',
                            views.review_volunteer_list),

#vendors 
                        url(r'^vendor/bid/?$',
                            views.create_vendor),

# site utility stuff
                        url(r'^login/?$', 
                            login),
                        url(r'^logout/?$', 
                            views.logout_view),
                        url(r'^accounts/login/?$', 
                            login), 
                        url(r'^accounts/logout/?$', 
                            views.logout_view),
                        url(r'^accounts/register/?$',
                            views.register),
                        url(r'update_profile/?$', 
                            views.update_profile),
                        url(r'^accounts/profile/?$', 
                            views.landing_page),
                         
# password reset 
                        url(r'^accounts/password/reset/?$',
                            password_reset,
                            {'post_reset_redirect' : '/accounts/password/reset/done/'},
                            name="password_reset"),
                        url(r'^accounts/password/reset/done/?$',
                            password_reset_done),
                        url(r'^accounts/password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 
                            password_reset_confirm, 
                            {'post_reset_redirect' : '/accounts/password/reset/complete/'},
                            name="password_reset_confirm"),
                        url(r'^accounts/password/reset/complete/?$', 
                            password_reset_complete)
                        
                        ) 
