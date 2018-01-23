from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from gbe.models import UserMessage
from gbe.scheduling.forms import (
    StaffAreaForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from gbe.functions import validate_perms
from gbe_forms_text import event_settings


class StaffAreaWizardView(EventWizardView):
    template = 'gbe/scheduling/ticketed_event_wizard.tmpl'
    event_type = "staff"

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = StaffAreaForm(
            initial={'conference':  self.conference})
        context['event_type'] = "Staff Area"
        context['second_title'] = "Create Staff Area"

        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = StaffAreaForm(request.POST)
        if context['second_form'].is_valid():
            new_event = context['second_form'].save()

            success = self.finish_booking(
                request,
                response,
                context['scheduling_form'].cleaned_data['day'].pk)
            if success:
                if request.POST.get(
                        'set_event') == 'Continue to Volunteer Opportunities':
                    return HttpResponseRedirect(
                        reverse('edit_event',
                                urlconf='gbe.scheduling.urls',
                                args=[self.conference.conference_slug,
                                      response.occurrence.pk]))
                else:
                    return success
        return render(request, self.template, context)
