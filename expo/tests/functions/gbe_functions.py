from gbe.models import (
    Conference,
    Profile,
)
from django.contrib.auth.models import (
    Group,
    User,
)
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
)

from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    TransactionFactory,
    TicketItemFactory,
    PurchaserFactory,
)
from gbe_forms_text import rank_interest_options


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
    return 'I forgot my username or password!' in response.content


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


def assert_alert_exists(response, tag, label, text):
    alert_html = '<div class="alert alert-%s">\n' + \
        '          <a href="#" class="close" data-dismiss="alert" ' + \
        'aria-label="close">&times;</a>\n' + \
        '          <strong>%s:</strong> %s\n' \
        '	</div>'
    assert alert_html % (tag, label, text) in response.content


def assert_rank_choice_exists(response, interest, selection=None):
    assert '<label for="id_%d-rank">%s:</label>' % (
        interest.pk,
        interest.interest) in response.content
    assert '<select id="id_%d-rank" name="%d-rank">' % (
        interest.pk,
        interest.pk) in response.content
    for value, text in rank_interest_options:
        if selection and selection == value:
            assert '<option value="%d" selected="selected">%s</option>' % (
                value, text) in response.content
        else:
            assert '<option value="%d">%s</option>' % (
                value, text) in response.content


def assert_hidden_value(response, field_id, name, value, max_length=None):
    if max_length:
        x = '<input id="%s" maxlength="%d" name="%s" type="hidden" ' + \
            'value="%s" />'
        assert x % (
            field_id, max_length, name, value) in response.content
    else:
        assert '<input id="%s" name="%s" type="hidden" value="%s" />' % (
            field_id, name, value) in response.content


def assert_has_help_text(response, help_text):
    assert '<span class="dropt" title="Help">' in response.content
    assert '<img src= "/static/img/question.png" alt="?"/>' in response.content
    assert ('<span style="width:200px;float:right;text-align:left;">'
            in response.content)
    assert help_text in response.content
    assert '</span>' in response.content


def assert_interest_view(response, interest):
    assert ('<label for="id_Volunteer Info-interest_id-%d">%s:</label>' %
            (interest.pk, interest.interest.interest)
            in response.content)
    assert interest.rank_description in response.content
    if interest.interest.help_text:
        assert_has_help_text(response, interest.interest.help_text)


def make_act_app_purchase(conference, user_object):
    purchaser = PurchaserFactory(
        matched_to_user=user_object)
    transaction = TransactionFactory(purchaser=purchaser)
    transaction.ticket_item.bpt_event.conference = conference
    transaction.ticket_item.bpt_event.act_submission_event = True
    transaction.ticket_item.bpt_event.bpt_event_id = "111111"
    transaction.ticket_item.bpt_event.save()
    return transaction


def post_act_conflict(conference, performer, data, url, testcase):
    original = ActFactory(
        b_conference=conference,
        performer=performer)
    login_as(performer.performer_profile, testcase)
    data['theact-b_title'] = original.b_title
    data['theact-b_conference'] = conference.pk
    response = testcase.client.post(
        url,
        data=data,
        follow=True)
    return response, original


def make_vendor_app_purchase(conference, user_object):
    bpt_event = BrownPaperEventsFactory(conference=conference,
                                        vendor_submission_event=True)
    purchaser = PurchaserFactory(matched_to_user=user_object)
    ticket_id = "%s-1111" % (bpt_event.bpt_event_id)
    ticket = TicketItemFactory(ticket_id=ticket_id)
    transaction = TransactionFactory(ticket_item=ticket,
                                     purchaser=purchaser)


def bad_id_for(cls):
    objects = cls.objects.all()
    if objects.exists():
        return objects.latest('pk').pk + 1
    return 1
