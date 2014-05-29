# 
# views.py - Contains Django Views for Ticketing
# edited by mdb 5/28/2014
#

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from ticketing.models import *
from ticketing.forms import *
from ticketing.brown_paper import *

# Create your views here.

def index(request):
    '''
    Represents the view for the main screen.  This will eventually be the 
    equivalent of cost.php from the old site.
    '''
    
    context = {}
    return render(request, 'ticketing\index.html', context)

def ticket_items(request):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise Http404
        
    if ('Import' in request.POST):
        import_ticket_items()
        
    ticket_items = TicketItem.objects.all()
    context = {'ticket_items' : ticket_items}
    return render(request, r'ticketing\ticket_items.tmpl', context)

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
    Used to create a form for editing ticket, adding or removing ticket items.
    
    note:  we need to check if the item is a duplicate before saving... 
    
    '''
    
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise Http404
        
    if (item_id != None):
        item = get_object_or_404(TicketItem, id=item_id)
    
    if (request.method == 'POST'):
        form = TicketItemForm(request.POST)
    else:
        form = TicketItemForm()
        
        
        


    
    context = {'item_id': item_id, 'form': form}
    
    return render(request, r'ticketing\ticket_item_edit.tmpl', context)
    
    
'''
    if request.method=='POST':
        form = ClassProposalForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')  # where to?
        else:
            return render(request, 'gbe/class_proposal.tmpl',
                          { 'form' : form } )
    else:
        form = ClassProposalForm()
        return render (request, 'gbe/class_proposal.tmpl',
                       {'form' : form})
                       
                       
'''
    
            
            
            
            
    
    
    
    
    
        

    