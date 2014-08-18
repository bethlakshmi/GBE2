from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from gbe.models import Event, Act, Performer
from gbe.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.forms.models import inlineformset_factory
import gbe_forms_text
from ticketingfuncs import compute_submission

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
             

def create_troupe(request):
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'
    submit_button = 'Save Troupe'
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
            return render (request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       'view_header_text':troupe_header_text})
    else:
        form = TroupeForm(initial={'contact':profile})
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
        return HttpResponseRedirect('/accounts/profile/')
    try:
        persona = Persona.objects.filter(id=persona_id)[0]
    except IndexError:
        return HttpResponseRedirect('/')  # just fail for now
    if persona.performer_profile != profile:
        return HttpResponseRedirect('/')  # just fail for now    
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES, instance=persona)
        if form.is_valid():
            performer = form.save(commit=True)
            return HttpResponseRedirect('/')  
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

    form = ActEditForm(prefix='theact')
    audioform= AudioInfoForm(prefix='audio')
    lightingform= LightingInfoForm(prefix='lighting')
    stageform = StageInfoForm(prefix='stage')
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    personae = profile.personae.all()
    draft_fields = Act().bid_draft_fields
    
    if len(personae) == 0:
        return HttpResponseRedirect("/performer/create?next=/act/create")
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
                return HttpResponseRedirect('/performer/create?next=/act/edit/'+str(act.id))

        else:
            fields, requiredsub = Act().bid_fields
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form ], 
                            'page_title': page_title,                            
                            'view_title': view_title,
                            'draft_fields': draft_fields,
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
                                'errors':problems})
                
            else:
                act.submitted = True

                act.save()
                details = {'user':request.user,
                           'is_submission_fee':True,
                           'bid':act}
                return render(request, 
                              'gbe/submission.tmpl',
                              compute_submission(details))
        else:
            return HttpResponseRedirect('/')

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
                        'draft_fields': draft_fields
                        })

@login_required
def edit_act(request, act_id):
    '''
    Modify an existing Act object. 
    '''
    page_title = 'Edit Act Proposal'
    view_title = 'Edit Your Act Proposal'
    form = ActEditForm(prefix='theact')
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')   

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
#            return HttpResponseRedirect('/wtf')
        else:
            fields, requiredsub = Act().bid_fields
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form],
                            'page_title': page_title,                            
                            'view_title': view_title, 
                            'draft_fields': draft_fields,
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
                               'errors':problems})
            else:
                act.submitted = True

                act.save()
                details = {'user':request.user,
                           'is_submission_fee':True,
                           'bid':act}
                return render(request, 
                              'gbe/submission.tmpl',
                              compute_submission(details))
                    

        else:
            return HttpResponseRedirect('/')
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
          return HttpResponseRedirect('/')  # just fail for now    
        actform = ActBidForm(instance = act, prefix = 'The Act')
        performer = PersonaForm(instance = act.performer, 
                                prefix = 'The Performer(s)')
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    

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
        return HttpResponseRedirect('/')   # should go to 404?

    if not reviewer.user_object.is_staff:
        return HttpResponseRedirect('/')   # better redirect please

    try:
        act = Act.objects.filter(id=act_id)[0]
        actform = ActEditForm(instance = act, prefix = 'The Act')
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
                       {'readonlyform': [actform, performer],
                        'reviewer':reviewer,
                        'form':form})

@login_required
def review_act_list (request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # should go to 404?

    if not 'Act Reviewers' in request.user.profile.privilege_groups:
        return HttpResponseRedirect('/')   # better redirect please

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
    page_title = "Submit a Class"
    view_title = "Submit a Class"
    try:
        owner = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')
    
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if len (teachers) == 0 :
        return HttpResponseRedirect('/performer/create?next=/class/create')
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
            new_class = form.save(commit=True)
            if 'submit' in request.POST.keys():
                if new_class.complete:
                    new_class.submitted=True                    
                    new_class.save()
                    return HttpResponseRedirect("/")
                else:
                    return render (request, 
                                   'gbe/bid.tmpl', 
                                   {'forms':[form], 
                                   ' page_title': page_title,                            
                                    'view_title': view_title,
                                    'draft_fields': draft_fields,
                                    'errors':['Cannot submit, class is not complete']})
            new_class.save()
            return HttpResponseRedirect('/profile')
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
                                                       filter(performer_profile_id=owner.id))
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
        return HttpResponseRedirect('/accounts/profile/')
    try:
        the_class = Class.objects.filter(id=class_id)[0]
    except IndexError:
        return HttpResponseRedirect('/')   # no class for this id, fail out
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if the_class.teacher not in teachers:
        return HttpResponseRedirect('/' )   # not a teacher for this class, fail out

    if request.method == 'POST':
        if 'submit' in request.POST.keys():
            form = ClassBidForm(request.POST, instance=the_class)
        else:
            form = ClassBidDraftForm(request.POST, instance=the_class)

        if form.is_valid():
            the_class = form.save(commit=True)
            if 'submit' in request.POST.keys():
                if the_class.complete:
                    the_class.submitted=True                    
                    the_class.save()
                    return HttpResponseRedirect("/")
                else:
                    return render (request, 
                                   'gbe/bid.tmpl', 
                                   {'forms':[form], 
                                    'page_title': page_title,                            
                                    'view_title': view_title,
                                    'draft_fields': draft_fields,
                                    'errors':['Cannot submit, class is not complete']})
            the_class.save()
            return HttpResponseRedirect('/profile')
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
          return HttpResponseRedirect('/')  # just fail for now    
        classform = ClassBidForm(instance = classbid, prefix = 'The Class')
        teacher = PersonaForm(instance = classbid.teacher, 
                                prefix = 'The Teacher(s)')
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    

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
        return HttpResponseRedirect('/')   # should go to 404?

    if not reviewer.user_object.is_staff:
        return HttpResponseRedirect('/')   # better redirect please

    try:
        aclass = Class.objects.filter(id=class_id)[0]
        classform = ClassBidForm(instance = aclass, prefix = 'The Class')
        teacher = PersonaForm(instance = aclass.teacher,
                                prefix = 'The Teacher(s)')
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    
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
            return HttpResponseRedirect('/class/reviewlist')
        else:
            return render (request, 'gbe/bid_review.tmpl',
                           {'readonlyform': [classform],
                           'form':form})
    else:
        form = BidEvaluationForm(instance = bid_eval)
        return render (request, 
                       'gbe/bid_review.tmpl',
                       {'readonlyform': [classform, teacher],
                        'reviewer':reviewer,
                        'form':form})

@login_required
def review_class_list (request):
    '''
    Show the list of class bids, review results,
    and give a way to update the reviews 
    '''
    try:
        reviewer = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/')   # should go to 404?

    if  'Class Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect('/')   # better redirect please


    try:

        header = Class().bid_review_header
        classes = Class.objects.filter(submitted=True)
        review_query = BidEvaluation.objects.filter(bid=classes).select_related('evaluator').order_by('bid', 'evaluator')
        rows = []
        for aclass in classes:
            bid_row = []
            bid_row.append(("bid", aclass.bid_review_summary))
            bid_row.append(("reviews", review_query.filter(bid=aclass.id).select_related('evaluator').order_by('evaluator')))
            bid_row.append(("id", aclass.id))
            rows.append(bid_row)
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    
    return render (request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'review_path': '/class/review/'})


@login_required
def create_volunteer(request):
    page_title = 'Volunteer'
    view_title = "Volunteer at the Expo"
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("accounts/profile?next=volunteer/create")
    if request.method == 'POST':
        form = VolunteerBidForm(request.POST)
        if form.is_valid():
            volunteer = form.save()
            if 'submit' in request.POST.keys():
                volunteer.submitted = True
                volunteer.save()
            return HttpResponseRedirect('/')
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
        return HttpResponseRedirect('/')   # should go to 404?

    if not reviewer.user_object.is_staff:
        return HttpResponseRedirect('/')   # better redirect please

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

    if 'Volunteer Reviewers' not in request.user.profile.privilege_groups:
        return HttpResponseRedirect('/')   # better redirect please

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

    title = "Vendor Application"
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/accounts/profile/?next=vendor/create")
    if request.method == 'POST':
        form = VendorBidForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save()
            return HttpResponseRedirect("/")
        else:
            return render (request,
                           'gbe/bid.tmpl', 
                           {'forms':[form], 
                            'page_title':title, 
                            'view_title':title})
    else:
        form = VendorBidForm(initial = {'profile':profile,
                                        'physical_address':profile.address})
        return render (request, 
                       'gbe/bid.tmpl', 
                       {'forms':[form], 
                        'page_title': title,
                        'view_title':title})

@login_required
def edit_vendor(request, vendor_id):

    page_title = 'Edit Vendor Application'
    view_title = 'Edit Your Vendor Application'
    form = VendorBidForm(prefix='thebiz')
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponseRedirect('/accounts/profile/')   

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
#            return HttpResponseRedirect('/wtf')
        else:
            return render (request,
                           'gbe/bid.tmpl',
                           {'forms':[form],
                            'page_title': page_title,                            
                            'view_title': view_title, 
                       })

        if 'submit' in request.POST.keys():
            problems = vendor.validation_problems_for_submit()
            if problems:
                return render (request,
                               'gbe/bid.tmpl',
                               {'forms':[form], 
                               'page_title': page_title,                            
                               'view_title': view_title,
                               'errors':problems})
            else:
                vendor.submitted = True

                vendor.save()
                details = {'user':request.user,
                           'is_submission_fee':True,
                           'bid':vendor}
                return render(request, 
                              'gbe/submission.tmpl',
#                              compute_submission(details)
			      )

        else:
            return HttpResponseRedirect('/')
    else:
 
        form = VendorBidForm(instance = vendor, 
                           prefix='thebiz')
 
        return render (request, 
                       'gbe/bid.tmpl',
                       {'forms':[form],
                        'page_title': page_title,                            
                        'view_title': view_title,
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
          return HttpResponseRedirect('/')  # just fail for now    
        vendorform = VendorBidForm(instance = vendor, prefix = 'The Business')
        profile = ParticipantForm(instance = vendor.profile, 
                                prefix = 'The Contact Info')
    except IndexError:
        return HttpResponseRedirect('/')   # 404 please, thanks.
    

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
            if prefs_form.is_valid():
                prefs_form.save(commit=True)
                profile.preferences = prefs_form.save()
            profile.save()
            
            form.save()
            return HttpResponseRedirect("/")
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
            template = loader.get_template('gbe/class_proposal.tmpl')
            context = RequestContext (request, {'form': form})
            return HttpResponse(template.render(context))
    else:
        form = ClassProposalForm()
        template = loader.get_template('gbe/class_proposal.tmpl')
        context = RequestContext (request, {'form': form})
        return HttpResponse(template.render(context))


