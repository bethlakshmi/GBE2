from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Performer
from gbe.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
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

def view_profile(request, profile_id=None):
    if not request.user.is_authenticated():
        viewer_profile=None
    else:
        try:
            viewer_profile = request.user.profile
        except Profile.DoesNotExist:
            viewer_profile=None

    if profile_id:
        requested_profile = get_object_or_404(Profile, pk=profile_id)
    else:
        if viewer_profile:
            requested_profile=viewer_profile
        else:
            return HttpResponseRedirect("/")
    own_profile =  (viewer_profile == requested_profile)
    template = loader.get_template('gbe/view_profile.tmpl')
    context = RequestContext (request, {'profile':requested_profile, 
                                        'warnings':requested_profile.get_warnings(own_profile),
                                        'performers':requested_profile.get_performers(own_profile),
                                        'acts': requested_profile.get_acts(own_profile),
                                        'shows': requested_profile.get_shows(own_profile),
                                        'classes': requested_profile.is_teaching(own_profile)
                                })
    return HttpResponse(template.render(context))

    
@login_required
def register_as_performer(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/accounts/profile/")
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES)
        if form.is_valid():
            performer = form.save(commit=True)
            pid = profile.pk
            return HttpResponseRedirect("/profile/"+ str(pid))
        else:
            return render (request, 
                           'gbe/performer_edit.tmpl',
                           {'form':form})
    else:
        form = PersonaForm (initial= {'performer_profile' : profile,
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
            return HttpResponseRedirect('/profile/')  
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'form':form})
    else:
        form = ActBidForm(initial={'owner':profile})
        return render (request, 
                       'gbe/bid.tmpl',
                       {'form':form})


@login_required
def edit_act(request, act_id):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect ('accounts/profile/')
    if request.method == 'POST':
        form = ActForm(request.POST, initial = {fields:act.bid_fields})

def review_acts (request):
    '''
    Show a list of acts which need to be reviewed by the current user. 
    If user is not a reviewer, politely decline to show anything. 
    '''
    pass


@login_required
def bid_class(request):
    '''
    Propose a class. Bidder is volunteering to teach this class - we have to 
    confirm that they understand and accept this. 
    '''
    try:
        owner = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    teachers = owner.personae.all()
    if len (teachers) == 0 :
        return HttpResponseRedirect('/performer/create/')
    if request.method == 'POST':
        form = ClassBidForm(request.POST)
        if form.is_valid():
            new_class = form.save(commit=True)
            return HttpResponseRedirect('/profile')
        else:
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'form':form})
    else:
        form = ClassBidForm (initial = {'owner':owner, 'teachers':teachers})
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
            form.save(commit=True)
            return HttpResponseRedirect("/profile/"+str(request.user.profile.id))
        else:
            return render(request, 'gbe/update_profile.html', 
                      {'form': form})

    else:
        if profile.display_name.strip() == '':
            display_name = request.user.first_name + ' ' + request.user.last_name
        else:
            display_name = profile.display_name
        form = ParticipantForm( instance = profile, 
                                initial={'email':request.user.email, 
                                         'first_name':request.user.first_name, 
                                         'last_name':request.user.last_name,
                                         'display_name':display_name
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
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.clean_username()
            password = form.clean_password2()
            form.save()
            user = authenticate(username = username, 
                                password = password)
            login (request, user)
            profile_form = ProfileForm ( 
                initial = {'user_object' : user})
            return HttpResponseRedirect('/update_profile/')
    else:
        form = UserCreateForm()
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
  

