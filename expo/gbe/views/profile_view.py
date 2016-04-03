from expo.gbe_logging import log_func
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.functions import validate_profile
from gbe.models import Profile
@log_func
def ProfileView(request, profile_id=None):
    '''
    Display a profile. Display depends on user. If own profile, show
    everything and link to edit. If admin user, show everything and
    link to admin.
    For non-owners and unregistered, display TBD
    '''
    viewer_profile = validate_profile(request, require=True)
    if profile_id is None:
        requested_profile = viewer_profile
    else:
        requested_profile = get_object_or_404(Profile, id=profile_id)

    own_profile = requested_profile == viewer_profile
    viewer_is_admin = viewer_profile.user_object.is_staff

    if viewer_is_admin:
        return render(request, 'gbe/admin_view_profile.tmpl',
                      {'profile': requested_profile,
                       'user': requested_profile.user_object})
    else:
        return render(request, 'gbe/view_profile.tmpl',
                      {'profile': requested_profile,
                       'user': requested_profile.user_object,
                       'viewer_is_admin': viewer_is_admin,
                       'own_profile': own_profile})
