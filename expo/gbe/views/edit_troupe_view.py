from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import(
    render,
    get_object_or_404,
)
from django.forms import ModelChoiceField
from expo.gbe_logging import log_func
from gbe.forms import TroupeForm
from gbe.models import (
    Profile,
    Troupe,
)
from gbe_forms_text import (
    persona_labels,
    troupe_header_text,
)
from gbe.functions import validate_profile


@login_required
@log_func
def EditTroupeView(request, troupe_id=None):
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'
    submit_button = 'Save Troupe'
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('troupe_create',
                                            urlconf='gbe.urls'))
    personae = profile.personae.all()
    if len(personae) == 0:
        return HttpResponseRedirect(reverse('persona_create',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('troupe_create',
                                            urlconf='gbe.urls'))
    if troupe_id:
        troupe = get_object_or_404(Troupe, resourceitem_id=troupe_id)
    else:
        troupe = Troupe()

    if (troupe_id > 0 and
            request.user and
            troupe.contact != request.user.profile):
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
            form.fields['contact'] = ModelChoiceField(
                queryset=q,
                empty_label=None,
                label=persona_labels['contact'])
            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': [form],
                           'nodraft': submit_button,
                           'page_title': page_title,
                           'view_title': view_title,
                           'view_header_text': troupe_header_text})
    else:
        form = TroupeForm(instance=troupe, initial={'contact': profile})
        q = Profile.objects.filter(resourceitem_id=profile.resourceitem_id)
        form.fields['contact'] = ModelChoiceField(
            queryset=q,
            empty_label=None,
            label=persona_labels['contact'])
        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       'view_header_text': troupe_header_text})
