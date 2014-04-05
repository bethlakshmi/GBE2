from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Bio, ActBid, ClassBid
from gbe.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.forms.models import inlineformset_factory

def index(request):
    events = Event.objects.all()[:5]
    template = loader.get_template("gbe/index.html")
    context = RequestContext (request, {'events_list':events})
    return HttpResponse(template.render(context))

def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'gbe/event.html', {'event':event})

@login_required
def bid(request, type, bid_id=None):   
	try:
		profile = request.user.profile
	except Profile.DoesNotExist:
		profile = Profile()
		profile.user_object = request.user

	# by default, the bid gets posted to the same URL
	editaction = "/editbid/"+type+"/"
	
	# editing a populated bid
	if bid_id:
		action = "/editbid/"+type+"/"+bid_id+"/"
        # to add a new bid type, add a case here
        # the model must of type Bid so we can check the bidder	
		if type == "act":
			bid = ActBid.objects.get(pk=bid_id)
			otherbids = ActBid.objects.filter(bidder=profile)
		elif type == "class":
			bid = ClassBid.objects.get(pk=bid_id)
			otherbids = ClassBid.objects.filter(bidder=profile).exclude(type = "Panel")
		elif type == "panel":
			bid = ClassBid.objects.get(pk=bid_id)
			otherbids = ClassBid.objects.filter(bidder=profile, type = "Panel")
		elif type == "vendor":
			bid = VendorBid.objects.get(pk=bid_id)
			otherbids = VendorBid.objects.filter(bidder=profile)
		else:
			return HttpResponseRedirect('/bid/'+type+'-error')

		# check values, if this isn't the bidder, redirect to empty form
		if bid.bidder.pk != profile.pk:
			bid_id = None
        
	# create an empty form
	if bid_id == None:
		action = "/bid/"+type+'/'

		# to add a new bid type, add a case here
		# the model must of type Bid  		
		if type == "act":
			bid = ActBid()
			otherbids = ActBid.objects.filter(bidder=profile)
		elif type == "class":
			bid = ClassBid()
			otherbids = ClassBid.objects.filter(bidder=profile).exclude(type = "Panel")
		elif type == "panel":
			bid = ClassBid()
			otherbids = ClassBid.objects.filter(bidder=profile, type = "Panel")
		elif type == "vendor":
			bid = VendorBid()
			otherbids = VendorBid.objects.filter(bidder=profile)
		else:
			return HttpResponseRedirect('/bid/'+type+'-error')
    
		bid.bidder = profile
		
	# Panels are never in "draft"
	if type == "panel":
		bid.state = "Submitted"
		
	if request.method =='POST':
		if type == "act":
			form = ActBidForm(request.POST, request.FILES, instance=bid, 
								initial={'profile':profile, 'bidid':bid.id})
		elif type == "class":
			form = ClassBidForm(request.POST, instance=bid, 
								initial={'profile':profile})
		elif type == "panel":
			form = PanelBidForm(request.POST, instance=bid, 
								initial={'profile':profile})
		elif type == "vendor":
			form = VendorBidForm(request.POST, instance=bid, 
								initial={'profile':profile})
		else:
			return HttpResponseRedirect('/bid/'+type+'-error')

		if form.is_valid():
			new = form.save(profile)
			return HttpResponseRedirect('/bid/'+type+'-thanks')
		else: 
			return render(request, 'bids/bid.html', { 'form': form, 'action':action,
				'otherbids':otherbids, 'editaction':editaction, 'state':bid.state, 'intro':'bids/'+type+'intro.html' })
	else:
		if type == "act":
			form = ActBidForm(instance=bid, initial={'name': profile.stage_name, 'bidid':bid.id,
						'email':request.user.email, 'onsite_phone':profile.onsite_phone} )
		elif type == "class":
			form = ClassBidForm(instance=bid, initial={'name': profile.stage_name, 
                     'email':request.user.email, 'onsite_phone':profile.onsite_phone} )
		elif type == "panel":
			form = PanelBidForm(instance=bid, initial={'name': profile.stage_name, 
                     'email':request.user.email, 'onsite_phone':profile.onsite_phone} )
		elif type == "vendor":
			form = VendorBidForm(instance=bid, initial={'name': profile.display_name, 
                     'email':request.user.email, 'onsite_phone':profile.onsite_phone} )
		else:
			return HttpResponseRedirect('/bid/'+type+'-error')


	return render(request, 'bids/bid.html', { 'form': form, 'action':action, 
        'otherbids':otherbids, 'editaction':editaction, 'state':bid.state, 'intro':'bids/'+type+'intro.html' })


    
@login_required
def bid_response(request,type,response):
	if response == "error":
		return render(request, 'bids/'+response+'.html')
	return render(request, 'bids/'+type+response+'.html')

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
            return render(request, 'gbe/update_profile.html', 
                      {'form': form})

    else:
        form = ParticipantForm( instance = profile, initial={'email':request.user.email, 
                     'first_name':request.user.first_name, 'last_name':request.user.last_name})
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

    

