from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.models import Profile
from gbe.functions import validate_perms


@login_required
@log_func
@never_cache
def ReviewProfilesView(request):
    admin_profile = validate_perms(request, ('Registrar',
                                             'Volunteer Coordinator',
                                             'Act Coordinator',
                                             'Conference Coordinator',
                                             'Vendor Coordinator',
                                             'Ticketing - Admin'))
    header = ['Name',
              'Username',
              'Last Login',
              'Contact Info',
              'Action']
    profiles = Profile.objects.filter(user_object__is_active=True)
    rows = []
    for aprofile in profiles:
        bid_row = {}
        bid_row['profile'] = (
            aprofile.display_name,
            aprofile.user_object.username,
            aprofile.user_object.last_login)
        bid_row['contact_info'] = {
            'contact_email': aprofile.user_object.email,
            'purchase_email': aprofile.purchase_email,
            'phone': aprofile.phone
        }
        bid_row['id'] = aprofile.resourceitem_id
        bid_row['actions'] = []
        if 'Registrar' in request.user.profile.privilege_groups:
            bid_row['actions'] += [
                {'url': reverse('admin_profile',
                                urlconf='gbe.urls',
                                args=[aprofile.resourceitem_id]),
                 'text': "Update"}]
            bid_row['actions'] += [
                {'url': reverse('delete_profile',
                                urlconf='gbe.urls',
                                args=[aprofile.resourceitem_id]),
                 'text': "Delete"}]
        bid_row['actions'] += [
            {'url': reverse(
                'admin_landing_page',
                urlconf='gbe.urls',
                args=[aprofile.resourceitem_id]),
             'text': "View Landing Page"}
        ]
        rows.append(bid_row)

    return render(request, 'gbe/profile_review.tmpl',
                  {'header': header, 'rows': rows})
