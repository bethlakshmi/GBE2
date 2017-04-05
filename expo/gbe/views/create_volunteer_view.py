from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (
    HttpResponseRedirect,
    Http404,
)
from django.core.urlresolvers import reverse
from django.shortcuts import render
from expo.gbe_logging import log_func
from gbe.forms import (
    VolunteerBidForm,
    VolunteerInterestForm,
)
from gbe.models import (
    AvailableInterest,
    Conference,
    UserMessage,
)
from gbe.functions import (
    notify_reviewers_on_bid_change,
    validate_profile,
)
from gbetext import (
    default_volunteer_submit_msg,
    default_volunteer_no_interest_msg,
    default_volunteer_no_bid_msg,
    existing_volunteer_msg,
    no_profile_msg,
)
from gbe.views.volunteer_display_functions import (
    validate_interests,
)


def no_vol_bidding(request):
    user_message = UserMessage.objects.get_or_create(
                    view='CreateVolunteerView',
                    code="NO_BIDDING_ALLOWED",
                    defaults={
                        'summary': "Volunteer Bidding Blocked",
                        'description': default_volunteer_no_bid_msg})
    messages.error(request, user_message[0].description)
    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))


@log_func
def CreateVolunteerView(request):
    page_title = 'Volunteer'
    view_title = "Volunteer at the Expo"
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('register',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('volunteer_create',
                                            urlconf='gbe.urls'))

    profile = validate_profile(request, require=False)
    formset = []
    if not profile or not profile.complete:
        user_message = UserMessage.objects.get_or_create(
            view='CreateVolunteerView',
            code="PROFILE_INCOMPLETE",
            defaults={
                'summary': "Volunteer Profile Incomplete",
                'description': no_profile_msg})
        messages.warning(request, user_message[0].description)
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('volunteer_create',
                                            urlconf='gbe.urls'))
    try:
        conference = Conference.objects.filter(accepting_bids=True).first()
        windows = conference.windows()
        available_interests = AvailableInterest.objects.filter(
            visible=True).order_by('interest')
    except:
        return no_vol_bidding(request)

    try:
        existing_bid = profile.volunteering.get(b_conference=conference)
        user_message = UserMessage.objects.get_or_create(
            view='CreateVolunteerView',
            code="FOUND_EXISTING_BID",
            defaults={
                'summary': "Existing Volunteer Offer Found",
                'description': existing_volunteer_msg})
        messages.success(request, user_message[0].description)
        return HttpResponseRedirect(
            reverse(
                'volunteer_edit',
                urlconf='gbe.urls',
                args=[existing_bid.id]))
    except:
        pass

    if len(windows) == 0 or len(available_interests) == 0:
        return no_vol_bidding(request)

    if request.method == 'POST':
        form = VolunteerBidForm(
            request.POST,
            available_windows=windows,
            unavailable_windows=windows)
        formset = [
            VolunteerInterestForm(
                request.POST,
                initial={'interest': interest},
                prefix=str(interest.pk)
                ) for interest in available_interests]
        valid_interests, like_one_thing = validate_interests(formset)

        if form.is_valid() and valid_interests and like_one_thing:
            volunteer = form.save(commit=False)
            volunteer.b_conference = conference
            volunteer.profile = profile
            if 'submit' in request.POST.keys():
                volunteer.submitted = True
                volunteer.save()
                for window in form.cleaned_data['available_windows']:
                    volunteer.available_windows.add(window)
                for window in form.cleaned_data['unavailable_windows']:
                    volunteer.unavailable_windows.add(window)
                for interest_form in formset:
                    vol_interest = interest_form.save(commit=False)
                    vol_interest.volunteer = volunteer
                    vol_interest.save()

                notify_reviewers_on_bid_change(
                    profile,
                    "Volunteer",
                    "Submission",
                    conference,
                    'Volunteer Reviewers',
                    reverse(
                        'volunteer_review', urlconf='gbe.urls'))
                user_message = UserMessage.objects.get_or_create(
                    view='CreateVolunteerView',
                    code="SUBMIT_SUCCESS",
                    defaults={
                        'summary': "Volunteer Submit Success",
                        'description': default_volunteer_submit_msg})
                messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            formset += [form]
            if not like_one_thing:
                user_message = UserMessage.objects.get_or_create(
                    view='CreateVolunteerView',
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
        title = 'volunteer bid: %s' % profile.display_name
        for interest in available_interests:
            formset += [VolunteerInterestForm(
                initial={'interest': interest},
                prefix=str(interest.pk))]
        formset += [VolunteerBidForm(
            initial={'profile': profile,
                     'b_title': title,
                     'description': 'volunteer bid',
                     'submitted': True},
            available_windows=windows,
            unavailable_windows=windows)]
        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': formset,
                       'page_title': page_title,
                       'view_title': view_title,
                       'nodraft': 'Submit'})
