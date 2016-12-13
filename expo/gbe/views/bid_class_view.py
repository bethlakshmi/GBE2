from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import ModelChoiceField
from django.shortcuts import render

from gbe.duration import Duration
from expo.gbe_logging import log_func
from gbe.forms import (
    ClassBidForm,
    ClassBidDraftForm,
)
from gbe.models import (
    Class,
    Conference,
    Persona,
    UserMessage
)
from gbe.functions import validate_profile
from gbe_forms_text import avoided_constraints_popup_text
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)


@login_required
@log_func
def BidClassView(request):
    '''
    Propose a class. Bidder is volunteering to teach this class - we have to
    confirm that they understand and accept this.
    '''
    page_title = "Submit a Class"
    view_title = "Submit a Class"

    owner = validate_profile(request, require=True)

    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if len(teachers) == 0:
        return HttpResponseRedirect(reverse('persona_create',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('class_create',
                                            urlconf='gbe.urls'))
    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''

        if 'submit' in request.POST.keys():
            form = ClassBidForm(request.POST)
            user_message = UserMessage.objects.get_or_create(
                view='BidClassView',
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "Class Submit Success",
                    'description': default_class_submit_msg})
        else:
            form = ClassBidDraftForm(request.POST)
            user_message = UserMessage.objects.get_or_create(
                view='BidClassView',
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "Class Draft Success",
                    'description': default_class_draft_msg})

        if form.is_valid():
            conference = Conference.objects.filter(accepting_bids=True).first()
            new_class = form.save(commit=False)
            new_class.duration = Duration(minutes=new_class.length_minutes)
            new_class = form.save(commit=True)
            if 'submit' in request.POST.keys():
                if new_class.complete:
                    new_class.submitted = True
                    new_class.b_conference = conference
                    new_class.e_conference = conference
                    new_class.save()
                else:
                    error_string = 'Cannot submit, class is not complete'
                    return render(request,
                                  'gbe/bid.tmpl',
                                  {'forms': [form],
                                   'page_title': page_title,
                                   'view_title': view_title,
                                   'draft_fields': draft_fields,
                                   'errors': [error_string],
                                   'popup_text':
                                        avoided_constraints_popup_text})

            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            fields, requiredsub = Class().get_bid_fields
            q = Persona.objects.filter(
                performer_profile_id=owner.resourceitem_id)
            form.fields['teacher'] = ModelChoiceField(queryset=q)
            return render(
                request,
                'gbe/bid.tmpl',
                {'forms': [form],
                 'page_title': page_title,
                 'view_title': view_title,
                 'draft_fields': draft_fields,
                 'submit_fields': requiredsub,
                 'popup_text': avoided_constraints_popup_text}
            )

    else:
        form = ClassBidForm(initial={'owner': owner,
                                     'teacher': teachers[0]})
        q = Persona.objects.filter(performer_profile_id=owner.resourceitem_id)
        form.fields['teacher'] = ModelChoiceField(queryset=q)

        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [form],
             'page_title': page_title,
             'view_title': view_title,
             'draft_fields': draft_fields,
             'popup_text': avoided_constraints_popup_text}
        )
