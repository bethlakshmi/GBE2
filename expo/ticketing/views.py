# 
# views.py - Contains Django Views for Ticketing
# edited by mdb 8/18/2014
#

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from ticketing.models import *
from ticketing.forms import *
from ticketing.brown_paper import *
import pytz

# Create your views here.

def index(request):
    '''
    Represents the view for the main screen.  This will eventually be the 
    equivalent of cost.php from the old site.
    '''
    
    ticket_items =  TicketItem.objects.all()
    
    context = {'ticket_items': ticket_items, 'user_id':request.user.id }
    return render(request, 'ticketing/index.html', context)
    
def ticket_items(request):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    if not request.user.is_authenticated():
        raise Http404

    if 'Ticketing - Admin' not in request.user.profile.privilege_groups:
        raise Http404
        
    if 'Import' in request.POST:
        import_ticket_items()
        
    ticket_items = TicketItem.objects.all()
    context = {'ticket_items' : ticket_items}
    return render(request, r'ticketing/ticket_items.tmpl', context)

def transactions(request):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise Http404
    
    count = -1
    error = ''
    
    if ('Sync' in request.POST):
        try:
            count = process_bpt_order_list()
        except Exception as e:
            error = 'Error processing transactions:  ' + str(e)
        
    transactions = Transaction.objects.all()
    purchasers = Purchaser.objects.all()
    sync_time = get_bpt_last_poll_time()
    
    context = {'transactions' : transactions, 'purchasers' : purchasers, 
        'sync_time' : sync_time, 'error' : error, 'count' : count}
    return render(request, r'ticketing/transactions.tmpl', context) 
    
    
def import_ticket_items():
    '''
    Function is used to initiate an import from BPT or other sources of 
    new Ticket Items.  It will not override existing items.
    '''
    import_item_list = get_bpt_price_list()
    db_item_list = TicketItem.objects.all()
    
    for i_item in import_item_list:
        if all(db_item.ticket_id != i_item.ticket_id for db_item in db_item_list):
            i_item.save()
            
def ticket_item_edit(request, item_id=None):
    '''
    Used to display a form for editing ticket, adding or removing ticket items.
    '''
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise Http404
        
    error = ''

    if (request.method == 'POST'):
    
        if 'delete_item' in request.POST:
            # Delete this item based on the item_id in the URL
            
            item = TicketItem.objects.filter(id=item_id)[0]
            if (item == None):
                return HttpResponseRedirect('/ticketing/ticket_items')
            
            # Check to see if ticket item is used in a transaction before deleting.
            
            trans_exists = False    
            for trans in Transaction.objects.all():
                print "%s %s" % (trans.ticket_item.ticket_id, item.ticket_id)
                if (trans.ticket_item.ticket_id == item.ticket_id):
                    trans_exists = True
                    break
            
            if (not trans_exists):
                item.delete()
                return HttpResponseRedirect('/ticketing/ticket_items')
            else:
                error = 'ERROR:  Cannot remove Ticket Item:  It is used in a Transaction.'
                form = TicketItemForm(instance=item)
                
        else:
            # save the item using the Forms API
    
            form = TicketItemForm(request.POST)
            if form.is_valid():
                form.save(str(request.user))
                form.save_m2m()
                return HttpResponseRedirect('/ticketing/ticket_items')
    else:
        if (item_id != None):
            item = get_object_or_404(TicketItem, id=item_id)
            form = TicketItemForm(instance=item)
        else:
            form = TicketItemForm()

    context = {'forms': [form,], 'error':error} 
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)

            
            
            
            
    
    
    
    
    
        

    
