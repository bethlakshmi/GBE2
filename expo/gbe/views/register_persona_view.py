from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.forms import PersonaForm
from gbe.functions import validate_profile


@login_required
@log_func
def RegisterPersonaView(request, **kwargs):
    import pdb; pdb.set_trace()
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    submit_button = 'Save Persona'
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('home',
                                            urlconf='gbe.urls'))
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES)
        if form.is_valid():
            performer = form.save(commit=True)
            pid = profile.pk
            if request.GET.get('next', None):
                redirect_to = request.GET['next']
            else:
                redirect_to = reverse('home', urlconf='gbe.urls')
            return HttpResponseRedirect(redirect_to)
        else:
            return render(request, 'gbe/bid.tmpl',
                          {'forms': [form],
                           'nodraft': submit_button,
                           'page_title': page_title,
                           'view_title': view_title,
                           })
    else:
        form = PersonaForm(initial={'performer_profile': profile,
                                    'contact': profile,
                                    })
        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       })
