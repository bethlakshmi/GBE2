from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.http import (
    HttpResponseRedirect
)
from django.core.urlresolvers import reverse
from django.forms import ModelChoiceField
from expo.gbe_logging import log_func
from gbe.functions import validate_profile
from gbe.forms import (
    CostumeBidDraftForm,
    CostumeDetailsDraftForm,
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
)
from gbe.models import (
    Conference,
    Costume,
    Persona,
    UserMessage
)
from gbe_forms_text import (
    costume_proposal_labels,
    costume_proposal_form_text,
)
from gbetext import (
    default_costume_submit_msg,
    default_costume_draft_msg
)


@login_required
@log_func
def BidCostumeView(request):
    '''
    Propose to display a costume at the costume exhibit.
    Bidder is volunteering to bring the costume, expo staff will organize
    displaying it.
        owner = profile of the submitter who is presumed to be in posession
              of the costume
        performer(s) = the performer who wore the costume (optional)
    '''
    page_title = "Displaying a Costume"
    view_title = "Displaying a Costume"

    owner = validate_profile(request, require=False)
    if not owner:
        return HttpResponseRedirect(reverse('profile',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('costume_create',
                                            urlconf='gbe.urls'))

    performers = owner.personae.all()

    if not performers.exists():
        return HttpResponseRedirect(reverse('persona_create',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('costume_create',
                                            urlconf='gbe.urls'))

    draft_fields = Costume().bid_draft_fields

    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''
        new_costume = Costume()
        if 'submit' in request.POST.keys():
            form = CostumeBidSubmitForm(request.POST, instance=new_costume)
            details = CostumeDetailsSubmitForm(request.POST,
                                               request.FILES,
                                               instance=new_costume)
            user_message = UserMessage.objects.get_or_create(
                view='BidCostumeView',
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "Costume Submit Success",
                    'description': default_costume_submit_msg})
        else:
            form = CostumeBidDraftForm(request.POST, instance=new_costume)
            details = CostumeDetailsDraftForm(request.POST,
                                              request.FILES,
                                              instance=new_costume)
            user_message = UserMessage.objects.get_or_create(
                view='BidCostumeView',
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "Costume Draft Success",
                    'description': default_costume_draft_msg})
        if form.is_valid() and details.is_valid():
            conference = Conference.objects.filter(accepting_bids=True).first()
            new_costume.profile = owner
            new_costume.conference = conference
            if 'submit' in request.POST.keys():
                new_costume.submitted = True
            new_costume = form.save()
            new_costume = details.save()
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home',
                                                urlconf='gbe.urls'))
        else:
            fields, requiredsub = Costume().bid_fields
            q = Persona.objects.filter(
                performer_profile_id=owner.resourceitem_id)
            form.fields['performer'] = ModelChoiceField(
                queryset=q,
                label=costume_proposal_labels['performer'],
                required=False)

            return render(
                request,
                'gbe/bid.tmpl',
                {'forms': [form, details],
                 'page_title': page_title,
                 'view_title': view_title,
                 'draft_fields': draft_fields,
                 'submit_fields': requiredsub,
                 'view_header_text': costume_proposal_form_text}
            )

    else:
        form = CostumeBidSubmitForm(initial={'profile': owner,
                                             'performer': performers[0]})
        details = CostumeDetailsSubmitForm(
            initial={'profile': owner,
                     'performer': performers[0]})
        q = Persona.objects.filter(performer_profile_id=owner.resourceitem_id)
        form.fields['performer'] = ModelChoiceField(
            queryset=q,
            label=costume_proposal_labels['performer'],
            required=False)

        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [form, details],
             'page_title': page_title,
             'view_title': view_title,
             'draft_fields': draft_fields,
             'view_header_text': costume_proposal_form_text}
        )
