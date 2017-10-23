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
from gbe.scheduling.forms import (
    ClassBookingForm,
    PickClassForm,
    ScheduleOccurrenceForm,
)
from gbe.models import Class
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbe.scheduling.views import EventWizardView


class ClassWizardView(EventWizardView):
    template = 'gbe/scheduling/class_wizard.tmpl'
    
    def groundwork(self, request, args, kwargs):
        context = super(ClassWizardView, self).groundwork(request, args, kwargs)
        context['event_type'] = "Conference Class"
        context['second_title'] = "Pick the Class"
        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            initial={'conference':  self.conference})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            request.POST,
            initial={'conference':  self.conference})
        if context['second_form'].is_valid():
            working_class = context['second_form'].cleaned_data['accepted_class']
            context['third_form'] = ClassBookingForm(
                instance=working_class)
            context['third_title'] = "Book Class:  %s" % working_class.e_title
            context['scheduling_form'] = ScheduleOccurrenceForm(
                conference=self.conference,
                initial={'duration': working_class.duration.hours() + float(
                    working_class.duration.minutes())/60,})
            context['scheduling_form'].fields['max_volunteer'].widget = HiddenInput()
        return render(request, self.template, context)
