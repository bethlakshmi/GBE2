from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Performer
from gbe.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

def index(request):
    events = Event.objects.all()[:5]
    template = loader.get_template("gbe/index.html")
    context = RequestContext (request, {'events_list':events})
    return HttpResponse(template.render(context))

def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'gbe/event.html', {'event':event})

def bid_act(request, act_id=0):      
    if request.method =='POST':
        form = ActForm(request.POST)
        if form.is_valid():
            new_act = form.save()
            return HttpResponseRedirect('/act/'+new_act.id)
    else:
        form = ActForm()

    return render(request, 'bids/actbid.html', {
        'form': form,
    })

def act(request, act_id):
    act = get_object_or_404(Act, pk=act_id)
    return render(request, 'gbe/act.html', {'act':act})

@login_required
def profile(request):
    return render(request, 'gbe/profile.html')
    
@login_required
def update_profile(request):
    if request.method=='POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            new_user=form.save()
            return HttpResponseRedirect("/accounts/profile/")
    else:
        form = ParticipantForm( initial = 
                                {'user_object':request.user})
        return render(request, 'gbe/update_profile.html', 
                      {'form': form})


def register (request):
    if request.method=='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile_form = ProfileForm ( 
                initial = {'user_object' : user})
            logout(request)
            return HttpResponseRedirect('/update_profile/')
    else:
        form = RegistrationForm()
    return render(request, 'gbe/register.html', {
        'form':form})

    

