from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Performer, ActBid, ClassBid
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


def techinfo(request):
    form = TechInfoForm()
    return render(request, 
                  'gbe/techinfo.html', 
                  {'form':form})

def view_profile(request, profile_id):
    try:
        viewer_profile = request.user.profile
    except Profile.DoesNotExist:
        viewer_profile=None
    requested_profile = get_object_or_404(Profile, pk=profile_id)
    own_profile =  (viewer_profile == requested_profile)
    template = loader.get_template('gbe/view_profile.tmpl')
    context = RequestContext (request, {'profile':requested_profile, 
                                        'warnings':requested_profile.get_warnings(own_profile),
                                        'performers':requested_profile.get_performers(own_profile),
                                        'acts': requested_profile.get_acts(own_profile)
                                })
    return HttpResponse(template.render(context))

    
@login_required
def register_as_performer(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/accounts/profile/")
    if request.method == 'POST':
        form = IndividualPerformerForm(request.POST, request.FILES)
        if form.is_valid():
            performer = form.save(commit=True)
            pid = profile.pk
            return HttpResponseRedirect("/profile/"+ str(pid))
        else:
            return render (request, 
                           'gbe/performer_edit.tmpl',
                           {'form':form})
    else:
        form = IndividualPerformerForm (initial= {'performer_profile' : profile,
                                                  'contact' : profile } )
        return render(request, 
                      'gbe/performer_edit.tmpl',
                      {'form':form})
                      


@login_required
def bid_act(request):
    '''
    Create a proposed Act object. 
    '''
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    if request.method == 'POST':
        form = ActBidForm(request.POST)
        if form.is_valid():
            audio_info = AudioInfo()
            audio_info.title=form.fields['song_name']
            audio_info.artist=form.fields['artist']
            audio_info.duration=form.fields['duration']
            audio_info.save()
            lighting = LightingInfo()
            lighting.save()
            props= PropsInfo()
            props.save()

            tech_info = TechInfo()
            tech_info.audio = audio_info
            tech_info.lighting = lighting
            tech_info.props = props
            
            tech_info.save()
            act = form.save(commit=False)
            act.tech=tech_info
            act.accepted = False
            act.save()
            return HttpResponseRedirect('/profile/')  # do something reasonable here
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'form':form})
    else:
        form = ActBidForm(initial={'owner':profile})
        return render (request, 
                       'gbe/bid.tmpl',
                       {'form':form})

def review_act_bid(request, act_id):
    act = get_object_or_404(Act, pk=act_id)
    if request.method == 'POST':
        act.accepted = request.POST.accepted
        return HttpResponseRedirect('/') # show us the act, or success message, or something
    else:
        form = ActBidReviewForm(instance=act)
        return render (request, 
                       'gbe/bid.tmpl',
                       {'form':form})
                                

    
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
        if not profile.display_name:
            profile.display_name = request.user.first_name + ' ' + request.user.last_name
        form = ParticipantForm( instance = profile, 
                                initial={'email':request.user.email, 
                                         'first_name':request.user.first_name, 
                                         'last_name':request.user.last_name,
                                     })
        return render(request, 'gbe/update_profile.html', 
                      {'form': form})


def register (request):
    '''
    Allow a user to register with gbe. This should create both a user
    object and a profile. Currently, creates only the user object
    (profile produced by "update_profile")
    '''
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


def logout_view (request):
    '''
    End the current user's session. 
    '''
    # if there's any cleanup to do, do it here. 

    logout(request)
    return HttpResponseRedirect('/')

def test(request):
    return render(request, 'bids/index.html')
  

