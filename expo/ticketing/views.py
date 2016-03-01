#
# views.py - Contains Django Views for Ticketing
# edited by mdb 8/18/2014
# updated by BB 7/26/2015
#

from expo.gbe_logging import logger
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from ticketing.models import *
from ticketing.forms import *
from ticketing.brown_paper import *
from gbe.functions import *
from gbe.models import Conference
import pytz


def index(request):
    '''
    Represents the view for the main screen.  This will eventually be the
    equivalent of cost.php from the old site.
    '''

    ticket_items = TicketItem.objects.all()

    context = {'ticket_items': ticket_items,
               'user_id': request.user.id,
               'site_name': get_current_site(request).name
               }
    return render(request, 'ticketing/purchase_tickets.tmpl', context)


def ticket_items(request, conference_choice=None):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    validate_perms(request, ('Ticketing - Admin', ))

    if 'Import' in request.POST:
        import_ticket_items()

    if conference_choice:
        events = BrownPaperEvents.objects.filter(
            conference__conference_slug=conference_choice)
    else:
        events = BrownPaperEvents.objects.exclude(
            conference__status='completed')

    conferences = Conference.objects.all()
    context = {'events': events,
               'conferences': conferences,
               'conference_choice':  conference_choice}
    return render(request, r'ticketing/ticket_items.tmpl', context)


def transactions(request):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    validate_perms(request, ('Ticketing - Transactions', ))

    count = -1
    error = ''

    if ('Sync' in request.POST):
        count = process_bpt_order_list()

    transactions = Transaction.objects.all()
    purchasers = Purchaser.objects.all()
    sync_time = get_bpt_last_poll_time()

    context = {'transactions': transactions,
               'purchasers': purchasers,
               'sync_time': sync_time,
               'error': error,
               'count': count}
    return render(request, r'ticketing/transactions.tmpl', context)


def import_ticket_items():
    '''
    Function is used to initiate an import from BPT or other sources of
    new Ticket Items.  It will not override existing items.
    '''
    import_item_list = get_bpt_price_list()
    db_item_list = TicketItem.objects.all()

    for i_item in import_item_list:
        if all(db_item.ticket_id != i_item.ticket_id
               for db_item in db_item_list):
            i_item.save()


def ticket_item_edit(request, item_id=None):
    '''
    Used to display a form for editing ticket, adding or removing ticket items.
    '''
    validate_perms(request, ('Ticketing - Admin', ))

    error = ''

    if (request.method == 'POST'):

        if 'delete_item' in request.POST:

            item = get_object_or_404(TicketItem, id=item_id)

            # Check to see if ticket item is used in a
            # transaction before deleting.

            trans_exists = False
            for trans in Transaction.objects.all():
                if (trans.ticket_item.ticket_id == item.ticket_id):
                    trans_exists = True
                    break

            if (not trans_exists):
                item.delete()
                return HttpResponseRedirect(
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls',
                        args=[str(item.bpt_event.conference.conference_slug)]))
            else:
                error = 'Cannot remove Ticket Item: %s \
                        It is used in a Transaction.' % item.ticket_id
                logger.error(error)
                form = TicketItemForm(instance=item)

        else:
            # save the item using the Forms API

            form = TicketItemForm(request.POST)
            if form.is_valid():
                item = form.save(str(request.user))
                form.save_m2m()
                return HttpResponseRedirect(
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls',
                        args=[str(item.bpt_event.conference.conference_slug)]))
    else:
        if (item_id is not None):
            item = get_object_or_404(TicketItem, id=item_id)
            form = TicketItemForm(instance=item)
        else:
            form = TicketItemForm()

    context = {'forms': [form], 'error': error, 'can_delete': True}
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)


def bptevent_edit(request, event_id):
    '''
    Used to display a form for editing events.
    Deleting and adding events should only be done by an Admin
    '''
    validate_perms(request, ('Ticketing - Admin', ))

    event = get_object_or_404(BrownPaperEvents, id=event_id)

    if (request.method == 'POST'):

        # save the item using the Forms API
        form = BPTEventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ticket_items',
                                                urlconf='ticketing.urls'))
        else:
            return render(request,
                          r'ticketing/ticket_item_edit.tmpl',
                          {'forms': [form], 'can_delete': False})

            # return render(request, r'ticketing/ticket_item_edit.tmpl')

    else:
        form = BPTEventForm(instance=event)

    context = {'forms': [form], 'can_delete': False}
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)
