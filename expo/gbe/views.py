from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Bio, ActBid
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

@login_required
def bid_act(request, actbid_id=None):   
    try:
      profile = request.user.profile
    except Profile.DoesNotExist:
      profile = Profile()
      profile.user_object = request.user

    if actbid_id:
      act_bid = ActBid.objects.get(pk=actbid_id)
      action = "/bid/editact/"+actbid_id+"/"	
    else:
      act_bid = ActBid()
      action = "/bid/act/"
      
    act_bid.bidder = profile

    if request.method =='POST':
        form = ActBidForm(request.POST, request.FILES, instance=act_bid, initial={'profile':profile})
        if form.is_valid():
            new_act = form.save(profile)
            return HttpResponseRedirect('/bid/thankact')
    else:
        form = ActBidForm(instance=act_bid, initial={'name': profile.stage_name, 
                     'email':request.user.email, 'onsite_phone':profile.onsite_phone} )

    return render(request, 'bids/actbid.html', {
        'form': form, 'action':action
    })
    
@login_required
def bid_act_thanks(request):
    return render(request, 'bids/actthanks.html')

def act(request, act_id):
    act = get_object_or_404(Act, pk=act_id)
    return render(request, 'gbe/act.html', {'act':act})

@login_required
def profile(request):
    return render(request, 'gbe/profile.html')
    
@login_required
def update_profile(request):
    try:
      profile = request.user.profile
    except Profile.DoesNotExist:
      profile = Profile()
      profile.user_object = request.user
    
    if request.method=='POST':
        form = ParticipantForm(request.POST, instance = profile)
        if form.is_valid():
            new_user=form.save()
            return HttpResponseRedirect("/accounts/profile/")
    else:
        form = ParticipantForm( instance = profile)
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

    

