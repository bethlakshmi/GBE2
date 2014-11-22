from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
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
                                   'personae':viewer_profile.get_personae(),
                                   'troupes':viewer_profile.get_troupes(),
                                   'combos':viewer_profile.get_combos(),
                                   'acts': viewer_profile.get_acts(),
                                   'shows': viewer_profile.get_shows(),
                                   'classes': viewer_profile.is_teaching(),
                                   'vendors': Vendor.objects.filter(profile = viewer_profile),
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
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    submit_button = 'Save Persona'
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
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
             

def edit_troupe(request, troupe_id=None):
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'
    submit_button = 'Save Troupe'
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls')+'?next='+reverse('troupe_create', urlconf='gbe.urls'))
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+'?next='+reverse('troupe_create', urlconf='gbe.urls'))
    if troupe_id:
        try:
            troupe = Troupe.objects.filter(resourceitem_id=troupe_id)[0]
        except:
            return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls')+'?next='+reverse('troupe_create', urlconf='gbe.urls'))
    else:
        troupe = Troupe();
        
    if request.method == 'POST':
        form = TroupeForm(request.POST, request.FILES, instance=troupe)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            form.fields['contact']= forms.ModelChoiceField(queryset=Profile.
                                                       objects.filter(resourceitem_id=profile.id),
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
        form.fields['contact']= forms.ModelChoiceField(queryset=Profile.
                                                       objects.filter(resourceitem_id=profile.resourceitem_id),
                                                       empty_label=None,
                                                       label=persona_labels['contact']) 
        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title, 
                       'view_title': view_title,
                       'view_header_text':troupe_header_text})
                                   
         
def create_combo(request):
    page_title = 'Manage Combo'
    view_title = 'Who is in this Combo?'
    submit_button = 'Save Combo'

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls')+'?next='+reverse('troupe_create', urlconf='gbe.urls'))
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+'?next='+reverse('troupe_create', urlconf='gbe.urls'))
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
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    try:
        persona = Persona.objects.filter(resourceitem_id=persona_id)[0]
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  # just fail for now
    if persona.performer_profile != profile:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  # just fail for now    
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
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    personae = profile.personae.all()
    draft_fields = Act().bid_draft_fields
    
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+'?next='+reverse('act_create', urlconf='gbe.urls'))
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
                return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+'?next='+reverse('act_edit', urlconf='gbe.urls', args=[str(act.id)]))

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
                          
        form.fields['performer']= forms.ModelChoiceField(queryset=Performer.
                                                         objects.filter(contact=profile)) 
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
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))   

    try:
        act = Act.objects.filter(id=act_id)[0]
        if act.performer.contact != profile:
          return HttpResponseRedirect('/fail1')  # just fail for now 
    except IndexError:
        return HttpResponseRedirect('/fail2')  # just fail for now
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
        form.fields['performer']= forms.ModelChoiceField(queryset=Performer.
                                                         objects.filter(contact=profile))  
 
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
    try:
        act = Act.objects.filter(id=act_id)[0]
        if act.performer.contact != request.user.profile:
          return HttpResponseRedirect(reverse('home'), urlconf='gbe.urls')  # just fail for now    
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
 
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    

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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if not 'Act Reviewers' in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    try:
        act = Act.objects.filter(id=act_id)[0]
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
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
    if  'Act Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance = act)
        # This requires that the show be scheduled - seems reasonable in current workflow and lets me
        # order by date.  Also - assumes that shows are only scheduled once
        try:
            start=Show.objects.all().filter(scheduler_events__resources_allocated__resource__actresource___item=act)[0]
        except:
            start=""
        actionform.fields['show'] = forms.ModelChoiceField(
        	                         queryset=Show.objects.all().filter(scheduler_events__isnull=False).order_by('scheduler_events__starttime'),
        	                         empty_label=None,
        	                         label='Pick a Show',
        	                         initial=start)
        actionURL = reverse('act_changestate', urlconf='gbe.urls', args=[act_id])
    else:
            actionform = False;
            actionURL = False;

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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if not 'Act Reviewers' in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

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
    The generic function to change a bid to a new state (accepted,
    rejected, etc.).  This can work for any Biddable class, but may
    be an add-on to other work for a given class type.
    NOTE: only call on a post request
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Act Coordinator' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    if request.method == 'POST':
        from scheduler.models import Event, ResourceAllocation, ActResource
        act = Act.objects.filter(id=bid_id)[0]

        # Clear out previous castings, deletes ActResource and ResourceAllocation
        ActResource.objects.filter(_item=act).delete()
 
        # if the act has been accepted, set the show.
        if request.POST['show'] and (request.POST['accepted'] == '3' or request.POST['accepted'] == '2'):
            # Cast the act into the show by adding it to the schedule resource allocation
            try:
                show = Event.objects.filter(eventitem__event=request.POST['show'])[0]
                casting = ResourceAllocation()
                casting.event = show
                actresource = ActResource(_item=act)
                actresource.save()
                casting.resource = actresource
                casting.save()
            except:
                return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please
            
    return bid_changestate (request, bid_id, 'act_review_list')



@login_required
def submit_act(request, act_id):
    try:
        submitter = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  # don't bother with next redirect, they can't own this act!
    try:
        the_act = Act.objects.get(id=act_id)
    except Act.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  # no such act
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
    try:
        owner = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if len (teachers) == 0 :
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+'?next='+reverse('class_create', urlconf='gbe.urls'))
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
        form.fields['teacher']= forms.ModelChoiceField(queryset=
                                                       Persona.objects.
                                                       filter(performer_profile_id=owner.resourceitem_id))
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
    try:
        owner = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    try:
        the_class = Class.objects.filter(id=class_id)[0]
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # no class for this id, fail out
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if the_class.teacher not in teachers:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # not a teacher for this class, fail out

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
    try:
        classbid = Class.objects.filter(id=class_id)[0]
        if classbid.teacher.contact != request.user.profile:
          return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))  # just fail for now    
        classform = ClassBidForm(instance = classbid, prefix = 'The Class')
        teacher = PersonaForm(instance = classbid.teacher, 
                                prefix = 'The Teacher(s)')
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    

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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Class Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    try:
        aclass = Class.objects.filter(id=class_id)[0]
        classform = ClassBidForm(instance = aclass, prefix = 'The Class')
        teacher = PersonaForm(instance = aclass.teacher,
                                prefix = 'The Teacher(s)')
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
 
    if  'Class Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance = aclass)
        actionURL = reverse('class_changestate', urlconf='gbe.urls', args=[aclass.id])
    else:
            actionform = False;
            actionURL = False;
   
    '''
    if user has previously reviewed the class, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=class_id, evaluator_id=reviewer.id)[0]
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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Class Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please


    try:

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
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('class_review', urlconf='gbe.urls')})

@login_required
def class_changestate (request, bid_id):
    '''
    The generic function to change a bid to a new state (accepted,
    rejected, etc.).  This can work for any Biddable class, but may
    be an add-on to other work for a given class type.
    NOTE: only call on a post request
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Class Coordinator' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    return bid_changestate (request, bid_id, 'class_review_list')




@login_required
def create_volunteer(request):
    page_title = 'Volunteer'
    view_title = "Volunteer at the Expo"
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls')+'?next='+reverse('volunteer_create', urlconf='gbe.urls'))
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
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if 'Volunteer Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    try:
        volunteer = Volunteer.objects.filter(id=volunteer_id)[0]
        volform = VolunteerBidForm(instance = volunteer, prefix = 'The Volunteer')
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
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
            return HttpResponseRedirect(reverse('volunteer_review_list', urlconf='gbe.urls'))
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
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if 'Volunteer Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    try:
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
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('volunteer_review', urlconf='gbe.urls') })
    

def review_vendor(request, vendor_id):
    '''
    Show a bid  which needs to be reviewed by the current user. 
    To show: display all information about the bid, and a standard 
    review form.
    If user is not a reviewer, politely decline to show anything. 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if 'Vendor Reviewers' not in reviewer.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please
    try:
        vendor = Vendor.objects.filter(id=vendor_id)[0]
        volform = VendorBidForm(instance = vendor, prefix = 'The Vendor')
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
    if  'Vendor Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance = vendor)
        actionURL = reverse('vendor_changestate', urlconf='gbe.urls', args=[vendor_id])
    else:
            actionform = False;
            actionURL = False;
   
    '''
    if user has previously reviewed the act, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(bid_id=vendor_id, evaluator_id=reviewer.id)[0]
    except:
        bid_eval = BidEvaluation(evaluator = reviewer, bid = vendor)

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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if 'Vendor Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    try:
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
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Vendor Coordinator' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please

    return bid_changestate (request, bid_id, 'vendor_review_list')


@login_required
def create_vendor(request):

    title = "Vendor Application"
    fee_link = vendor_submittal_link(request.user.id)

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('accounts_profile', urlconf='gbe.urls')+'?next='+reverse('vendor_create', urlconf='gbe.urls'))
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

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))

    try:
        vendor = Vendor.objects.filter(id=vendor_id)[0]
        if vendor.profile != profile:
          return HttpResponseRedirect('/fail1')  # just fail for now 
    except IndexError:
        return HttpResponseRedirect('/fail2')  # just fail for now
 
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
    try:
        vendor = Vendor.objects.filter(id=vendor_id)[0]
        if vendor.profile != request.user.profile:
          return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        vendorform = VendorBidForm(instance = vendor, prefix = 'The Business')
        profile = ParticipantForm(instance = vendor.profile,
                                  initial= { 'email' : request.user.email, 
                                           'first_name' : request.user.first_name, 
                                           'last_name' : request.user.last_name},
                                  prefix = 'The Contact Info')
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    

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
    if request.user.is_authenticated:
        try: 
            viewer_profile = request.user.profile
        except Profile.DoesNotExist:
            return HttpResponseRedirect(reverse('profile_update', urlconf='gbe.urls'))
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
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please
    if not admin_profile.user_object.is_staff:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please
    try:
        user_profile=Profile.objects.filter(id=profile_id)[0]
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please
    if request.method == 'POST':
        form = ProfileAdminForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls', 
                                                args=[str(profile_id)]))
        else:
            return render(request, 'gbe/update_profile.tmpl', 
                          {'form':form})
    else:
        form = ProfileAdminForm(instance=user_profile,
                              initial={'email':request.user.email, 
                                         'first_name':request.user.first_name, 
                                         'last_name':request.user.last_name,
                                     })
        return render(request, 'gbe/update_profile.tmpl', 
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
            return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
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

    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Class Coordinator' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('homer', urlconf='gbe.urls'))   # better redirect please

    try:
        the_class = ClassProposal.objects.filter(id=class_id)[0]
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # no class for this id, fail out

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
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # should go to 404?

    if  'Class Coordinator' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # better redirect please


    try:

        header = ClassProposal().bid_review_header
        classes = ClassProposal.objects.all().order_by('type', 'title')
        rows = []
        for aclass in classes:
            bid_row = {}
            bid_row['bid'] = aclass.bid_review_summary
            bid_row['id'] =  aclass.id
            bid_row['review_url'] = reverse('proposal_publish', urlconf='gbe.urls', args=[aclass.id])
            rows.append(bid_row)
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_link': reverse('proposal_publish', urlconf='gbe.urls')})

 
def events_list(request):
    '''
    Returns a list of the various events, with short descriptions.
    '''
    try:
        events = Event.objects.all()
    except:
        events = None
    return render(request, 'gbe/event_list.tmpl',
                  {'title': event_list_title,
                   'view_header_text': event_list_text,
                   'events': events,
                   'show_tickets': True,
                   'user_id':request.user.id })
    pass


def shows_list(request):
    '''
    Mostly to test event display
    '''
    try:
        shows = Show.objects.all()
    except:
        shows = None
    return render(request, 'gbe/event_list.tmpl',
                  {'title': show_list_title,
                   'view_header_text': show_list_text,
                   'events': shows})


def panel_create(request):
    '''
    View for creating a panel.  Boilerplate for now, more later.
    '''

    pass

def panel_list(request):
    '''
    View for getting a list of all panels that meets regex in request.
    Boilerplate.
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
    try:
        owner = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    
    presenters = owner.personae.all()
    classes = ClassProposal.objects.filter(display=True).order_by('type', 'title')
    # if there's no classes to work with, save the user the bother, and
    # just let them know
    if len(classes) == 0:
        return render (request, 'gbe/conf_volunteer_list.tmpl', 
                   {'view_title': view_title, 'page_title': page_title})
    if len (presenters) == 0 :
        return HttpResponseRedirect(reverse('persona_create', urlconf='gbe.urls')+'?next='+reverse('conference_volunteer', urlconf='gbe.urls'))

    header = ClassProposal().presenter_bid_header
    header += ConferenceVolunteer().presenter_bid_header

    if request.method == 'POST':
        error = "start of work---"
        for aclass in classes:
            if str(aclass.id)+'-volunteering' in request.POST.keys():
                try:
                    volunteer = ConferenceVolunteer.objects.filter(bid=aclass).filter(
                                           presenter=request.POST.get(str(aclass.id)+'-presenter'))[0]
                except IndexError:
                    volunteer = ConferenceVolunteer()

                form = ConferenceVolunteerForm(request.POST, instance=volunteer,
                                               prefix=str(aclass.id))
                if form.is_valid():
                    form.save()
                else:
                    return render (request, 'gbe/error.tmpl', 
                                   {'error': 'There was an error saving your presentation request, please try again.'})

        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else: 
      try:
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

      except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))   # 404 please, thanks.
    
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

    try:
        bid = Biddable.objects.filter(id=bid_id)[0]
    except IndexError:
        return HttpResponseRedirect(reverse(redirectURL, urlconf='gbe.urls'))   
    
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

