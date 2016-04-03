from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect

from expo.gbe_logging import log_func
from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
)
from gbe.functions import validate_profile
from gbe.models import (
    Costume,
    Persona,
)
from gbetext import not_yours

@login_required
@log_func
def EditCostumeView(request, costume_id):
    '''
    Edit an existing costume display proposal.
    '''
    page_title = "Displaying a Costume"
    view_title = "Displaying a Costume"

    owner = validate_profile(request, require=True)
    if not owner:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))

    the_costume = get_object_or_404(Costume, id=costume_id)

    if the_costume.profile != owner:
        return render(request,
                      'gbe/error.tmpl',
                      {'error': not_yours})

    performers = owner.personae.all()
    draft_fields = Costume().bid_draft_fields

    if performers.count() > 0 and the_costume.performer not in performers:
        return render(request,
                      'gbe/error.tmpl',
                      {'error': "This bid is not one of your stage names."})

    if request.method == 'POST':
        if 'submit' in request.POST.keys():
            form = CostumeBidSubmitForm(request.POST,
                                        instance=the_costume)
            details = CostumeDetailsSubmitForm(request.POST,
                                               request.FILES,
                                               instance=the_costume)
        else:
            form = CostumeBidDraftForm(request.POST,
                                       instance=the_costume)
            details = CostumeDetailsDraftForm(request.POST,
                                              request.FILES,
                                              instance=the_costume)

        if form.is_valid() and details.is_valid():
            the_costume = form.save()
            the_costume = details.save()
            if 'submit' in request.POST.keys():
                the_costume.submitted = True

            the_costume.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            fields, requiredsub = Costume().bid_fields
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
        form = CostumeBidSubmitForm(instance=the_costume)
        details = CostumeDetailsSubmitForm(instance=the_costume)

        q = Persona.objects.filter(performer_profile_id=owner.resourceitem_id)
        form.fields['performer'] = forms.ModelChoiceField(
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
