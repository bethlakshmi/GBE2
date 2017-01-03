from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.forms import (
    VolunteerBidForm,
    VolunteerInterestForm,
)
from gbe.functions import (
    validate_perms,
    validate_profile,
)
from gbe.models import (
    UserMessage,
    Volunteer,
)
from gbetext import (
    default_volunteer_edit_msg,
    default_volunteer_no_interest_msg,
    default_window_schedule_conflict,
)
from gbe.views.volunteer_display_functions import (
    validate_interests,
)
from expo.settings import DATETIME_FORMAT

def get_reduced_availability(the_bid, form):
    '''  Get cases where the volunteer has reduced their availability.
    Either by offering fewer available windows, or by adding to the unavailable
    windows.  Either one is a case for needing to check schedule conflict.
    '''
    reduced = []
    for window in the_bid.available_windows.all():
        if window not in form.cleaned_data['available_windows']:
            reduced += [window]
    
    for window in form.cleaned_data['unavailable_windows']:
        if window not in the_bid.unavailable_windows.all():
            reduced += [window]
    return reduced


def manage_schedule_problems(changed_windows, profile):
    warnings = ""
    conflicts = []
    for window in changed_windows:
        for conflict in profile.get_conflicts(window):
            if ((conflict not in conflicts) and
                conflict.eventitem.payload['type'] == 'Volunteer'):
                conflicts += [conflict]
                warnings += "<br>%s working for %s - as %s" % (
                    conflict.starttime.strftime(DATETIME_FORMAT),
                    str(conflict),
                    conflict.eventitem.child().volunteer_category_description)
                leads = conflict.eventitem.roles(roles=['Staff Lead',])
                for lead in leads:
                    warnings += ", Staff Lead is %s" % (
                        str(lead.item.badge_name))
    return warnings


@login_required
@log_func
@never_cache
def EditVolunteerView(request, volunteer_id):
    page_title = "Edit Volunteer Bid"
    view_title = "Edit Submitted Volunteer Bid"
 
    user = validate_profile(request, require=True)

    the_bid = get_object_or_404(Volunteer, id=volunteer_id)
    if the_bid.profile != user:
        user = validate_perms(request, ('Volunteer Coordinator',))

    formset = []

    if request.method == 'POST':
        form = VolunteerBidForm(
            request.POST,
            instance=the_bid,
            available_windows=the_bid.conference.windows(),
            unavailable_windows=the_bid.conference.windows())

        formset = [
            VolunteerInterestForm(
                request.POST,
                instance=interest,
                initial={'interest': interest.interest},
                prefix=str(interest.pk)
                ) for interest in the_bid.volunteerinterest_set.all()]
        valid_interests, like_one_thing = validate_interests(formset)

        if form.is_valid() and valid_interests and like_one_thing:
            changed_windows = get_reduced_availability(the_bid, form)
            warnings = manage_schedule_problems(
                changed_windows, the_bid.profile)
            if warnings:
                user_message = UserMessage.objects.get_or_create(
                view='EditVolunteerView',
                code="AVAILABILITY_CONFLICT",
                defaults={
                    'summary': "Volunteer Edit Caused Conflict",
                    'description': default_window_schedule_conflict,})
                messages.warning(request, user_message[0].description+warnings)
            the_bid = form.save(commit=True)
            the_bid.available_windows.clear()
            the_bid.unavailable_windows.clear()
            for window in form.cleaned_data['available_windows']:
                the_bid.available_windows.add(window)
            for window in form.cleaned_data['unavailable_windows']:
                the_bid.unavailable_windows.add(window)
            for interest_form in formset:
                interest_form.save()

            user_message = UserMessage.objects.get_or_create(
                view='EditVolunteerView',
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "Volunteer Edit Success",
                    'description': default_volunteer_edit_msg})
            messages.success(request, user_message[0].description)
            if the_bid.profile == user:
                return HttpResponseRedirect(
                    reverse('home', urlconf='gbe.urls'))
            else:
                return HttpResponseRedirect("%s?conf_slug=%s" % (
                    reverse('volunteer_review', urlconf='gbe.urls'),
                    the_bid.conference.conference_slug))

        else:
            formset += [form]
            if not like_one_thing:
                user_message = UserMessage.objects.get_or_create(
                    view='EditVolunteerView',
                    code="NO_INTERESTS_SUBMITTED",
                    defaults={
                        'summary': "Volunteer Has No Interests",
                        'description': default_volunteer_no_interest_msg})
                messages.error(request, user_message[0].description)

            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': formset,
                           'page_title': page_title,
                           'view_title': view_title,
                           'nodraft': 'Submit'})
    else:
        for interest in the_bid.volunteerinterest_set.all():
            formset += [VolunteerInterestForm(
                instance=interest,
                initial={'interest': interest.interest},
                prefix=str(interest.pk))]

        formset += [VolunteerBidForm(
            instance=the_bid,
            available_windows=the_bid.conference.windows(),
            unavailable_windows=the_bid.conference.windows())]

        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': formset,
                       'page_title': page_title,
                       'view_title': view_title,
                       'nodraft': 'Submit'})
