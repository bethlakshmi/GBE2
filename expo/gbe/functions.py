import gbe.models as conf
from django.http import Http404
from django.core.mail import EmailMessage
from django.contrib.auth.models import User, Group


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


def validate_perms(request, perms):
    '''
    Validate that the requesting user has the stated permissions
    Returns valid profile if access allowed, raises 404 if not
    '''
    profile = validate_profile(request, require=True)
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    raise Http404

'''
    Sends mail to a privilege group, designed for use by bid functions
    Will always send using default_from_email 
'''
def mail_to_group(subject, message, group_name):
    to_list = [user.email for user in User.objects.filter(groups__name=group_name)]
    msg = EmailMessage(subject, message, to_list)
    msg.send()
    return None