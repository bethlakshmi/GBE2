from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import (
    loader,
    RequestContext,
)
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from gbe.models import (
    Act,
    Class,
    Costume,
    Profile,
    Vendor,
    Volunteer,
    Event,
    UserMessage,
)
from gbe.ticketing_idd_interface import (
    get_purchased_tickets,
)
from gbetext import (
    acceptance_states,
    interested_explain_msg,
)
from gbe.functions import (
    validate_perms,
    validate_profile,
)
from expo.gbe_logging import log_func
from scheduler.idd import get_schedule


@login_required
@log_func
@never_cache
def LandingPageView(request, profile_id=None, historical=False):
    historical = "historical" in request.GET.keys()
    standard_context = {}
    standard_context['events_list'] = Event.objects.all()[:5]
    if (profile_id):
        admin_profile = validate_perms(request, ('Registrar',
                                                 'Volunteer Coordinator',
                                                 'Act Coordinator',
                                                 'Class Coordinator',
                                                 'Vendor Coordinator',
                                                 'Ticketing - Admin'))
        viewer_profile = get_object_or_404(Profile, pk=profile_id)
        admin_message = "You are viewing a user's profile, not your own."
    else:
        viewer_profile = validate_profile(request, require=False)
        admin_message = None

    template = loader.get_template('gbe/landing_page.tmpl')
    class_to_class_name = {Act: "Act",
                           Class: "Class",
                           Costume: "Costume",
                           Vendor: "Vendor",
                           Volunteer: "Volunteer"}
    class_to_view_name = {Act: 'act_review',
                          Class: 'class_review',
                          Costume: 'costume_review',
                          Vendor: 'vendor_review',
                          Volunteer: 'volunteer_review'}

    if viewer_profile:
        bids_to_review = []
        for bid in viewer_profile.bids_to_review():
            bid_type = class_to_class_name.get(bid.__class__, "UNKNOWN")
            view_name = class_to_view_name.get(bid.__class__, None)
            url = ""
            if view_name:
                url = reverse(view_name,
                              urlconf='gbe.urls',
                              args=[str(bid.id)])
            bids_to_review += [{'bid': bid,
                                'url': url,
                                'action': "Review",
                                'bid_type': bid_type}]

        context = RequestContext(
            request,
            {'profile': viewer_profile,
             'historical': historical,
             'alerts': viewer_profile.alerts(historical),
             'standard_context': standard_context,
             'personae': viewer_profile.get_personae(),
             'troupes': viewer_profile.get_troupes(),
             'combos': viewer_profile.get_combos(),
             'acts': viewer_profile.get_acts(historical),
             'shows': viewer_profile.get_shows(),
             'classes': viewer_profile.is_teaching(historical),
             'proposed_classes': viewer_profile.proposed_classes(historical),
             'vendors': viewer_profile.vendors(historical),
             'volunteering': viewer_profile.get_volunteerbids(),
             'costumes': viewer_profile.get_costumebids(historical),
             'review_items': bids_to_review,
             'tickets': get_purchased_tickets(viewer_profile.user_object),
             'acceptance_states': acceptance_states,
             'admin_message': admin_message,
             'bookings': get_schedule(
                viewer_profile.user_object).schedule_items,
             })
        if not historical:
            user_message = UserMessage.objects.get_or_create(
                view="LandingPageView",
                code="ABOUT_INTERESTED",
                defaults={
                    'summary': "About Interested Attendees",
                    'description': interested_explain_msg})
            context['interested_info'] = user_message[0].description

    else:
        context = RequestContext(request,
                                 {'standard_context': standard_context})
    return HttpResponse(template.render(context))
