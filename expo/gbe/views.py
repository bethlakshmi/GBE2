from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Performer
from gbe.forms import *
from gbe.ticketing_idd_interface import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.forms.models import inlineformset_factory
import gbe_forms_text
from ticketingfuncs import compute_submission
from django.core.urlresolvers import reverse
from duration import Duration



def validate_profile(request, require=False):
    '''
    Return the user profile if any
    '''
    if request.user.is_authenticated():
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            if require:
                raise Http404
    else:
        return None


def validate_perms(request, perms):
    '''
    Validate that the requesting user has the stated permissions
    Returns valid profile if access allowed, raises 404 if not
    '''
    profile = validate_profile(request, require=True)
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    raise Http404



def down(request):
    '''
    Static "Site down" notice. Simply refers user to a static template with 
    a message. 
    '''
    template = loader.get_template('down.tmpl')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

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
            context_dict['alerts']= landing_page_no_profile_alert
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
    viewer_profile = validate_profile(request, require = False)

    template = loader.get_template('gbe/landing_page.tmpl')
    if viewer_profile:
        context = RequestContext (request, 
                                  {'profile':viewer_profile, 
                                   'standard_context' : standard_context,
                                   'personae':viewer_profile.get_personae(),
                                   'troupes':viewer_profile.get_troupes(),
                                   'combos':viewer_profile.get_combos(),
                                   'acts': viewer_profile.get_acts(),
                                   'shows': viewer_profile.get_shows(),
                                   'classes': viewer_profile.is_teaching(),
                                   'vendors': Vendor.objects.filter(profile = viewer_profile),
                                   'volunteering': viewer_profile.get_volunteerbids(),
                                   'review_items': viewer_profile.bids_to_review(),
                                   'acceptance_states': acceptance_states,
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
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    submit_button = 'Save Persona'
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES)
        if form.is_valid():
            performer = form.save(commit=True)
            pid = profile.pk
            if request.GET.get('next', None):
                redirect_to = request.GET['next']
            else:
                redirect_to=reverse('home', urlconf='gbe.urls')
            return HttpResponseRedirect(redirect_to)
        else:
            return render (request, 'gbe/bid.tmpl',
                           {'forms': [form],
                            'nodraft': submit_button,
                            'page_title': page_title, 
                            'view_title':view_title, })
    else:
        form = PersonaForm (initial= {'performer_profile' : profile,
                                      'contact' : profile, 
                                      } )
        return render(request,'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title, 
                       'view_title':view_title})
             

@login_required
def edit_troupe(request, troupe_id=None):
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'
    submit_button = 'Save Troupe'
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update', urlconf='gbe.urls')+
                                    '?next='+
                                    reverse('troupe_create', urlconf='gbe.urls'))
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+
                                    '?next='+
                                    reverse('troupe_create', urlconf='gbe.urls'))
    if troupe_id:
        troupe = get_object_or_404(Troupe, resourceitem_id=troupe_id)

    else:
        troupe = Troupe();
        
    if troupe_id > 0 and troupe.contact != request.user.profile:
          return HttpResponseRedirect(reverse('troupe_view', 
                                              urlconf='gbe.urls', 
                                              args=[str(troupe_id)])) 

    if request.method == 'POST':
        form = TroupeForm(request.POST, request.FILES, instance=troupe)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            q = Profile.objects.filter(resourceitem_id=profile.resourceitem_id)
            form.fields['contact']= forms.ModelChoiceField(queryset=q,
                                                       empty_label=None,
                                                       label=persona_labels['contact']) 
            return render (request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       'view_header_text':troupe_header_text})
    else:
        form = TroupeForm(instance=troupe, initial={'contact':profile})
        q = Profile.objects.filter(resourceitem_id=profile.resourceitem_id)
        form.fields['contact']= forms.ModelChoiceField(queryset=q,
                                                       empty_label=None,
                                                       label=persona_labels['contact']) 
        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title, 
                       'view_title': view_title,
                       'view_header_text':troupe_header_text})
                                   
@login_required
def view_troupe(request, troupe_id=None):
    '''
    Show troupes to troupe members, only contact should edit. 
    '''
    
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update', urlconf='gbe.urls')+
                                    '?next='+
                                    reverse('troupe_create', urlconf='gbe.urls'))

    troupe = get_object_or_404(Troupe, resourceitem_id=troupe_id)
    form = TroupeForm(instance = troupe, prefix = 'The Troupe')
    owner = ParticipantForm(instance = profile, 
                            prefix = 'Troupe Contact')

    return render (request, 'gbe/bid_view.tmpl',
                   {'readonlyform': [form, owner]})
 
@login_required         
def create_combo(request):
    page_title = 'Manage Combo'
    view_title = 'Who is in this Combo?'
    submit_button = 'Save Combo'

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update', urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('troupe_create', urlconf='gbe.urls'))
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('troupe_create', urlconf='gbe.urls'))
    if request.method == 'POST':
        form = ComboForm(request.POST, request.FILES)
        if form.is_valid():
            troupe = form.save(commit=True)
            troupe_id = troupe.pk
            return HttpResponseRedirect(reverse('home'), urlconf='gbe.urls')
        else:
            return render (request, 'gbe/bid.tmpl',
                           {'forms': [form],
                            'nodraft': submit_button,
                            'page_title': page_title,
                            'view_title':view_title,
                            'view_header_text':combo_header_text})
    else:
        form = ComboForm(initial={'contact':profile})
        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title':view_title,
                       'view_header_text':combo_header_text })
                                   
    
@login_required
def edit_persona(request, persona_id):
    '''
    Modify an existing Persona object. 
    '''
    page_title = 'Manage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    submit_button = 'Save Persona'

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    persona = get_object_or_404 (Persona, resourceitem_id=persona_id)
    if persona.performer_profile != profile:
        raise Http404

    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES, instance=persona)
        if form.is_valid():
            performer = form.save(commit=True)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form],
                            'nodraft': submit_button,
                            'page_title': page_title,                             
                            'view_title': view_title, 
                        })
    else:
        form = PersonaForm(instance = persona)
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form],
                        'nodraft': submit_button,
                            'page_title': page_title,                            
                            'view_title': view_title, 
                    })  
                        

@login_required
def bid_act(request):
    '''
    Create a proposed Act object. 
    '''
    page_title = 'Propose Act'
    view_title = 'Propose an Act'
    fee_link = performer_act_submittal_link(request.user.id)
    form = ActEditForm(prefix='theact')
    audioform= AudioInfoForm(prefix='audio')
    lightingform= LightingInfoForm(prefix='lighting')
    stageform = StageInfoForm(prefix='stage')

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    personae = profile.personae.all()
    draft_fields = Act().bid_draft_fields
    
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('act_create', urlconf='gbe.urls'))
    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''
        if 'submit' in request.POST.keys():
            form = ActEditForm(request.POST, 
                          prefix='theact')
        else:
            form = ActEditDraftForm(request.POST, 
                          prefix='theact')	    
        if  form.is_valid():
            act = form.save(commit=False)
            techinfo = TechInfo()
            audioinfoform = AudioInfoForm(request.POST, prefix='theact')
            techinfo.audio = audioinfoform.save()
            stageinfoform = StageInfoForm(request.POST, prefix='theact')
            techinfo.stage = stageinfoform.save()
            lightinginfo = LightingInfo()
            lightinginfo.save()
            techinfo.lighting = lightinginfo
            techinfo.save()
            
            act.tech=techinfo
            act.submitted = False
            act.accepted = False
            act.save()
            if not act.performer:
                return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls') +
                                            '?next=' +
                                            reverse('act_edit', urlconf='gbe.urls', args=[str(act.id)]))

        else:
            fields, requiredsub = Act().bid_fields
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form ], 
                            'page_title': page_title,                            
                            'view_title': view_title,
                            'draft_fields': draft_fields,
                            'fee_link': fee_link,
                            'submit_fields': requiredsub
                    })  

        if 'submit' in request.POST.keys():
            problems = act.validation_problems_for_submit()
            if problems:
                return render (request,
                               'gbe/bid.tmpl',
                               {'forms':[form], 
                                'page_title': page_title,                            
                                'view_title': view_title,
                                'draft_fields': draft_fields,
                                'fee_link': fee_link,
                                'errors':problems})
                
            else:
                '''
                If this is a formal submit request, did they pay?
                They can't submit w/out paying
                '''
                if (verify_performer_app_paid(request.user.username)):
                    act.submitted = True
                    act.save()
                    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                else: 
                    page_title = 'Act Payment'
                    return render(request,'gbe/please_pay.tmpl',
                           {'link': fee_link,
                            'page_title': page_title
                            })
        else:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    else:
        form = ActEditForm(initial = {'owner':profile,
                                     'performer': personae[0]}, 
                                     prefix='theact')
        q = Performer.objects.filter(contact=profile)
        form.fields['performer']= forms.ModelChoiceField(queryset=q)

        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form], 
                        'page_title': page_title,                            
                        'view_title': view_title,
                        'fee_link': fee_link,
                        'draft_fields': draft_fields
                        })

@login_required
def edit_act(request, act_id):
    '''
    Modify an existing Act object. 
    '''
    page_title = 'Edit Act Proposal'
    view_title = 'Edit Your Act Proposal'
    fee_link = performer_act_submittal_link(request.user.id)
    form = ActEditForm(prefix='theact')

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))   


    act = get_object_or_404(Act,id=act_id)
    if act.performer.contact != profile:
        raise Http404

    audio_info = act.tech.audio
    stage_info = act.tech.stage
    draft_fields = Act().bid_draft_fields

    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''
        if 'submit' in request.POST.keys():
            form = ActEditForm(request.POST,  
                           instance=act, 
                           prefix = 'theact', 
                           initial = { 
                               'track_title':audio_info.track_title,
                               'track_artist':audio_info.track_artist,
                               'track_duration':audio_info.track_duration,
                               'act_duration':stage_info.act_duration
                           })
        else:
            form = ActEditDraftForm(request.POST,  
                           instance=act, 
                           prefix = 'theact', 
                           initial = { 
                               'track_title':audio_info.track_title,
                               'track_artist':audio_info.track_artist,
                               'track_duration':audio_info.track_duration,
                               'act_duration':stage_info.act_duration
                           })

        audioform = AudioInfoForm(request.POST, prefix='theact', instance=audio_info)
        stageform = StageInfoForm(request.POST, prefix='theact', instance=stage_info)

        if all( [form.is_valid(), 
                 audioform.is_valid(),
                 stageform.is_valid() ] ):

            tech = act.tech
            tech.audio = audioform.save()
            tech.stage = stageform.save()

            
            tech.save()
            form.save()
        else:
            fields, requiredsub = Act().bid_fields
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form],
                            'page_title': page_title,                            
                            'view_title': view_title, 
                            'draft_fields': draft_fields,
                            'fee_link': fee_link,
                            'submit_fields': requiredsub
                       })



        if 'submit' in request.POST.keys():
            problems = act.validation_problems_for_submit()
            if problems:
                return render (request,
                               'gbe/bid.tmpl',
                               {'forms':[form], 
                               'page_title': page_title,                            
                               'view_title': view_title,
                               'draft_fields': draft_fields,
                               'fee_link': fee_link,
                               'errors':problems})
            else:
                '''
                If this is a formal submit request, did they pay?
                They can't submit w/out paying
                '''
                if (verify_performer_app_paid(request.user.username)):
                    act.submitted = True
                    act.save()
                    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                else: 
                    page_title = 'Act Payment'
                    return render(request,'gbe/please_pay.tmpl',
                           {'link': fee_link,
                            'page_title': page_title
                            })
        else:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else:
        audio_info = act.tech.audio
        stage_info = act.tech.stage

        form = ActEditForm(instance = act, 
                           prefix='theact', 
                           initial = { 
                               'track_title':audio_info.track_title,
                               'track_artist':audio_info.track_artist,
                               'track_duration':audio_info.track_duration,
                               'act_duration':stage_info.act_duration
                           })
        q = Performer.objects.filter(contact=profile)
        form.fields['performer']= forms.ModelChoiceField(queryset=q)

 
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form],
                        'page_title': page_title,                            
                        'view_title': view_title,
                        'fee_link': fee_link,
                        'draft_fields': draft_fields
                        })
                    

@login_required
def view_act (request, act_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''

    act = get_object_or_404(Act, id=act_id)
    if act.performer.contact != request.user.profile:
        raise Http404
    audio_info = act.tech.audio
    stage_info = act.tech.stage
    actform = ActEditForm(instance = act, 
                          prefix='The Act', 
                          initial = { 
                              'track_title':audio_info.track_title,
                              'track_artist':audio_info.track_artist,
                              'track_duration':audio_info.track_duration,
                              'act_duration':stage_info.act_duration
                          })
    try:
        instance = Troupe.objects.get(pk=act.performer.id)
        performer = TroupeForm(instance = instance, 
                               prefix = 'The Troupe')
    except:
        performer = PersonaForm(instance = act.performer, 
                                prefix = 'The Performer(s)')
 

    return render (request, 'gbe/bid_view.tmpl',
                   {'readonlyform': [actform, performer]})
    
    
@login_required
def review_act (request, act_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    
    reviewer = validate_perms(request, ('Act Reviewers', ))

    act = get_object_or_404(Act,id=act_id)
    audio_info = act.tech.audio
    stage_info = act.tech.stage
    
    actform = ActEditForm(instance = act, 
                          prefix='The Act', 
                          initial = { 
                              'track_title':audio_info.track_title,
                              'track_artist':audio_info.track_artist,
                              'track_duration':audio_info.track_duration,
                              'act_duration':stage_info.act_duration
                          })
 
    performer = PersonaForm(instance = act.performer, 
                            prefix = 'The Performer(s)')

    
    if  'Act Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance = act)
        # This requires that the show be scheduled - seems reasonable in current workflow and lets me
        # order by date.  Also - assumes that shows are only scheduled once
        try:
            start=Show.objects.all().filter(scheduler_events__resources_allocated__resource__actresource___item=act)[0]
        except:
            start=""
        q = Show.objects.all().filter(scheduler_events__isnull=False).order_by('scheduler_events__starttime')
        actionform.fields['show'] = forms.ModelChoiceField(
        	                         queryset=q,
        	                         empty_label=None,
        	                         label='Pick a Show',
        	                         initial=start)
        actionURL = reverse('act_changestate', urlconf='gbe.urls', args=[act_id])
    else:
            actionform = False;
            actionURL = False;

    '''
    if user has previously reviewed the act, provide their review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=act_id, evaluator_id=reviewer.resourceitem_id)[0]
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
            return HttpResponseRedirect(reverse('act_review_list', urlconf='gbe.urls'))
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [actform, performer],
                           'reviewer':reviewer,
                           'form':form,
                           'actionform':actionform,
                           'actionURL': actionURL})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [actform, performer],
                        'reviewer':reviewer,
                        'form':form,
                        'actionform':actionform,
                        'actionURL': actionURL})

@login_required
def review_act_list (request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews 
    '''
    reviewer = validate_perms(request, ('Act Reviewers',))

    try:
        header = Act().bid_review_header
        acts = Act.objects.filter(submitted=True).order_by('accepted', 'performer')
        review_query = BidEvaluation.objects.filter(bid=acts).select_related('evaluator').order_by('bid', 'evaluator')
        rows = []
        for act in acts:
            bid_row = {}
            bid_row['bid'] = act.bid_review_summary
            bid_row['reviews'] = review_query.filter(bid=act.id).select_related('evaluator').order_by('evaluator')
            bid_row['id'] =  act.id
            bid_row['review_url'] = reverse('act_review', urlconf='gbe.urls', args=[act.id])
            rows.append(bid_row)
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows})

@login_required
def act_changestate (request, bid_id):
    '''
    Fairly specific to act - removes the act from all shows, and resets the act to the
    selected show (if accepted/waitlisted), and then does the regular state change
    NOTE: only call on a post request
    '''
    reviewer = validate_perms(request, ('Act Coordinator',))


    if request.method == 'POST':
        from scheduler.models import Event, ResourceAllocation, ActResource
        act = get_object_or_404(Act,id=bid_id)

        # Clear out previous castings, deletes ActResource and ResourceAllocation
        ActResource.objects.filter(_item=act).delete()
 
        # if the act has been accepted, set the show.
        if request.POST['show'] and (request.POST['accepted'] == '3' or request.POST['accepted'] == '2'):
            # Cast the act into the show by adding it to the schedule resource allocation
            show = get_object_or_404(Event,eventitem__event=request.POST['show'])
            casting = ResourceAllocation()
            casting.event = show
            actresource = ActResource(_item=act)
            actresource.save()
            casting.resource = actresource
            casting.save()
            
    return bid_changestate (request, bid_id, 'act_review_list')



@login_required
def submit_act(request, act_id):
    submitter = validate_profile(request, require=True)
    
    try:
        the_act = Act.objects.get(id=act_id)
    except Act.DoesNotExist:
        raise Http404
    if the_act not in submitter.get_acts():
        return render (request, 
                       'gbe/error.tmpl', 
                       {'error' : 'You don\'t own that act.'})
    else:
        the_act.submitted= True             # Should show a review screen with a submit button
        the_act.save()                      # but I want to review how bid review is working to 
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                                            # implementing

        

class_durations = {0:0, 1:60, 2:90,3:120}

@login_required
def bid_class(request):
    '''
    Propose a class. Bidder is volunteering to teach this class - we have to 
    confirm that they understand and accept this. 
    '''
    page_title = "Submit a Class"
    view_title = "Submit a Class"

    owner = validate_profile(request, require=True)
    
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if len (teachers) == 0 :
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('class_create', urlconf='gbe.urls'))
    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''
        if 'submit' in request.POST.keys():
            form = ClassBidForm(request.POST)
        else:
            form = ClassBidDraftForm(request.POST)

        if form.is_valid():
            new_class = form.save(commit=False)
            new_class.duration = Duration(minutes = new_class.length_minutes)
            new_class = form.save(commit=True)
            if 'submit' in request.POST.keys():
                if new_class.complete:
                    new_class.submitted=True                    
                    new_class.save()
                    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                else:
                    return render (request, 
                                   'gbe/bid.tmpl', 
                                   {'forms':[form], 
                                   ' page_title': page_title,                            
                                    'view_title': view_title,
                                    'draft_fields': draft_fields,
                                    'errors':['Cannot submit, class is not complete']})
            new_class.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            fields, requiredsub = Class().get_bid_fields
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form],
                            'page_title': page_title,                            
                            'view_title': view_title,
                            'draft_fields': draft_fields,
                            'submit_fields': requiredsub
                            })

    else:
        form = ClassBidForm (initial = {'owner':owner, 'teacher': teachers[0] })
        q = Persona.objects.filter(performer_profile_id=owner.resourceitem_id)
        form.fields['teacher']= forms.ModelChoiceField(queryset=q)

        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form], 
                        'page_title': page_title,
                        'view_title': view_title,
                        'draft_fields': draft_fields
                        })


    
def edit_class(request, class_id):
    '''
    Edit an existing class.
    '''
    page_title = "Edit Class"
    view_title = "Edit Your Class Proposal"

    owner = validate_profile(request, require=True)

    the_class = get_object_or_404(Class, id=class_id)
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if the_class.teacher not in teachers:
        raise Http404

    if request.method == 'POST':
        if 'submit' in request.POST.keys():
            form = ClassBidForm(request.POST, instance=the_class)
        else:
            form = ClassBidDraftForm(request.POST, instance=the_class)

        if form.is_valid():
            the_class = form.save(commit=False)
            the_class.duration = Duration(minutes = the_class.length_minutes)
            the_class = form.save(commit=True)

           
            if 'submit' in request.POST.keys():
                if the_class.complete:
                    the_class.submitted=True                    

                    the_class.save()
                    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                else:
                    return render (request, 
                                   'gbe/bid.tmpl', 
                                   {'forms':[form], 
                                    'page_title': page_title,                            
                                    'view_title': view_title,
                                    'draft_fields': draft_fields,
                                    'errors':['Cannot submit, class is not complete']})
            the_class.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            fields, requiredsub = Class().get_bid_fields
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form], 
                            'page_title': page_title,                            
                            'view_title': view_title, 
                            'draft_fields': draft_fields,
                            'submit_fields': requiredsub
                       })
    else:
        form = ClassBidForm (instance=the_class)
        draft_fields = Class().get_draft_fields
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form], 
                        'page_title': page_title,                            
                        'view_title': view_title,
                        'draft_fields': draft_fields
                        })

@login_required
def view_class (request, class_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''

    classbid = get_object_or_404(Class,id=class_id)
    if classbid.teacher.contact != request.user.profile:
        raise Http404
    classform = ClassBidForm(instance = classbid, prefix = 'The Class')
    teacher = PersonaForm(instance = classbid.teacher, 
                          prefix = 'The Teacher(s)')

    return render (request, 'gbe/bid_view.tmpl',
                   {'readonlyform': [classform, teacher]})
    

@login_required
def review_class (request, class_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''

    reviewer = validate_perms(request, ('Class Reviewers',))

    aclass = get_object_or_404(Class,id=class_id)
    classform = ClassBidForm(instance = aclass, prefix = 'The Class')
    teacher = PersonaForm(instance = aclass.teacher,
                                prefix = 'The Teacher(s)')

 
    if  'Class Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance = aclass)
        actionURL = reverse('class_changestate', urlconf='gbe.urls', args=[aclass.id])
    else:
            actionform = False;
            actionURL = False;
   
    '''
    if user has previously reviewed the class, provide their review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=class_id, evaluator_id=reviewer.resourceitem_id)[0]
    except:
        bid_eval = BidEvaluation(evaluator = reviewer, bid = aclass)

    # show class info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance = bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = aclass
            evaluation.save()
            return HttpResponseRedirect(reverse('class_review_list', urlconf='gbe.urls'))
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [classform, teacher],
                           'reviewer':reviewer,
                           'form':form,
                           'actionform':actionform,
                           'actionURL': actionURL})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        

        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [classform, teacher],
                        'reviewer':reviewer,
                        'form':form,
                        'actionform':actionform,
                        'actionURL': actionURL })

@login_required
def review_class_list (request):
    '''
    Show the list of class bids, review results,
    and give a way to update the reviews 
    '''

    reviewer = validate_perms(request, ('Class Reviewers', ))

    header = Class().bid_review_header
    classes = Class.objects.filter(submitted=True).order_by('accepted', 'title')
    review_query = BidEvaluation.objects.filter(bid=classes).select_related('evaluator').order_by('bid', 'evaluator')
    rows = []
    for aclass in classes:
        bid_row = {}
        bid_row['bid']=  aclass.bid_review_summary
        bid_row['reviews'] =  review_query.filter(bid=aclass.id).select_related('evaluator').order_by('evaluator')
        bid_row['id']=aclass.id
        bid_row['review_url'] = reverse('class_review', urlconf='gbe.urls', args=[aclass.id])
        rows.append(bid_row)

    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('class_review', urlconf='gbe.urls')})

@login_required
def class_changestate (request, bid_id):
    '''
    Because classes are scheduleable, if a class is rejected, or moved back to nodecision, then
    the scheduling information is removed from the class.
    '''

    reviewer = validate_perms(request, ('Class Coordinator', ))


    if request.method == 'POST':
        thisclass = get_object_or_404(Class,id=bid_id)

        # if the class has been rejected/no decision, clear any schedule items.
        if (request.POST['accepted'] == '0' or request.POST['accepted'] == '1'):
            from scheduler.models import Event

            try:
                sched_classes = Event.objects.filter(eventitem__event=thisclass.event_id).delete()
                
            except:
                return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please
            
    return bid_changestate (request, bid_id, 'class_review_list')




@login_required
def create_volunteer(request):
    page_title = 'Volunteer'
    view_title = "Volunteer at the Expo"

    profile = validate_profile(request, require = False)
    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('volunteer_create', urlconf='gbe.urls'))
    if request.method == 'POST':
        form = VolunteerBidForm(request.POST)
        if form.is_valid():
            volunteer = form.save()
            if 'submit' in request.POST.keys():
                volunteer.submitted = True
                volunteer.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form], 
                            'page_title': page_title,
                            'view_title': view_title,
                            'nodraft':'Submit'})
    else:
        form = VolunteerBidForm(initial = {'profile':profile,
                                           'title':'volunteer bid: '+ profile.display_name,
                                           'description':'volunteer bid',
                                           'submitted':True})
        return render (request, 
                       'gbe/bid.tmpl', 
                       {'forms':[form], 
                        'page_title': page_title,
                        'view_title': view_title,
                        'nodraft':'Submit'})
                            
@login_required
def view_volunteer (request, volunteer_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    
    volunteer = get_object_or_404(Volunteer,id=volunteer_id)
    if volunteer.profile != request.user.profile:
        raise Http404
    volunteerform = VolunteerBidForm(instance = volunteer, prefix = 'Volunteer Info')
    profile = ParticipantForm(instance = volunteer.profile,
                              initial= { 'email' : volunteer.profile.user_object.email, 
                                         'first_name' : volunteer.profile.user_object.first_name, 
                                         'last_name' : volunteer.profile.user_object.last_name},
                              prefix = 'Contact Info')    

    return render (request, 'gbe/bid_view.tmpl',
                   {'readonlyform': [volunteerform, profile]})

@login_required
def review_volunteer (request, volunteer_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    reviewer = validate_perms(request, ('Volunteer Coordinator',))


    volunteer = get_object_or_404(Volunteer,id=volunteer_id)
    volunteer_prof = volunteer.profile
    volform = VolunteerBidForm(instance = volunteer, prefix = 'The Volunteer')
    profile = ParticipantForm(instance = volunteer_prof,
                              initial= { 'email' : volunteer_prof.user_object.email, 
                                         'first_name' : volunteer_prof.user_object.first_name, 
                                         'last_name' : volunteer_prof.user_object.last_name},
                              prefix = 'Contact Info')

    
    '''
    if user has previously reviewed the bid, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=volunteer_id, evaluator_id=reviewer.resourceitem_id)[0]
    except:
        bid_eval = BidEvaluation(evaluator = reviewer, bid = volunteer)

    # show info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance = bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = volunteer
            evaluation.save()
            return HttpResponseRedirect(reverse('volunteer_review_list', urlconf='gbe.urls'))
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [volform],
                           'form':form})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [volform, profile],
                        'reviewer':reviewer,
                        'form':form})

 
@login_required
def review_volunteer_list (request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews 
    '''
    reviewer = validate_perms(request, ('Volunteer Reviewers',))


    header = Volunteer().bid_review_header
    volunteers = Volunteer.objects.filter(submitted=True)
    review_query = BidEvaluation.objects.filter(bid=volunteers).select_related('evaluator').order_by('bid', 'evaluator')
    rows = []
    for volunteer in volunteers:
        bid_row = {}
        bid_row['bid']= volunteer.bid_review_summary
        bid_row['reviews']= review_query.filter(bid=volunteer.id).select_related('evaluator').order_by('evaluator')
        bid_row['id'] = volunteer.id
        bid_row['review_url'] = reverse('volunteer_review', urlconf='gbe.urls', args=[volunteer.id])
        rows.append(bid_row)
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('volunteer_review', urlconf='gbe.urls') })
    
@login_required
def edit_volunteer (request, volunteer_id):
    page_title = "Edit Volunteer Bid"
    view_title = "Edit Submitted Volunteer Bid"

    reviewer = validate_perms(request, ('Volunteer Coordinator',))

    the_bid = get_object_or_404(Volunteer, id=volunteer_id)

    if request.method == 'POST':
        form = VolunteerBidForm(request.POST, instance=the_bid)

        if form.is_valid():
            the_bid = form.save(commit=True)
            return HttpResponseRedirect(reverse('volunteer_review', urlconf='gbe.urls'))
        else:
            return render (request, 
                           'gbe/bid.tmpl', 
                           {'forms':[form], 
                            'page_title': page_title,
                            'view_title': view_title,
                            'nodraft':'Submit'})
    else:
        if len(the_bid.availability.strip()) > 0:
            availability_initial = eval(the_bid.availability)
        else:
            availability_initial = []

        if len(the_bid.unavailability.strip()) > 0:
            unavailability_initial = eval(the_bid.unavailability)
        else:
            unavailability_initial = []

        if len(the_bid.interests.strip()) > 0:
            interests_initial = eval(the_bid.interests)
        else:
            interests_initial = []

        form = VolunteerBidForm(instance = the_bid,
                                initial={'availability': availability_initial,
                                         'unavailability': unavailability_initial,
                                         'interests': interests_initial})
        return render (request, 
                       'gbe/bid.tmpl', 
                       {'forms':[form], 
                        'page_title': page_title,
                        'view_title': view_title,
                        'nodraft':'Submit'})



@login_required
def delete_volunteer (request, volunteer_id):
    reviewer = validate_perms(request, ('Volunteer Coordinator',))
    the_bid = get_object_or_404(Volunteer, id=volunteer_id)
    the_bid.delete()
    return HttpResponseRedirect(reverse('volunteer_review', urlconf='gbe.urls'))


def review_vendor(request, vendor_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    reviewer = validate_perms(request, ('Vendor Reviewers',))

    vendor = get_object_or_404(Vendor,id=vendor_id)
    volform = VendorBidForm(instance = vendor, prefix = 'The Vendor')    
    if  'Vendor Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance = vendor)
        actionURL = reverse('vendor_changestate', urlconf='gbe.urls', args=[vendor_id])
    else:
            actionform = False;
            actionURL = False;
   
    '''
    if user has previously reviewed the act, provide his review for update
    '''

    bid_eval, created =BidEvaluation.objects.get_or_create(bid_id=vendor_id, 
                                                  evaluator_id=reviewer.resourceitem_id,
                                                  defaults = {})


    # show act info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance = bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = vendor
            evaluation.save()
            return HttpResponseRedirect(reverse('vendor_review_list', urlconf='gbe.urls'))
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [volform],
                           'reviewer':reviewer,
                           'form':form,
                           'actionform':actionform,
                           'actionURL': actionURL})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [volform],
                        'reviewer':reviewer,
                        'form':form,
                        'actionform':actionform,
                        'actionURL': actionURL})
    
 
@login_required
def review_vendor_list (request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews 
    '''
    reviewer = validate_perms(request, ('Vendor Reviewers',))

    header = Vendor().bid_review_header
    vendors = Vendor.objects.filter(submitted=True).order_by('accepted', 'title')
    review_query = BidEvaluation.objects.filter(bid=vendors).select_related('evaluator').order_by('bid', 'evaluator')
    rows = []
    for vendor in vendors:
        bid_row = {}
        bid_row['bid'] = vendor.bid_review_summary
        bid_row['reviews']= review_query.filter(bid=vendor.id).select_related('evaluator').order_by('evaluator')
        bid_row['id']= vendor.id
        bid_row['review_url']= reverse('vendor_review', 
                                       urlconf='gbe.urls', 
                                       args=[vendor.id])
        rows.append(bid_row)

    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('vendor_review', urlconf='gbe.urls')})

@login_required
def vendor_changestate (request, bid_id):
    '''
    The generic function to change a bid to a new state (accepted,
    rejected, etc.).  This can work for any Biddable class, but may
    be an add-on to other work for a given class type.
    NOTE: only call on a post request
    '''
    reviewer = validate_perms(request, ('Vendor Coordinator',))

    return bid_changestate (request, bid_id, 'vendor_review_list')


@login_required
def create_vendor(request):

    title = "Vendor Application"
    fee_link = vendor_submittal_link(request.user.id)

    profile = validate_profile(request, require='False')
    if not profile:
        return HttpResponseRedirect(reverse('accounts_profile', urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('vendor_create', urlconf='gbe.urls'))
    if request.method == 'POST':
        form = VendorBidForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save()
        else:
            return render (request,
                           'gbe/bid.tmpl', 
                           {'forms':[form], 
                            'page_title':title, 
                            'fee_link': fee_link,
                            'view_title':title})
        if 'submit' in request.POST.keys():
            problems = vendor.validation_problems_for_submit()
            if problems:
                return render (request,
                               'gbe/bid.tmpl',
                               {'forms':[form], 
                               'page_title': page_title,                            
                               'view_title': view_title,
                               'fee_link': fee_link,
                               'errors':problems})
            else:
                '''
                If this is a formal submit request, did they pay?
                They can't submit w/out paying
                '''
                if (verify_vendor_app_paid(request.user.username)):
                    vendor.submitted = True
                    vendor.save()
                    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                else: 
                    page_title = 'Vendor Payment'
                    return render(request,'gbe/please_pay.tmpl',
                           {'link': fee_link,
                            'page_title': page_title
                            })
        else:   #saving a draft
            if form.is_valid():
                vendor = form.save()
                return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else:
        form = VendorBidForm(initial = {'profile':profile,
                                        'physical_address':profile.address})
        return render (request, 
                       'gbe/bid.tmpl', 
                       {'forms':[form], 
                        'fee_link': fee_link,
                        'page_title': title,
                        'view_title':title})

@login_required
def edit_vendor(request, vendor_id):

    page_title = 'Edit Vendor Application'
    view_title = 'Edit Your Vendor Application'
    form = VendorBidForm(prefix='thebiz')
    fee_link = vendor_submittal_link(request.user.id)

    profile = validate_profile(request, require = False)

    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))

    vendor = get_object_or_404(Vendor, id=vendor_id)
    if vendor.profile != profile:
        raise Http404
 
    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''
        form = VendorBidForm(request.POST, request.FILES,
                           instance=vendor, 
                           prefix = 'thebiz')

        if form.is_valid():
            form.save()
#            return HttpResponseRedirect('/wtf')  <---  Yep, really fails.
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form],
                            'page_title': page_title,                            
                            'view_title': view_title, 
                            'fee_link': fee_link
                            })

        if 'submit' in request.POST.keys():
            problems = vendor.validation_problems_for_submit()
            if problems:
                return render (request,
                               'gbe/bid.tmpl',
                               {'forms':[form], 
                               'page_title': page_title,                            
                               'view_title': view_title,
                               'fee_link': fee_link,
                               'errors':problems})
            else:
                '''
                If this is a formal submit request, did they pay?
                They can't submit w/out paying
                '''
                if (verify_vendor_app_paid(request.user.username)):
                    vendor.submitted = True
                    vendor.save()
                    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
                else: 
                    page_title = 'Vendor Payment'
                    return render(request,'gbe/please_pay.tmpl',
                           {'link': fee_link,
                            'page_title': page_title
                            })
        else:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else:
        if len(vendor.help_times.strip()) > 0:
            help_times_initial = eval(vendor.help_times)
        else:
            help_times_initial = []
        form = VendorBidForm(instance = vendor, 
                           prefix='thebiz',
                           initial = { 'help_times': help_times_initial })
 
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form],
                        'page_title': page_title,                            
                        'view_title': view_title,
                        'fee_link': fee_link
                        })
                    
@login_required
def view_vendor (request, vendor_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''

    vendor = get_object_or_404(Vendor,id=vendor_id)
    if vendor.profile != request.user.profile:
        raise Http404
    vendorform = VendorBidForm(instance = vendor, prefix = 'The Business')
    profile = ParticipantForm(instance = vendor.profile,
                              initial= { 'email' : request.user.email, 
                                         'first_name' : request.user.first_name, 
                                         'last_name' : request.user.last_name},
                              prefix = 'The Contact Info')    

    return render (request, 'gbe/bid_view.tmpl',
                   {'readonlyform': [vendorform, profile]})
    

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
    viewer_profile = validate_profile(request, require=True)
    if profile_id == None:
        requested_profile = viewer_profile
    else:
        requested_profile = get_object_or_404(Profile, id=profile_id)

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
def review_profiles(request):

    admin_profile = validate_perms(request, ('Registrar',))

    header = Profile().review_header
    profiles=Profile.objects.all()
    rows = []
    for aprofile in profiles:
        bid_row = {}
        bid_row['profile']=  aprofile.review_summary
        bid_row['id']=aprofile.resourceitem_id
        bid_row['review_url'] = reverse('admin_profile', urlconf='gbe.urls', args=[aprofile.resourceitem_id])
        bid_row['action1']="Update"
        rows.append(bid_row)

    
    return render (request, 'gbe/profile_review.tmpl',
                  {'header': header, 'rows': rows})
    


@login_required
def admin_profile(request, profile_id):

    admin_profile = validate_perms(request, ('Registrar',))

    user_profile=get_object_or_404(Profile, resourceitem_id=profile_id)

    if request.method == 'POST':
        form = ProfileAdminForm(request.POST, instance=user_profile)
        prefs_form = ProfilePreferencesForm(request.POST, 
                                            instance=user_profile.preferences,
                                            prefix='prefs')
        
        if form.is_valid():
            form.save(commit=True)
            if prefs_form.is_valid():
                prefs_form.save(commit=True)
                user_profile.preferences = prefs_form.save()
            user_profile.save()
            
            form.save()
            return HttpResponseRedirect(reverse('manage_users', urlconf='gbe.urls'))
    else:
        if user_profile.display_name.strip() == '':
            display_name = user_profile.user_object.first_name + ' ' + user_profile.user_object.last_name
        else:
            display_name = user_profile.display_name
        if len(user_profile.how_heard.strip()) > 0:
            how_heard_initial = eval(user_profile.how_heard)
        else:
            how_heard_initial = []

        form = ProfileAdminForm( instance = user_profile, 
                                initial= { 'email' : user_profile.user_object.email, 
                                           'first_name' : user_profile.user_object.first_name, 
                                           'last_name' : user_profile.user_object.last_name,
                                           'display_name' : display_name,
                                           'how_heard': how_heard_initial })

        if len(user_profile.preferences.inform_about.strip()) >0:
            inform_initial = eval(user_profile.preferences.inform_about)
        else:
            inform_initial = []
        prefs_form = ProfilePreferencesForm(prefix='prefs',
                                            instance=user_profile.preferences, 
                                            initial = {'inform_about': inform_initial })

        return render(request, 'gbe/update_profile.tmpl', 
                      {'left_forms': [form], 'right_forms':[prefs_form]})


@login_required
def update_profile(request):
    profile = validate_profile(request, require = False)
        
    if not profile:
        profile = Profile()
        profile.user_object = request.user
        profile.save()
        profile.preferences = ProfilePreferences()
        profile.preferences.save()
        profile.save()
    if request.method=='POST':
        form = ParticipantForm(request.POST, instance = profile)
        prefs_form = ProfilePreferencesForm(request.POST, 
                                            instance=profile.preferences,
                                            prefix='prefs')
        
        if form.is_valid():
            form.save(commit=True)
            if profile.display_name.strip() == '':
                profile.display_name = " ".join ([request.user.first_name.strip(), 
                                                  request.user.last_name.strip()])
            if profile.purchase_email.strip() == '':
                profile.purchase_email = request.user.email.strip()
            if prefs_form.is_valid():
                prefs_form.save(commit=True)
                profile.preferences = prefs_form.save()
            profile.save()
            
            form.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            return render(request, 'gbe/update_profile.tmpl',
                      {'left_forms': [form], 'right_forms':[prefs_form]})

    else:
        if profile.display_name.strip() == '':
            display_name = request.user.first_name + ' ' + request.user.last_name
        else:
            display_name = profile.display_name
        if len(profile.how_heard.strip()) > 0:
            how_heard_initial = eval(profile.how_heard)
        else:
            how_heard_initial = []
        form = ParticipantForm( instance = profile, 
                                initial= { 'email' : request.user.email, 
                                           'first_name' : request.user.first_name, 
                                           'last_name' : request.user.last_name,
                                           'display_name' : display_name,
                                           'how_heard': how_heard_initial })
        if len(profile.preferences.inform_about.strip()) >0:
            inform_initial = eval(profile.preferences.inform_about)
        else:
            inform_initial = []
        prefs_form = ProfilePreferencesForm(prefix='prefs',
                                            instance=profile.preferences, 
                                            initial = {'inform_about': inform_initial })

        return render(request, 'gbe/update_profile.tmpl', 
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
            return HttpResponseRedirect(reverse('profile_update', urlconf='gbe.urls'))
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
    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))




def propose_class (request):
    '''
    Handle suggestions for classes from the great unwashed 
    '''
    if request.method=='POST':
        form = ClassProposalForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  # where to?
        else:
            template = loader.get_template('gbe/class_proposal.tmpl')
            context = RequestContext (request, {'form': form})
            return HttpResponse(template.render(context))
    else:
        form = ClassProposalForm()
        template = loader.get_template('gbe/class_proposal.tmpl')
        context = RequestContext (request, {'form': form})
        return HttpResponse(template.render(context))
    
    
@login_required
def publish_proposal (request, class_id):
    '''
    Edit an existing proposal.  This is only available to the proposal reviewer.
    The only use here is to prep and publish a proposal, so it's a different user
    community than the traditional "edit" thread, so it's named "publish" instead.
    '''
    page_title = "Edit Proposal"
    view_title = "Edit & Publish Proposal"
    submit_button = "Save Proposal"

    reviewer = validate_perms(request, ('Class Coordinator',))

    the_class = get_object_or_404(ClassProposal, id=class_id)

    if request.method == 'POST':
        form = ProposalPublishForm(request.POST, instance=the_class)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('proposal_review_list', urlconf='gbe.urls'))
        else:
            template = loader.get_template('gbe/bid.tmpl')
            context = RequestContext (request, {'forms': [form],
                        'page_title': page_title,                            
                        'view_title': view_title,
                        'nodraft': submit_button})
            return HttpResponse(template.render(context))
    else:
        form = ProposalPublishForm(instance=the_class)
        template = loader.get_template('gbe/bid.tmpl')
        context = RequestContext (request, {'forms': [form],
                        'page_title': page_title,                            
                        'view_title': view_title,
                        'nodraft': submit_button})
        return HttpResponse(template.render(context))
    
    


@login_required
def review_proposal_list (request):
    '''
    Show the list of class bids, review results,
    and give a way to update the reviews 
    '''
    reviewer = validate_perms(request, ('Class Coordinator',))

    header = ClassProposal().bid_review_header
    classes = ClassProposal.objects.all().order_by('type', 'title')
    rows = []
    for aclass in classes:
        bid_row = {}
        bid_row['bid'] = aclass.bid_review_summary
        bid_row['id'] =  aclass.id
        bid_row['review_url'] = reverse('proposal_publish', urlconf='gbe.urls', args=[aclass.id])
        rows.append(bid_row)
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows})


def panel_create(request):
    '''
    View for creating a panel.  Boilerplate for now, more later.
    '''
    pass



def panel_view(request, panel_id):
    '''
    View for viewing a panel.
    Boilerplate.
    '''
    pass

def panel_edit(request, panel_id):
    '''
    View for editting a panel.
    Boilerplate.
    '''

    pass

def panel_delete(request, panel_id):
    '''
    View to delete a panel.  Deleting only marks panel as deleted, does not
    actually remove the data from the DB.
    Boilerplate.
    '''

    pass

def conference_volunteer(request):
    '''
    Volunteer to chair or sit on a panel or teach a class.
    Builds out from Class Proposal
    '''
    page_title = "Volunteer for the Conference"
    view_title = "Volunteer to be a Teacher or Panelist"

    owner = validate_profile(request, require = False)
    if not owner:
        return HttpResponseRedirect(reverse('profile_update', urlconf='gbe.urls'))
    
    presenters = owner.personae.all()

    classes = ClassProposal.objects.filter(display=True).order_by('type', 'title')
    # if there's no classes to work with, save the user the bother, and
    # just let them know
    if len(classes) == 0:
        return render (request, 'gbe/conf_volunteer_list.tmpl', 
                   {'view_title': view_title, 'page_title': page_title})
    if len (presenters) == 0 :
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls') + 
                                    '?next=' +
                                    reverse('conference_volunteer', urlconf='gbe.urls'))

    header = ClassProposal().presenter_bid_header
    header += ConferenceVolunteer().presenter_bid_header

    if request.method == 'POST':
        for aclass in classes:
            if str(aclass.id)+'-volunteering' in request.POST.keys():
                volunteer = ConferenceVolunteer.objects.filter(bid=aclass).filter(
                    presenter=request.POST.get(str(aclass.id)+'-presenter'))[0]

                form = ConferenceVolunteerForm(request.POST, instance=volunteer,
                                               prefix=str(aclass.id))
                if form.is_valid():
                    form.save()
                else:
                    return render (request, 'gbe/error.tmpl', 
                                   {'error': 'There was an error saving your presentation request, please try again.'})

        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else: 
        rows = []
        for aclass in classes:
            form = ConferenceVolunteerForm(initial = {'bid': aclass, 'presenter': presenters[0] },
                                           prefix=str(aclass.id))
            form.fields['presenter']= forms.ModelChoiceField(queryset=Performer.
                                                         objects.filter(contact=owner),
                                                         empty_label=None) 
            if aclass.type == "Class":
              form.fields['how_volunteer']= forms.ChoiceField(choices=class_participation_types)
              form.fields['how_volunteer'].widget.attrs['readonly'] = True
            elif aclass.type == "Panel":
              form.fields['how_volunteer']= forms.ChoiceField(choices=panel_participation_types,
                                                              initial="Panelist")
            else:
              form.fields['how_volunteer']= forms.ChoiceField(choices=conference_participation_types)
            form.fields['how_volunteer'].widget.attrs['class'] = 'how_volunteer'
            bid_row = {}
            bid_row['conf_item'] = aclass.presenter_bid_info
            bid_row['form'] = form
            rows.append(bid_row)

    return render (request, 'gbe/conf_volunteer_list.tmpl', 
                   {'view_title': view_title, 'page_title': page_title,
                    'header': header, 'rows': rows})

def ad_create(request):
    '''
    View to create an advertisement.
    Boilerplate
    '''

    pass

def ad_list(request):
    '''
    View to get a list of advertisements.
    Boilerplate
    '''

    pass

def ad_edit(request, ad_id):
    '''
    View to edit or alter an advertisement.
    Boilerplate
    '''

    pass

def ad_view(request, ad_id):
    '''
    View an advertisement.
    Boilerplate
    '''

    pass

def ad_delete(request, ad_id):
    '''
    Delete an advertisement.  Deletion does not remove the ad from the database,
    but marks it as deleted.
    Boilerplate
    '''

    pass

def bios_staff(request):
    '''
    Display the staff bios, pulled from their profiles.
    '''

    pass

def bios_teachers(request):
    '''
    Display the teachers bios, pulled from their profiles.
    '''

    pass

def bios_volunteer(request):
    '''
    Display the volunteer bios, pulled from their profiles.
    '''

    pass

def special(request):
    '''
    Edit special privledges.
    '''

    pass

def volunteer(request):
    '''
    Gateway to volunteering pages for users.  Either places links to individual
    pages for panel, class, tech, etc volunteering, or a more flexible widget to
    deal with all type of volunteering.
    '''

    pass

def costume_display(request):
    '''
    Costume Display.  May move this and a few other things into a separate app?
    '''

    pass

def fashion_faire(request):
    '''
    The Vintage Fashion Faire.  Glorified vendor list
    '''
    vendors = list(Vendor.objects.filter(accepted=3))
    vendor_rows = [vendors[i*3:i*3+3] for i in range(len(vendors)/3)]
    if len(vendors)%3>0:
        vendor_rows.append(vendors[-(len(vendors)%3):])
    template = 'gbe/fashionfair.tmpl'
    context = {'vendor_rows':vendor_rows}
    return render(request, template, context)
    
    
@login_required
def bid_changestate (request, bid_id, redirectURL):
    '''
    The generic function to change a bid to a new state (accepted, rejected, etc.).
    This can work for any Biddable class, but may be an add-on to other work for a given class type.
    NOTE: only call on a post request, and call from within a specific type of bid changestate
    function
    '''
    bid = get_object_or_404(Biddable, id=bid_id)
        
    # show class info and inputs for review
    if request.method == 'POST':
        form = BidStateChangeForm(request.POST, instance=bid)
        if form.is_valid():
            bid = form.save()
            return HttpResponseRedirect(reverse(redirectURL, urlconf='gbe.urls'))
        else:
            return render (request, 
                       'gbe/bid_review.tmpl',
                       {'actionform': False,
                        'actionURL': False })

    return HttpResponseRedirect(reverse(redirectURL, urlconf='gbe.urls'))

