from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
from scheduler.data_transfer import Person
from scheduler.idd import (
    get_bookings,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import (
    show_general_status,
)
from gbe.models import (
    UserMessage,
)
from gbe.functions import validate_profile
from gbetext import (
    no_profile_msg,
    no_login_msg,
    full_login_msg,
    set_favorite_msg,
    unset_favorite_msg,
)


class SetFavoriteView(View):

    def check_user_state(self, request, url):
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

    @never_cache
    def get(self, request, *args, **kwargs):
        this_url = reverse(
                'set_favorite',
                args=[kwargs['occurrence_id'], kwargs['state']],
                urlconf='gbe.scheduling.urls')
        response = self.check_user_state(request, this_url)
        if response:
            return response
        occurrence_id = int(kwargs['occurrence_id'])
        interested = get_bookings(occurrence_id,
                                role="Interested")
        bookings = []
        for person in interested.people:
            if person.user == self.owner.user_object:
                bookings += [person.booking_id]

        if kwargs['state'] == 'on' and len(bookings) == 0:
            person = Person(
                user=self.owner.user_object,
                role="Interested")
            response = set_person(occurrence_id, person)
            show_general_status(request,
                                response,
                                self.__class__.__name__)
            if len(response.errors) == 0 and response.booking_id:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_FAVORITE",
                    defaults={
                        'summary': "User has shown interest",
                        'description': set_favorite_msg})
                messages.success(request, user_message[0].description)
        elif kwargs['state'] == 'off' and len(bookings) > 0:
            success = True
            for booking_id in bookings:
                response = remove_booking(occurrence_id,
                                          booking_id)
                show_general_status(request,
                                    response,
                                    self.__class__.__name__)
                if not response.booking_id:
                    success = False
            if success:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="REMOVE_FAVORITE",
                    defaults={
                        'summary': "User has shown lack of interest",
                        'description': unset_favorite_msg})
                messages.success(request, user_message[0].description)
        if request.GET.get('next', None):
            redirect_to = request.GET['next']
        else:
            redirect_to = reverse('home', urlconf='gbe.urls')
        return HttpResponseRedirect(redirect_to)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SetFavoriteView, self).dispatch(*args, **kwargs)
