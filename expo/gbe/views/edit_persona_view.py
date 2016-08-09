from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from expo.gbe_logging import log_func
from gbe.models import Persona
from gbe.forms import PersonaForm
from gbe.functions import validate_profile


@login_required
@log_func
def EditPersonaView(request, persona_id):
    '''
    Modify an existing Persona object.
    '''
    page_title = 'Manage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    submit_button = 'Save Persona'
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))
    persona = get_object_or_404(Persona, resourceitem_id=persona_id)
    if persona.performer_profile != profile:
        raise PermissionDenied

    if request.method == 'POST':
        form = PersonaForm(request.POST,
                           request.FILES,
                           instance=persona)
        if form.is_valid():
            performer = form.save(commit=True)
            return HttpResponseRedirect(reverse('home',
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': [form],
                           'nodraft': submit_button,
                           'page_title': page_title,
                           'view_title': view_title,
                           })
    else:
        form = PersonaForm(instance=persona)
        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       })
