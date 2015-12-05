from django.conf.urls import (
    patterns,
    url,
    include
)
from django.contrib.auth.views import *
from gbe import views

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding patter, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.

urlpatterns = patterns(
    '',
    #  landing page
    url(r'^gbe/?',
        views.landing_page,
        name='home'),
    url(r'index.html/?',
        views.landing_page),

    #  profile
    url(r'^profile/?$',
        views.profile, name='profile'),
    url(r'^profiles/?$',
        views.profiles, name='profiles'),
    url(r'^profile/(\d+)/?$',
        views.profile, name='profile_view'),

    #  bios
    url(r'^bios/staff/?$',
        views.bios_staff, name='bios_staff'),
    url(r'^bios/teachers/?$',
        views.bios_teachers, name='bios_teacher'),
    url(r'^/bios/volunteers/?$',
        views.bios_volunteer, name='bios_volunteer'),

    #  acts
    url(r'^act/create/?$',
        views.bid_act, name='act_create'),
    url(r'^act/edit/(\d+)/?$',
        views.edit_act, name='act_edit'),
    url(r'^act/view/(\d+)/?$',
        views.view_act, name='act_view'),
    url(r'^act/review/(\d+)/?$',
        views.review_act, name='act_review'),
    url(r'^act/review/?$',
        views.review_act_list, name='act_review'),
    url(r'^act/reviewlist/?$',
        views.review_act_list,
        name='act_review_list'),
    url(r'^act/(?P<act_id>\d+)/?$',
        views.act, name='act'),
    url(r'^act/submit/(\d+)/?$',
        views.submit_act, name='act_submit'),
    url(r'^act/changestate/(\d+)/?$',
        views.act_changestate,
        name='act_changestate'),

    #  act tech info
    url(r'^acttechinfo/edit/(\d+)/?$',
        views.edit_act_techinfo,
        name='act_techinfo_edit'),

    #  classes
    url(r'^class/create/?$',
        views.bid_class, name='class_create'),
    url(r'class/edit/(\d+)/?$',
        views.edit_class, name='class_edit'),
    url(r'^class/view/(\d+)/?$',
        views.view_class, name='class_view'),
    url(r'^class/review/(\d+)/?$',
        views.review_class, name='class_review'),
    url(r'^class/review/?$',
        views.review_class_list, name='class_review'),
    url(r'^class/reviewlist/?$',
        views.review_class_list, name='class_review_list'),
    url(r'^class/changestate/(\d+)/?$',
        views.class_changestate,
        name='class_changestate'),

    #  proposals
    url(r'^class/propose/?$',
        views.propose_class,
        name='class_propose'),
    url(r'^classpropose/edit/?$',
        views.review_proposal_list,
        name='proposal_publish'),
    url(r'^classpropose/edit/(\d+)/?$',
        views.publish_proposal,
        name='proposal_publish'),
    url(r'^classpropose/reviewlist/?$',
        views.review_proposal_list,
        name='proposal_review_list'),

    #  panel
    url(r'^panel/?$',
        views.panel_view, name='panel_view'),
    url(r'^panel/create/?$',
        views.panel_create, name='panel_create'),
    url(r'^panel/edit/(\d+)/?$',
        views.panel_edit, name='panel_edit'),
    url(r'^panel/delete/(\d+)/?$',
        views.panel_delete, name='panel_delete'),

    #  conference
    url(r'^conference/volunteer/?$',
        views.conference_volunteer,
        name='conference_volunteer'),

    #  ads
    url(r'^ad/list/?$',
        views.ad_list, name='ad_list'),
    url(r'^ad/create/?$',
        views.ad_create, name='ad_create'),
    url(r'^ad/view/(\d+)/?$',
        views.ad_view, name='ad_view'),
    url(r'^ad/edit/(\d+)/?$',
        views.ad_edit, name='ad_edit'),
    url(r'^ad/delete/(\d+)/?$',
        views.ad_delete, name='ad_delete'),

    #  personae
    url(r'^performer/create/?$',
        views.register_persona, name='persona_create'),
    url(r'^persona/edit/(\d+)/?$',
        views.edit_persona, name='persona_edit'),
    url(r'^troupe/create/?$',
        views.edit_troupe, name='troupe_create'),
    url(r'^troupe/edit/(\d+)/?$',
        views.edit_troupe, name='troupe_edit'),
    url(r'^troupe/view/(\d+)/?$',
        views.view_troupe, name='troupe_view'),
    url(r'^combo/create/?$',
        views.create_combo, name='combo_create'),

    #  volunteers
    url(r'^volunteer/bid/?$',
        views.create_volunteer, name='volunteer_create'),
    url(r'^volunteer/view/(\d+)/?$',
        views.view_volunteer, name='volunteer_view'),
    url(r'^volunteer/edit/(\d+)/?$',
        views.edit_volunteer, name='volunteer_edit'),
    url(r'^volunteer/review/(\d+)/?$',
        views.review_volunteer, name='volunteer_review'),
    url(r'^volunteer/review/?$',
        views.review_volunteer_list,
        name='volunteer_review'),
    url(r'^volunteer/reviewlist/?$',
        views.review_volunteer_list,
        name='volunteer_review_list'),
    url(r'^volunteer/changestate/(\d+)/?$',
        views.volunteer_changestate,
        name='volunteer_changestate'),
    url(r'^volunteer/?$',
        views.volunteer, name='volunteer'),
    #  plain volunteer is for users to use to volunteer
    #  to help with tech, classes, panels, etc.


    #  vendors
    url(r'^vendor/create/?$',
        views.create_vendor, name='vendor_create'),
    url(r'^vendor/edit/(\d+)/?$',
        views.edit_vendor, name='vendor_edit'),
    url(r'^vendor/view/(\d+)/?$',
        views.view_vendor, name='vendor_view'),
    url(r'^vendor/review/(\d+)/?$',
        views.review_vendor, name='vendor_review'),
    url(r'^vendor/review/?$',
        views.review_vendor_list,
        name='vendor_review'),
    url(r'^vendor/reviewlist/?$',
        views.review_vendor_list,
        name='vendor_review_list'),
    url(r'^vendor/changestate/(\d+)/?$',
        views.vendor_changestate,
        name='vendor_changestate'),

    #  costumes
    url(r'^costume/create/?$',
        views.bid_costume, name='costume_create'),
    url(r'costume/edit/(\d+)/?$',
        views.edit_costume, name='costume_edit'),
    url(r'^costume/view/(\d+)/?$',
        views.view_costume, name='costume_view'),
    url(r'^costume/review/(\d+)/?$',
        views.review_costume, name='costume_review'),
    # url(r'^costume/review/?$',
    #    views.review_costume_list, name='costume_review'),
    # url(r'^costume/reviewlist/?$',
    #    views.review_costume_list, name='costume_review_list'),
    # url(r'^costume/changestate/(\d+)/?$',
    #    views.costume_changestate,
    #    name='costume_changestate'),

    url(r'^clone/(?P<bid_type>\w+)/(?P<bid_id>\d+)/?$',
        views.clone_bid,
        name='clone_bid'),

    #  miscellaneous URLs
    url(r'^costume_display/?$',
        views.costume_display, name='costume_display'),
    url(r'^fashion_faire/$',
        views.fashion_faire, name='fashion_faire'),

    #  create and schedule events
    url(r'^create_event/(?P<event_type>[-\w]+)/?$',
        views.create_event, name='create_event'),

    #  site utility stuff
    url(r'^login/?$',
        login, name='login'),
    url(r'^logout/?$',
        views.logout_view, name='logout'),
    url(r'^accounts/login/?$',
        login),
    url(r'^accounts/logout/?$',
        views.logout_view),
    url(r'^accounts/register/?$',
        views.register, name='register'),
    url(r'update_profile/?$',
        views.update_profile, name='profile_update'),
    url(r'^special/?$',
        views.special, name='special'),

    #  password reset
    url(r'^accounts/password/reset/?$',
        password_reset,
        {'post_reset_redirect':
         '/accounts/password/reset/done/'},
        name="password_reset"),
    url(r'^accounts/password/reset/done/?$',
        password_reset_done, name='password_reset_done'),
    url(r'^accounts/password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm,
        {'post_reset_redirect':
         '/accounts/password/reset/complete/'},
        name="password_reset_confirm"),
    url(r'^accounts/password/reset/complete/?$',
        password_reset_complete),

    #  registration & user management
    url(r'^user_contact/?$',
        views.handle_user_contact_email,
        name='handle_user_contact_email'),
    url(r'^profile/manage/?$',
        views.review_profiles,
        name='manage_users'),
    url(r'^profile/admin/(\d+)/?$',
        views.admin_profile,
        name='admin_profile'),
    url(r'^profile/review_commitments/(\d+)/?$',
        views.review_user_commitments,
        name='review_user_commitments'),
    url(r'^profile/manage_user_tickets/(\d+)/?$',
        views.manage_user_tickets,
        name='manage_user_tickets'),
    url(r'^profile/landing_page/(\d+)/?$',
        views.landing_page,
        name='admin_landing_page')
)
