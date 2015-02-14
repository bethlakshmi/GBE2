import gbe.models as conf
from django.http import Http404
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.conf import settings

def validate_profile(request, require=False):
    '''
    Return the user profile if any
    '''
    if request.user.is_authenticated():
        try:
            return request.user.profile
        except conf.Profile.DoesNotExist:
            if require:
                raise Http404
    else:
        return None


def validate_perms(request, perms, require = True):
    '''
    Validate that the requesting user has the stated permissions
    Returns profile object if perms exist, False if not
    '''
    profile = validate_profile(request, require = False)
    if not profile:
        if require:
            raise Http404
        else:
            return False
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    if require:                # error out if permission is required
        raise Http404
    return False               # or just return false if we're just checking


'''
    Sends mail to a privilege group, designed for use by bid functions
    Will always send using default_from_email 
'''
def mail_to_group(subject, message, group_name):
    to_list = [user.email for user in User.objects.filter(groups__name=group_name)]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to_list)
    return None
