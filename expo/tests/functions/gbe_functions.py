from  gbe.models import (
    Profile,
    User,
)
from django.contrib.auth.models import Group

def user_for(user_or_profile):
    if type(user_or_profile) == Profile:
        user = user_or_profile.user_object
    elif type(user_or_profile) == User:
        user = user_or_profile
    else:
        raise ValueError("login_as requires a Profile or User")
    return user


def login_as(user_or_profile, testcase):
    user = user_for(user_or_profile)
    user.set_password('foo')
    user.save()
    testcase.client.login(email=user.email, password='foo')


def grant_privilege(user_or_profile, privilege):
    '''Add named privilege to user's groups. If group does not exist, create it
    '''
    user = user_for(user_or_profile)
    try:
        g, _ = Group.objects.get_or_create(name=privilege)
    except:
        g = Group(name=privilege)
        g.save()
    if g in user.groups.all():
        return
    else:
        user.groups.add(g)


def is_login_page(response):
    return 'I forgot my password!' in response.content


def is_profile_update_page(response):
    return 'Your privacy is very important to us' in response.content


def location(response):
    response_dict = dict(response.items())
    return response_dict['Location']
