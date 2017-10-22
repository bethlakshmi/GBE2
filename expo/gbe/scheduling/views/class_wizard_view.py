from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import PickClassForm
from gbe.models import Class
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbe.scheduling.views import EventWizardView


class ClassWizardView(EventWizardView):
    template = 'gbe/scheduling/class_wizard.tmpl'

    @never_cache
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['event_type'] = "Conference Class"
        context['next_form'] = PickClassForm(
            initial={'conference':  self.conference})
        context['next_title'] = "Pick the Class"
        return render(request, self.template, context)
