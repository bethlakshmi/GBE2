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
from gbe.functions import validate_perms
from gbe.models import (
    UserMessage,
    Volunteer,
)
from gbetext import (
    default_volunteer_edit_msg,
    default_volunteer_no_interest_msg,
)
from gbe.views.volunteer_display_functions import (
    validate_interests,
)


@login_required
@log_func
def EditVolunteerView(request, volunteer_id):
    page_title = "Edit Volunteer Bid"
    view_title = "Edit Submitted Volunteer Bid"
    reviewer = validate_perms(request, ('Volunteer Coordinator',))
    the_bid = get_object_or_404(Volunteer, id=volunteer_id)
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
        # originally the volunteer create was supposed to save a title, there
        # was a bug and most old bids don't have a title.
        # This is the autocorrect
        if not the_bid.title:
            the_bid.title = 'volunteer bid: %s' % the_bid.profile.display_name

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
