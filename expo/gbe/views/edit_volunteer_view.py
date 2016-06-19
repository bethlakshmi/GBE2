from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.forms import VolunteerBidForm
from gbe.functions import validate_perms
from gbe.models import Volunteer


@login_required
@log_func
def EditVolunteerView(request, volunteer_id):
    page_title = "Edit Volunteer Bid"
    view_title = "Edit Submitted Volunteer Bid"
    reviewer = validate_perms(request, ('Volunteer Coordinator',))
    the_bid = get_object_or_404(Volunteer, id=volunteer_id)

    if request.method == 'POST':
        form = VolunteerBidForm(
            request.POST,
            instance=the_bid,
            available_windows=the_bid.b_conference.windows(),
            unavailable_windows=the_bid.b_conference.windows())

        if form.is_valid():
            the_bid = form.save(commit=True)
            the_bid.available_windows.clear()
            the_bid.unavailable_windows.clear()
            for window in form.cleaned_data['available_windows']:
                the_bid.available_windows.add(window)
            for window in form.cleaned_data['unavailable_windows']:
                the_bid.unavailable_windows.add(window)

            return HttpResponseRedirect(reverse('volunteer_review',
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': [form],
                           'page_title': page_title,
                           'view_title': view_title,
                           'nodraft': 'Submit'})
    else:
        if len(the_bid.interests.strip()) > 0:
            interests_initial = eval(the_bid.interests)
        else:
            interests_initial = []
        form = VolunteerBidForm(
            instance=the_bid,
            initial={'interests': interests_initial},
            available_windows=the_bid.b_conference.windows(),
            unavailable_windows=the_bid.b_conference.windows())

        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': [form],
                       'page_title': page_title,
                       'view_title': view_title,
                       'nodraft': 'Submit'})
