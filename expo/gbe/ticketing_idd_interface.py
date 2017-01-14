# ticketing_idd.py - Interface Design Description (IDD) between GBE and
# TICKETING modules

# See documentation in https://github.com/bethlakshmi/GBE2/wiki/Ticketing-To-Do
# section:  "By Friday - needed for integration"
# - Betty 8/15
from expo.gbe_logging import logger
from ticketing.models import (
    BrownPaperEvents,
    RoleEligibilityCondition,
    TicketingEligibilityCondition,
    TicketItem,
    Transaction,
)
from gbe.models import (
    Conference,
)
from ticketing.brown_paper import *
from gbetext import *
from django.db.models import Count


def performer_act_submittal_link(user_id):
    '''
    defines the act submission url for BPT to be used for payment.
    In other words, this gives you a string that a given user should go
    to at BPT to pay the fee.
    user_id - the integer User ID of the user.
    returns - the URL string described above.
    '''
    act_sub_events = BrownPaperEvents.objects.filter(
        act_submission_event=True,
        conference=Conference.objects.filter(status="upcoming").first())
    if (act_sub_events.count() > 0):
        return ('http://www.brownpapertickets.com/event/ID-' +
                unicode(user_id) +
                '/' +
                act_sub_events[0].bpt_event_id)
    return None


def vendor_submittal_link(user_id):
    '''
    defines the vendor url for BPT to be used for payment.  In other words,
    this gives you a string that a given user should go to at BPT to pay the
    fee.
    user_id - the integer User ID of the user.
    returns - the URL string described above.
    '''
    vendor_events = BrownPaperEvents.objects.filter(
        vendor_submission_event=True,
        conference=Conference.objects.filter(status="upcoming").first())
    if (vendor_events.count() > 0):
        return ('http://www.brownpapertickets.com/event/ID-' +
                unicode(user_id) +
                '/' +
                vendor_events[0].bpt_event_id)
    return None


def verify_performer_app_paid(user_name, conference):
    '''
    Verifies if a user has paid his or her application fee.
    NOTE:  This function assumes that there is a record of the application,
    saved in the database with a status of "submitted", at the time the check
    is performed.
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the application submittal fee is
      paid
    '''
    from gbe.models import Act
    act_fees_purchased = 0
    acts_submitted = 0

    # First figure out how many acts this user has purchased
    for act_event in BrownPaperEvents.objects.filter(
            act_submission_event=True,
            conference=conference):
        for trans in Transaction.objects.all():
            trans_event = trans.ticket_item.ticket_id.split('-')[0]
            trans_user_name = trans.purchaser.matched_to_user.username
            if ((act_event.bpt_event_id == trans_event) and
                    (unicode(user_name) == trans_user_name)):
                act_fees_purchased += 1

    # Then figure out how many acts have already been submitted.
    acts_submitted = Act.objects.filter(
        submitted=True,
        conference=conference).count()
    logger.info("Purchased Count:  %s  Submitted Count:  %s" %
                (act_fees_purchased, acts_submitted))
    return act_fees_purchased > acts_submitted


def verify_vendor_app_paid(user_name, conference):
    '''
    Verifies user has paid a vendor submittal fee.
    NOTE:  This function assumes that there is a record of the application,
    saved in the database, with a status of "submitted", at the time the check
    is performed.
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the vendor submittal fee is paid
    '''
    from gbe.models import Vendor
    vendor_fees_purchased = 0
    vendor_apps_submitted = 0

    # First figure out how many vendor spots this user has purchased
    for vendor_event in BrownPaperEvents.objects.filter(
            vendor_submission_event=True,
            conference=conference):
        for trans in Transaction.objects.all():
            trans_event = trans.ticket_item.ticket_id.split('-')[0]
            trans_user_name = trans.purchaser.matched_to_user.username

            if ((vendor_event.bpt_event_id == trans_event) and
                    (unicode(user_name) == trans_user_name)):
                vendor_fees_purchased += 1

    # Then figure out how many vendor applications have already been submitted.
    vendor_apps_submitted = Vendor.objects.filter(
        submitted=True,
        conference=conference).count()
    logger.info("Purchased Count:  %s  Submitted Count:  %s" %
                (vendor_fees_purchased, vendor_apps_submitted))
    return vendor_fees_purchased > vendor_apps_submitted


def verify_event_paid(user_name, event_id):
    '''
    This is extra.  Verifies if a user has paid at least once for a given
    event.
    user_name - This is the user name of the user in question.
    event_id - six digit BPT number that indicates if given user has paid for
      given event.
    returns - true if the system recognizes the fee is paid
    '''
    for trans in Transaction.objects.all():
        trans_event = trans.ticket_item.ticket_id.split('-')[0]
        trans_user_name = trans.purchaser.matched_to_user.username

        if ((unicode(event_id) == trans_event) and
                (unicode(user_name) == trans_user_name)):
            return True
    return False


def get_purchased_tickets(user):
    '''
    get the tickets purchased by the given profile
    '''
    ticket_by_conf = []
    conferences = Conference.objects.exclude(
        status="completed").order_by('status')
    for conf in conferences:
        tickets = TicketItem.objects.filter(
            bpt_event__conference=conf,
            transaction__purchaser__matched_to_user=user).annotate(
                number_of_tickets=Count('transaction')).order_by('title')
        if tickets:
            ticket_by_conf.append({'conference': conf, 'tickets': tickets})
    return ticket_by_conf


def get_checklist_items_for_tickets(profile,
                                    conference,
                                    tickets):
    '''
    get the checklist items for a purchaser in the BTP
    '''
    checklist_items = []
    transactions = Transaction.objects.filter(
            purchaser__matched_to_user=profile.user_object)

    for ticket in set(tickets):
        items = []
        count = transactions.filter(ticket_item=ticket).count()
        if count > 0:
            for condition in TicketingEligibilityCondition.objects.filter(
                    tickets=ticket):
                if not condition.is_excluded(tickets, profile, conference):
                    items += [condition.checklistitem]
            if len(items) > 0:
                checklist_items += [{'ticket': ticket.title,
                                     'count': count,
                                     'items': items}]

    return checklist_items


def get_checklist_items_for_roles(profile, conference, tickets):
    '''
    get the checklist items for the roles a person does in this conference
    '''
    checklist_items = []

    for role in profile.get_roles(conference):
        items = []
        for condition in RoleEligibilityCondition.objects.filter(role=role):
            if not condition.is_excluded(tickets, profile, conference):
                items += [condition.checklistitem]

        if len(items) > 0:
            checklist_items += [{'role': role,
                                 'items': items}]

    return checklist_items


def get_checklist_items(profile, conference):
    '''
    get the checklist items for a person with a profile
    '''
    checklist_items = []

    tickets = TicketItem.objects.filter(
        bpt_event__conference=conference,
        transaction__purchaser__matched_to_user=profile.user_object).distinct()

    checklist_items += get_checklist_items_for_tickets(profile,
                                                       conference,
                                                       tickets)

    checklist_items += get_checklist_items_for_roles(profile,
                                                     conference,
                                                     tickets)

    return checklist_items
