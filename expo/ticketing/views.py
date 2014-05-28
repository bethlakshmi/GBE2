# 
# views.py - Contains Django Views for Ticketing
# edited by mdb 5/9/2014
#

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.

def index(request):
    context = {}
    return render(request, 'ticketing\index.html', context)

def ticket_items(request):
    context = {}
    return render(request, 'ticketing\TicketItems.html', context)
