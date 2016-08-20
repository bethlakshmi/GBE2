from django.conf.urls import (
    patterns,
    url,
    include,
)
from django.contrib.auth.views import *

from gbe.views import (
    ActChangeStateView,
    AdminProfileView,
    AssignVolunteerView,
    BidActView,
    BidClassView,
    BidCostumeView,
    BiosTeachersView,
    ClassChangeStateView,
    CloneBidView,
    ConferenceVolunteerView,
    CostumeChangeStateView,
    CreateComboView,
    CreateEventView,
    CreateVendorView,
    CreateVolunteerView,
    EditActView,
    EditActTechInfoView,
    EditClassView,
    EditCostumeView,
    EditPersonaView,
    EditTroupeView,
    EditVendorView,
    EditVolunteerView,
    FashionFaireView,
    HandleUserContactEmailView,
    LandingPageView,
    LogoutView,
    ProfileView,
    ProposeClassView,
    PublishProposalView,
    RegisterView,
    RegisterPersonaView,
    ReviewActListView,
    ReviewActView,
    ReviewClassView,
    ReviewClassListView,
    ReviewCostumeView,
    ReviewCostumeListView,
    ReviewProfilesView,
    ReviewProposalListView,
    ReviewVendorView,
    ReviewVendorListView,
    ReviewVolunteerView,
    ReviewVolunteerListView,
    SubmitActView,
    UpdateProfileView,
    VendorChangeStateView,
    ViewActView,
    ViewClassView,
    ViewCostumeView,
    ViewTroupeView,
    ViewVendorView,
    ViewVolunteerView,
    VolunteerChangeStateView,

)

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding patter, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.

urlpatterns = patterns(
    '',
    #  landing page
    url(r'^gbe/?',
        LandingPageView, name='home'),

    #  profile
    url(r'^profile/?$',
        ProfileView, name='profile'),
    url(r'^profile/(\d+)/?$',
        ProfileView, name='profile_view'),

    #  bios
    url(r'^bios/teachers/?$',
        BiosTeachersView, name='bios_teacher'),

    #  acts
    url(r'^act/create/?$',
        BidActView, name='act_create'),
    url(r'^act/edit/(\d+)/?$',
        EditActView, name='act_edit'),
    url(r'^act/view/(\d+)/?$',
        ViewActView, name='act_view'),
    url(r'^act/review/(?P<object_id>\d+)/?$',
        ReviewActView.as_view(), name='act_review'),
    url(r'^act/review/?$',
        ReviewActListView, name='act_review'),
    url(r'^act/reviewlist/?$',
        ReviewActListView,
        name='act_review_list'),
    url(r'^act/submit/(\d+)/?$',
        SubmitActView, name='act_submit'),
    url(r'^act/changestate/(\d+)/?$',
        ActChangeStateView,
        name='act_changestate'),

    #  act tech info
    url(r'^acttechinfo/edit/(\d+)/?$',
        EditActTechInfoView,
        name='act_techinfo_edit'),

    #  classes
    url(r'^class/create/?$',
        BidClassView, name='class_create'),
    url(r'class/edit/(\d+)/?$',
        EditClassView, name='class_edit'),
    url(r'^class/view/(\d+)/?$',
        ViewClassView, name='class_view'),
    url(r'^class/review/(?P<object_id>\d+)/?$',
        ReviewClassView.as_view(), name='class_review'),
    url(r'^class/review/?$',
        ReviewClassListView, name='class_review'),
    url(r'^class/reviewlist/?$',
        ReviewClassListView, name='class_review_list'),
    url(r'^class/changestate/(\d+)/?$',
        ClassChangeStateView,
        name='class_changestate'),

    #  proposals
    url(r'^class/propose/?$',
        ProposeClassView,
        name='class_propose'),
    url(r'^classpropose/edit/?$',
        PublishProposalView,
        name='proposal_publish'),
    url(r'^classpropose/edit/(\d+)/?$',
        PublishProposalView,
        name='proposal_publish'),
    url(r'^classpropose/reviewlist/?$',
        ReviewProposalListView,
        name='proposal_review_list'),

    #  conference
    url(r'^conference/volunteer/?$',
        ConferenceVolunteerView,
        name='conference_volunteer'),

    #  personae
    url(r'^performer/create/?$',
        RegisterPersonaView, name='persona_create'),
    url(r'^persona/edit/(\d+)/?$',
        EditPersonaView, name='persona_edit'),
    url(r'^troupe/create/?$',
        EditTroupeView, name='troupe_create'),
    url(r'^troupe/edit/(\d+)/?$',
        EditTroupeView, name='troupe_edit'),
    url(r'^troupe/view/(\d+)/?$',
        ViewTroupeView, name='troupe_view'),
    url(r'^combo/create/?$',
        CreateComboView, name='combo_create'),

    #  volunteers
    url(r'^volunteer/bid/?$',
        CreateVolunteerView, name='volunteer_create'),
    url(r'^volunteer/view/(\d+)/?$',
        ViewVolunteerView, name='volunteer_view'),
    url(r'^volunteer/edit/(\d+)/?$',
        EditVolunteerView, name='volunteer_edit'),
    url(r'^volunteer/assign/(\d+)/?$',
        AssignVolunteerView, name='volunteer_assign'),

    url(r'^volunteer/review/(?P<object_id>\d+)/?$',
        ReviewVolunteerView.as_view(), name='volunteer_review'),
    url(r'^volunteer/review/(\d+)/?$',
        ReviewVolunteerView, name='volunteer_review'),
    url(r'^volunteer/review/?$',
        ReviewVolunteerListView,
        name='volunteer_review'),
    url(r'^volunteer/reviewlist/?$',
        ReviewVolunteerListView,
        name='volunteer_review_list'),
    url(r'^volunteer/changestate/(\d+)/?$',
        VolunteerChangeStateView,
        name='volunteer_changestate'),


    #  vendors
    url(r'^vendor/create/?$',
        CreateVendorView, name='vendor_create'),
    url(r'^vendor/edit/(\d+)/?$',
        EditVendorView, name='vendor_edit'),
    url(r'^vendor/view/(\d+)/?$',
        ViewVendorView, name='vendor_view'),
    url(r'^vendor/review/(?P<object_id>\d+)/?$',
        ReviewVendorView.as_view(), name='vendor_review'),
    url(r'^vendor/review/?$',
        ReviewVendorListView,
        name='vendor_review'),
    url(r'^vendor/reviewlist/?$',
        ReviewVendorListView,
        name='vendor_review_list'),
    url(r'^vendor/changestate/(\d+)/?$',
        VendorChangeStateView,
        name='vendor_changestate'),

    #  costumes
    url(r'^costume/create/?$',
        BidCostumeView, name='costume_create'),
    url(r'costume/edit/(\d+)/?$',
        EditCostumeView, name='costume_edit'),
    url(r'^costume/view/(\d+)/?$',
        ViewCostumeView, name='costume_view'),
    url(r'^costume/review/(?P<object_id>\d+)/?$',
        ReviewCostumeView.as_view(), name='costume_review'),
    url(r'^costume/review/?$',
        ReviewCostumeListView, name='costume_review'),
    url(r'^costume/reviewlist/?$',
        ReviewCostumeListView, name='costume_review_list'),
    url(r'^costume/changestate/(\d+)/?$',
        CostumeChangeStateView,
        name='costume_changestate'),

    url(r'^clone/(?P<bid_type>\w+)/(?P<bid_id>\d+)/?$',
        CloneBidView,
        name='clone_bid'),

    #  miscellaneous URLs
    url(r'^fashion_faire/$',
        FashionFaireView, name='fashion_faire'),

    #  create and schedule events
    url(r'^create_event/(?P<event_type>[-\w]+)/?$',
        CreateEventView, name='create_event'),

    #  site utility stuff
    url(r'^login/?$',
        login, name='login'),
    url(r'^logout/?$',
        LogoutView, name='logout'),
    url(r'^accounts/login/?$',
        login),
    url(r'^accounts/logout/?$', LogoutView),
    url(r'^accounts/register/?$',
        RegisterView, name='register'),
    url(r'update_profile/?$',
        UpdateProfileView, name='profile_update'),

    #  password reset
    url(r'^accounts/password/reset/?$',
        password_reset,
        {'post_reset_redirect':
         '/accounts/password/reset/done/'},
        name="password_reset"),
    url(r'^accounts/password/reset/done/?$',
        password_reset_done, name='password_reset_done'),
    url(r'^accounts/password/confirm/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm,
        {'post_reset_redirect':
         '/accounts/password/reset/complete/'},
        name="password_reset_confirm"),
    url(r'^accounts/password/reset/complete/?$',
        password_reset_complete),

    #  registration & user management
    url(r'^user_contact/?$',
        HandleUserContactEmailView,
        name='handle_user_contact_email'),
    url(r'^profile/manage/?$',
        ReviewProfilesView,
        name='manage_users'),
    url(r'^profile/admin/(\d+)/?$',
        AdminProfileView,
        name='admin_profile'),
    url(r'^profile/landing_page/(\d+)/?$',
        LandingPageView,
        name='admin_landing_page')
)
