def validate_profile(request, require=False):
    '''
    Return the user profile if any
    '''
    if request.user.is_authenticated():
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            if require:
                raise Http404
    else:
        return None


def validate_perms(request, perms):
    '''
    Validate that the requesting user has the stated permissions
    Returns valid profile if access allowed, raises 404 if not
    '''
    profile = validate_profile(request, require=True)
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    raise Http404