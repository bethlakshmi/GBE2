from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Performer
from gbe.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.forms.models import inlineformset_factory

def index(request):
    '''
    one of two cases: 
      - unknown user (sign in or register/browse expo)
      - registered user (show objects/browse expo) 
    '''
    if request.user.is_authenticated():
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            context_dict['alerts']= "You seem to have screwed up the registration. Contact Scratch"
            return render_to_response ('gbe/index_unregistered_user.tmpl', context_dict)
        template = loader.get_template('gbe/index_registered_user.tmpl')
        context_dict['profile'] = profile
    else:
        pass
    context = RequestContext (request, context_dict)
    return HttpResponse(template.render(context))


def landing_page(request):
    standard_context = {}
    standard_context['events_list']  = Event.objects.all()[:5]
    if not request.user.is_authenticated():
        viewer_profile=None
    else:
        try:
            viewer_profile = request.user.profile
        except Profile.DoesNotExist:
            viewer_profile=None

    template = loader.get_template('gbe/landing_page.tmpl')
    if viewer_profile:
        context = RequestContext (request, 
                                  {'profile':viewer_profile, 
                                   'standard_context' : standard_context,
                                   'performers':viewer_profile.get_performers(),
                                   'acts': viewer_profile.get_acts(),
                                   'shows': viewer_profile.get_shows(),
                                   'classes': viewer_profile.is_teaching(),
                                   'review_items': viewer_profile.bids_to_review()
                               })
    else:
        context = RequestContext (request,
                                  {'standard_context' : standard_context })
    return HttpResponse(template.render(context))


def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'gbe/event.html', {'event':event})


def techinfo(request):
    form = TechInfoForm()
    return render(request, 
                  'gbe/techinfo.html', 
                  {'form':form})

    
@login_required
def register_persona(request, **kwargs):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/accounts/profile/")
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES)
        if form.is_valid():
            performer = form.save(commit=True)
            pid = profile.pk
#            if kwargs['redirect']:
#                redirect_to = kwargs['redirect']
            if request.GET.get('next', None):
                redirect_to = request.GET['next']
            else:
                redirect_to='/profile/'+str(pid)
            return HttpResponseRedirect(redirect_to)
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
             

def create_troupe(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/?next=/troupe/create')
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect('/performer/create/?next=/troupe/create')
    if request.method == 'POST':
        form = TroupeForm(request.POST, request.FILES)
        if form.is_valid():
            troupe = form.save(commit=True)
            troupe_id = troupe.pk
            return HttpResponseRedirect('/')
        else:
            return render (request, 
                           'gbe/performer_edit.tmpl',
                           {'form':form})
    else:
        form = TroupeForm(initial={'contact':profile})
        return render(request, 'gbe/performer_edit.tmpl',
                      {'form':form})
                                   
         
def create_combo(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/?next=/troupe/create')
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect('/performer/create/?next=/troupe/create')
    if request.method == 'POST':
        form = ComboForm(request.POST, request.FILES)
        if form.is_valid():
            troupe = form.save(commit=True)
            troupe_id = troupe.pk
            return HttpResponseRedirect('/')
        else:
            return render (request, 
                           'gbe/performer_edit.tmpl',
                           {'form':form})
    else:
        form = ComboForm(initial={'contact':profile})
        return render(request, 'gbe/performer_edit.tmpl',
                      {'form':form})
                                   
            



@login_required
def edit_persona(request, persona_id):
    '''
    Modify an existing Persona object. 
    '''
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    try:
        persona = Persona.objects.filter(id=persona_id)[0]
    except IndexError:
        return HttpResponseRedirect('/')  # just fail for now
    if persona.performer_profile != profile:
        return HttpResponseRedirect('/')  # just fail for now    
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            performer = form.save(commit=True)
            return HttpResponseRedirect('/')  
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form]})
    else:
        form = PersonaForm(instance = persona)
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form]})



@login_required
def bid_act(request):
    '''
    Create a proposed Act object. 
    '''
    form = ActBidForm(prefix='theact')
    audioform= AudioInfoBidForm(prefix='audio')
    lightingform= LightingInfoBidForm(prefix='lighting')
    propsform = PropsInfoBidForm(prefix='props')
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect("/performer/create?next=/act/create")
    if request.method == 'POST':
        form = ActBidForm(request.POST, 
                          prefix='theact')
        audioform= AudioInfoBidForm(request.POST, prefix='audio')
        lightingform= LightingInfoBidForm(request.POST, prefix='lighting')
        propsform = PropsInfoBidForm(request.POST, prefix='props')

        if  (form.is_valid() and 
            audioform.is_valid() and 
            lightingform.is_valid() and
            propsform.is_valid()):

            act = form.save(commit=False)
            audioinfo = audioform.save()
            lightinginfo = lightingform.save()
            propsinfo= propsform.save()

            tech_info = TechInfo()
            tech_info.audio = audioinfo
            tech_info.lighting = lightinginfo
            tech_info.props = propsinfo
            
            tech_info.save()
            
            act.tech=tech_info
            act.accepted = False
            act.save()
            if not act.performer:
                return HttpResponseRedirect('/performer/create?next=/act/edit/'+str(act.id))
            else:
                return HttpResponseRedirect('/')  
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form, audioform, lightingform, propsform], 
                           } )
    else:
        form = ActBidForm(initial = {'owner':profile,
                                     'performer': personae[0]}, 
                                     prefix='theact')
                          
        form.fields['performer']= forms.ModelChoiceField(queryset=Persona.
                                                         objects.filter(performer_profile=profile))
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form, audioform, lightingform, propsform]})

@login_required
def edit_act(request, act_id):
    '''
    Modify an existing Act object. 
    '''
    form = ActEditForm(prefix='theact')
    audioform= AudioInfoForm(prefix='audio')
    lightingform= LightingInfoForm(prefix='lighting')
    propsform = PropsInfoForm(prefix='props')
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    try:
        act = Act.objects.filter(id=act_id)[0]
        audio = act.tech.audio
        lighting = act.tech.lighting
        props = act.tech.props

    except IndexError:
        return HttpResponseRedirect('/')  # just fail for now
    if request.method == 'POST':
        form = ActBidForm(request.POST,  instance=act, prefix = 'theact')
        audioform= AudioInfoForm(request.POST, instance = audio,  prefix='audio')
        lightingform= LightingInfoForm(request.POST, instance = lighting, prefix='lighting')
        propsform = PropsInfoForm(request.POST, instance = props,  prefix='props')
        if (form.is_valid() and
            audioform.is_valid() and 
            lightingform.is_valid() and
            propsform.is_valid() ):
            audioform.save()
            lightingform.save()
            propsform.save()
            form.save()
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form, audioform, lightingform, propsform]})
        if 'submit' in request.POST.keys():
            if act.complete:
                act.submitted = True
                return HttpResponseRedirect('/')  
            else:
                return render (request,
                               'gbe/bid.tmpl',
                               {'forms':[form, audioform, lightingform, propsform], 
                                'errors':['Cannot submit incomplete act']})
        else:
            return HttpResponseRedirect('/')  
    else:
        form = ActEditForm(instance = act, prefix='theact')
        audioform= AudioInfoForm(prefix='audio', instance = audio)
        lightingform= LightingInfoForm(prefix='lighting', instance = lighting)
        propsform = PropsInfoForm(prefix='props', instance = props)
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form, audioform, lightingform, propsform]})



def review_acts(request):
    return render (request, 'gbe/error.tmpl', 
                   {'error' : "Not yet implemented"} )


def review_act (request, act_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # should go to 404?

    try:
        act = Act.objects.filter(id=act_id)[0]
        actform = ActBidForm(instance = act, prefix = 'The Act')
        audioform = AudioInfoBidForm(instance = act, prefix = 'Audio')
        performer = PersonaForm(instance = act.performer, 
                                prefix = 'The Performer(s)')
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    
    '''
    if user has previously reviewed the act, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=act_id, evaluator_id=reviewer.id)[0]
    except:
        bid_eval = BidEvaluation(evaluator = reviewer, bid = act)

    # show act info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance = bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = act
            evaluation.save()
            return HttpResponseRedirect('/act/reviewlist')
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [actform, audioform],
                           'form':form})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [actform, audioform, performer],
                        'reviewer':reviewer,
                        'form':form})

def review_act_list (request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # should go to 404?

    try:

        header = Act().bid_review_header
        acts = Act.objects.filter(submitted=True)
        review_query = BidEvaluation.objects.filter(bid=acts).select_related('evaluator').order_by('bid', 'evaluator')
        rows = []
        for act in acts:
            bid_row = []
            bid_row.append(("bid", act.bid_review_summary))
            bid_row.append(("reviews", review_query.filter(bid=act.id).select_related('evaluator').order_by('evaluator')))
            bid_row.append(("id", act.id))
            rows.append(bid_row)
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'review_path': '/act/review/'})



@login_required
def submit_act(request, act_id):
    try:
        submitter = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')  # don't bother with next redirect, they can't own this act!
    try:
        the_act = Act.objects.get(id=act_id)
    except Act.DoesNotExist:
        return HttpResponseRedirect('/')  # no such act
    if the_act not in submitter.get_acts():
        return render (request, 
                       'gbe/error.tmpl', 
                       {'error' : 'You don\'t own that act.'})
    else:
        the_act.submitted= True             # Should show a review screen with a submit button
        the_act.save()                      # but I want to review how bid review is working to 
        return HttpResponseRedirect('/')    # see if I can make use of existing code before 
                                            # implementing

        


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
        return HttpResponseRedirect('/performer/create?next=/class/create')
    if request.method == 'POST':
        form = ClassBidForm(request.POST)
        if form.is_valid():
            new_class = form.save(commit=True)
            return HttpResponseRedirect('/profile')
        else:
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form]})
    else:
        form = ClassBidForm (initial = {'owner':owner, })
        form.fields['teacher']= forms.ModelChoiceField(queryset=Persona.objects.filter(performer_profile_id=owner.id))

        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form]})
                                
def edit_class(request, class_id):
    '''
    Edit an existing class.
    '''
    try:
        owner = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    try:
        the_class = Class.objects.filter(id=class_id)[0]
    except IndexError:
        return HttpResponseRedirect('/')   # no class for this id, fail out
    teachers = owner.personae.all()
    if the_class.teacher not in teachers:
        return HttpResponseRedirect('/' )   # not a teacher for this class, fail out

    if request.method == 'POST':
        form = ClassEditForm(request.POST)
        if form.is_valid():
            new_class = form.save(commit=True)
            return HttpResponseRedirect('/profile')
        else:
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form]})
    else:
        form = ClassEditForm (instance=the_class)
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form]})


@login_required
def create_volunteer(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("accounts/profile?next=volunteer/create")
    if request.method == 'POST':
        form = VolunteerBidForm(request.POST)
        if form.is_valid():
            volunteer = form.save()
            return HttpResponseRedirect('/')
        else:
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form]})
    else:
        form = VolunteerBidForm(initial = {'profile':profile,
                                           'title':'volunteer bid: '+ profile.display_name,
                                           'description':'volunteer bid',
                                           'submitted':True})
        return render (request, 
                       'gbe/bid.tmpl', 
                       {'forms':[form]})
                            
@login_required
def review_volunteer (request, volunteer_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # should go to 404?

    try:
        volunteer = Volunteer.objects.filter(id=volunteer_id)[0]
        volform = VolunteerBidForm(instance = volunteer, prefix = 'The Volunteer')
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    
    '''
    if user has previously reviewed the act, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=volunteer_id, evaluator_id=reviewer.id)[0]
    except:
        bid_eval = BidEvaluation(evaluator = reviewer, bid = volunteer)

    # show act info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance = bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = volunteer
            evaluation.save()
            return HttpResponseRedirect('/volunteer/reviewlist')
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [volform],
                           'form':form})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [volform],
                        'reviewer':reviewer,
                        'form':form})


@login_required
def review_volunteer_list (request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # should go to 404?

    try:
        header = Volunteer().bid_review_header
        volunteers = Volunteer.objects.filter(submitted=True)
        review_query = BidEvaluation.objects.filter(bid=volunteers).select_related('evaluator').order_by('bid', 'evaluator')
        rows = []
        for volunteer in volunteers:
            bid_row = []
            bid_row.append(("bid", volunteer.bid_review_summary))
            bid_row.append(("reviews", review_query.filter(bid=volunteer.id).select_related('evaluator').order_by('evaluator')))
            bid_row.append(("id", volunteer.id))
            rows.append(bid_row)
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'review_path': '/volunteer/review/'})
    
@login_required
def create_vendor(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/accounts/profile/?next=vendor/create")
    if request.method == 'POST':
        form = VendorBidForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            return HttpResponseRedirect("/")
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form]})
    else:
        form = VendorBidForm(initial = {'profile':profile})
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form]})

@login_required
def bid_response(request,type,response):
    if response == "error":
        return render(request, 'bids/'+response+'.html')
    return render(request, 'bids/'+type+response+'.html')

def act(request, act_id):
    '''
    Act detail view. Display depends on state of act and identity of viewer. 
    '''
    act = get_object_or_404(Act, pk=act_id)
    return render(request, 'gbe/act.html', {'act':act})




def profile(request, profile_id=None):
    '''
    Display a profile. Display depends on user. If own profile, show everything and 
    link to edit. If admin user, show everything and link to admin. 
    For non-owners and unregistered, display TBD
    '''
    if request.user.is_authenticated:
        try: 
            viewer_profile = request.user.profile
        except Profile.DoesNotExist:
            return render (request, 'gbe/error.tmpl', 
                           {'error' : "Not signed in"} )
    try:
        requested_profile = Profile.objects.filter(id=profile_id)[0]
    except IndexError:
        requested_profile = viewer_profile  
    own_profile = requested_profile == viewer_profile  
    viewer_is_admin = viewer_profile.user_object.is_staff
    
    if viewer_is_admin:
        return render (request, 'gbe/admin_view_profile.tmpl', 
                       {'profile' : requested_profile,
                        'user' : requested_profile.user_object})
    else:
        return render (request, 'gbe/view_profile.tmpl', 
                       {'profile' : requested_profile,
                        'user' : requested_profile.user_object,                        
                        'viewer_is_admin':viewer_is_admin,
                        'own_profile': own_profile})
        
    
    
def profiles(request):
    '''
    Profiles browse view. If implemented, this should show profiles. Which ones 
    and how much information depends on the viewer. TBD
    '''
    return render (request, 'gbe/error.tmpl', 
                   {'error' : "Not yet implemented"})
    

@login_required
def admin_profile(request, profile_id):
    try:
        admin_profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # better redirect please
    if not admin_profile.user_object.is_staff:
        return HttpResponseRedirect('/')   # better redirect please
    try:
        user_profile=Profile.objects.filter(id=profile_id)[0]
    except IndexError:
        return HttpResponseRedirect('/')   # better redirect please
    if request.method == 'POST':
        form = ProfileAdminForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect('/profile/' + str(profile_id))
        else:
            return render(request, 'gbe/update_profile.html', 
                          {'form':form})
    else:
        form = ProfileAdminForm(instance=user_profile,
                              initial={'email':request.user.email, 
                                         'first_name':request.user.first_name, 
                                         'last_name':request.user.last_name,
                                     })
        return render(request, 'gbe/update_profile.html', 
                      {'form':form})


@login_required
def update_profile(request):
    try:
      profile = request.user.profile
 
    except Profile.DoesNotExist:
      profile = Profile()
      profile.user_object = request.user
      profile.save()
      profile.preferences = ProfilePreferences()
      profile.preferences.save()
    if request.method=='POST':
        form = ParticipantForm(request.POST, instance = profile)
        prefs_form = ProfilePreferencesForm(request.POST, instance=profile.preferences)
        if prefs_form.is_valid():
            prefs_form.save(commit=True)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, 'gbe/update_profile.html', 
                          {'forms': (form,prefs_form)})

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
        prefs_form = ProfilePreferencesForm()
        form.fields['how_heard'].widget= forms.CheckboxSelectMultiple(choices=how_heard_options)
        prefs_form.fields['inform_about'].widget = forms.CheckboxSelectMultiple(choices=inform_about_options)
        return render(request, 'gbe/update_profile.html', 
                      {'left_forms': [form], 'right_forms':[prefs_form]})


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




def propose_class (request):
    '''
    Handle suggestions for classes from the great unwashed 
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
  
