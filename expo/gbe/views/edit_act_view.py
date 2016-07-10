from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.forms import ModelChoiceField

from expo.gbe_logging import log_func
from gbe.functions import validate_profile
from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)
from gbe.models import (
    Act,
    Performer,
    UserMessage
)
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
    AudioInfoForm,
    StageInfoForm,
)
from gbe.duration import Duration
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg
)

@login_required
@log_func
def EditActView(request, act_id):
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

    act = get_object_or_404(Act, id=act_id)
    if act.performer.contact != profile:
        raise Http404

    audio_info = act.tech.audio
    stage_info = act.tech.stage
    draft_fields = Act().bid_draft_fields

    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form
        with fewer required fields (same model)
        '''
        if 'submit' in request.POST.keys():
            form = ActEditForm(request.POST,
                               instance=act,
                               prefix='theact',
                               initial={
                                   'track_title': audio_info.track_title,
                                   'track_artist': audio_info.track_artist,
                                   'track_duration': audio_info.track_duration,
                                   'act_duration': stage_info.act_duration
                               })
            user_message = UserMessage.objects.get_or_create(
                view='EditActView',
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "Act Edit & Submit Success",
                    'description': default_act_submit_msg})
        else:
            form = ActEditDraftForm(
                request.POST,
                instance=act,
                prefix='theact',
                initial={
                    'track_title': audio_info.track_title,
                    'track_artist': audio_info.track_artist,
                    'track_duration': audio_info.track_duration,
                    'act_duration': stage_info.act_duration
                })
            user_message = UserMessage.objects.get_or_create(
                view='EditActView',
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "Act Edit Draft Success",
                    'description': default_act_draft_msg})
        audioform = AudioInfoForm(request.POST, prefix='theact',
                                  instance=audio_info)
        stageform = StageInfoForm(request.POST, prefix='theact',
                                  instance=stage_info)

        if all([form.is_valid(),
                audioform.is_valid(),
                stageform.is_valid()]):
            tech = act.tech
            tech.audio = audioform.save()
            tech.stage = stageform.save()
            tech.save()
            form.save()
        else:
            fields, requiredsub = Act().bid_fields
            return render(
                request,
                'gbe/bid.tmpl',
                {'forms': [form],
                 'page_title': page_title,
                 'view_title': view_title,
                 'draft_fields': draft_fields,
                 'fee_link': fee_link,
                 'submit_fields': requiredsub}
            )

        if 'submit' in request.POST.keys():
            '''
            If this is a formal submit request, did they pay?
            They can't submit w/out paying
            '''
            if verify_performer_app_paid(request.user.username):
                act.submitted = True
                act.save()
            else:
                page_title = 'Act Payment'
                return render(
                    request,
                    'gbe/please_pay.tmpl',
                    {'link': fee_link,
                     'page_title': page_title}
                )
        messages.success(request, user_message[0].description)
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else:
        audio_info = act.tech.audio
        stage_info = act.tech.stage

        form = ActEditForm(instance=act,
                           prefix='theact',
                           initial={
                               'track_title': audio_info.track_title,
                               'track_artist': audio_info.track_artist,
                               'track_duration': audio_info.track_duration,
                               'act_duration': stage_info.act_duration
                           })
        q = Performer.objects.filter(contact=profile)
        form.fields['performer'] = ModelChoiceField(queryset=q)
        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [form],
             'page_title': page_title,
             'view_title': view_title,
             'fee_link': fee_link,
             'draft_fields': draft_fields}
        )
