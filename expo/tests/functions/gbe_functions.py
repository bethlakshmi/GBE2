from gbe.models import (
    Conference,
    Profile,
    User,
)
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import ConferenceFactory

def _user_for(user_or_profile):
    if type(user_or_profile) == Profile:
        user = user_or_profile.user_object
    elif type(user_or_profile) == User:
        user = user_or_profile
    else:
        raise ValueError("this function requires a Profile or User")
    return user


def login_as(user_or_profile, testcase):
    user = _user_for(user_or_profile)
    user.set_password('foo')
    user.save()
    testcase.client.login(username=user.username,
                          email=user.email,
                          password='foo')


def grant_privilege(user_or_profile, privilege):
    '''Add named privilege to user's groups. If group does not exist, create it
    '''
    user = _user_for(user_or_profile)
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

def current_conference():
    current_confs = Conference.objects.filter(
        status__in=('upcoming', 'ongoing'),
        accepting_bids=True)
    if current_confs.exists():
        return current_confs.first()
    return ConferenceFactory(status='upcoming',
                             accepting_bids=True)

def clear_conferences():
    Conference.objects.all().delete()

def reload(object):
    return type(object).objects.get(pk=object.pk)
