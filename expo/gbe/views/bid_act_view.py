from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from expo.gbe_logging import log_func
from gbe.forms import (
    ActEditForm,
    ActEditDraftForm,
    AudioInfoForm,
    LightingInfoForm,
    StageInfoForm,
)

from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)

from gbe.models import (
    Conference,
    Act,
    AudioInfo,
    LightingInfo,
    StageInfo,
    TechInfo,
)
from gbe.functions import validate_profile


@login_required
@log_func
def BidActView(request):
    '''
    Create a proposed Act object.
    '''
    page_title = 'Propose Act'
    view_title = 'Propose an Act'
    fee_link = performer_act_submittal_link(request.user.id)
    form = ActEditForm(prefix='theact')
    audioform = AudioInfoForm(prefix='audio')
    lightingform = LightingInfoForm(prefix='lighting')
    stageform = StageInfoForm(prefix='stage')

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    personae = profile.personae.all()
    draft_fields = Act().bid_draft_fields

    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('act_create',
                                            urlconf='gbe.urls'))
    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form
        with fewer required fields (same model)
        '''
        if 'submit' in request.POST.keys():
            form = ActEditForm(request.POST,
                               prefix='theact')
        else:
            form = ActEditDraftForm(request.POST,
                                    prefix='theact')
        if form.is_valid():
            # hack
            conference = Conference.objects.filter(accepting_bids=True).first()
            act = form.save(commit=False)
            act.conference = conference
            techinfo = TechInfo()
            audioinfoform = AudioInfoForm(request.POST, prefix='theact')
            techinfo.audio = audioinfoform.save()
            stageinfoform = StageInfoForm(request.POST, prefix='theact')
            techinfo.stage = stageinfoform.save()
            lightinginfo = LightingInfo()
            lightinginfo.save()
            techinfo.lighting = lightinginfo
            techinfo.save()

            act.tech = techinfo
            act.submitted = False
            act.accepted = False
            act.save()

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
                return HttpResponseRedirect(reverse('home',
                                                    urlconf='gbe.urls'))
            else:
                page_title = 'Act Payment'
                return render(
                    request,
                    'gbe/please_pay.tmpl',
                    {'link': fee_link,
                     'page_title': page_title}
                )
        else:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    else:
        form = ActEditForm(initial={'owner': profile,
                                    'performer': personae[0]},
                           prefix='theact')
        q = Performer.objects.filter(contact=profile)
        form.fields['performer'] = forms.ModelChoiceField(queryset=q)

        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [form],
             'page_title': page_title,
             'view_title': view_title,
             'fee_link': fee_link,
             'draft_fields': draft_fields}
        )
