from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import (
    loader,
    Context,
)
from django.shortcuts import render

from expo.gbe_logging import log_func
from gbe.forms import VolunteerBidForm
from gbe.models import (
    Conference,
    UserMessage
)
from gbe.functions import (
    mail_to_group,
    validate_profile,
)
from gbetext import (
    default_volunteer_submit_msg
)

@login_required
@log_func
def CreateVolunteerView(request):
    page_title = 'Volunteer'
    view_title = "Volunteer at the Expo"
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('volunteer_create',
                                            urlconf='gbe.urls'))
    if request.method == 'POST':
        form = VolunteerBidForm(
            request.POST,
            available_windows=Conference.current_conf().windows(),
            unavailable_windows=Conference.current_conf().windows())
        if form.is_valid():
            volunteer = form.save(commit=False)
            # hack TO DO: do this better
            conference = Conference.objects.filter(accepting_bids=True).first()
            volunteer.conference = conference
            volunteer.profile = profile
            if 'submit' in request.POST.keys():
                volunteer.submitted = True
                volunteer.save()
                for window in form.cleaned_data['available_windows']:
                    volunteer.available_windows.add(window)
                for window in form.cleaned_data['unavailable_windows']:
                    volunteer.unavailable_windows.add(window)

                message = loader.get_template('gbe/email/bid_submitted.tmpl')
                c = Context({'bidder': profile.display_name,
                             'bid_type': 'volunteer',
                             'review_url': reverse('volunteer_review',
                                                   urlconf='gbe.urls')})
                mail_to_group("Volunteer Offer Submitted", message.render(c),
                              'Volunteer Reviewers')
                user_message = UserMessage.objects.get_or_create(
                    view='CreateVolunteerView',
                    code="SUBMIT_SUCCESS",
                    defaults={
                        'summary': "Volunteer Submit Success",
                        'description': default_volunteer_submit_msg})
                messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': [form],
                           'page_title': page_title,
                           'view_title': view_title,
                           'nodraft': 'Submit'})
    else:
        title = 'volunteer bid: %s' % profile.display_name
        form = VolunteerBidForm(
            initial={'profile': profile,
                     'title': title,
                     'description': 'volunteer bid',
                     'submitted': True},
            available_windows=Conference.current_conf().windows(),
            unavailable_windows=Conference.current_conf().windows())
        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': [form],
                       'page_title': page_title,
                       'view_title': view_title,
                       'nodraft': 'Submit'})
