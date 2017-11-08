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
    ScheduleSelectionForm,
    VolunteerOpportunityForm,
    WorkerAllocationForm,
)
from scheduler.data_transfer import Person
from scheduler.idd import (
    set_person,
)
from scheduler.views.functions import (
    get_event_display_info,
)
from gbe.scheduling.views.functions import (
    show_scheduling_occurrence_status,
)
from gbe.models import (
    Event,
    Performer,
    Profile,
    Room,
)
from gbe.functions import validate_profile
from gbetext import (
    no_profile_msg,
    no_login_msg,
    full_login_msg,
)


class SetFavoriteView(View):

    @never_cache
    def get(self, request, *args, **kwargs):
        this_url = reverse(
                'set_favorite',
                args=[kwargs['occurrence_id'], kwargs['state']],
                urlconf='gbe.scheduling.urls')
        if not request.user.is_authenticated():
            follow_on = '?next=%s' % this_url
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="USER_NOT_LOGGED_IN",
                defaults={
                    'summary': "Need Login - %s Bid",
                    'description': no_login_msg})
            full_msg = full_login_msg % (
                user_message[0].description,
                reverse('login', urlconf='gbe.urls') + follow_on)
            messages.warning(request, full_msg)

            return HttpResponseRedirect(
                reverse('register', urlconf='gbe.urls') + follow_on)
        self.owner = validate_profile(request, require=False)
        if not self.owner or not self.owner.complete:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PROFILE_INCOMPLETE",
                defaults={
                    'summary': "%s Profile Incomplete",
                    'description': no_profile_msg})
            messages.warning(request, user_message[0].description)
            return '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'),
                this_url)
        occurrence_id = int(kwargs['occurrence_id'])
        if kwargs['state'] == 'on':
            person = Person(
                user=self.owner.user_object,
                role="Interested")
            response = set_person(occurrence_id, person)

        else:
            set_favorite = False
        
        raise Exception("occurrence %d, state %s" % (
            occurrence_id,
            set_favorite))
        pass

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SetFavoriteView, self).dispatch(*args, **kwargs)
