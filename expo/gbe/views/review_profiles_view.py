from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from expo.gbe_logging import log_func
from gbe.models import Profile
from gbe.functions import validate_perms



@login_required
@log_func
def ReviewProfilesView(request):
    admin_profile = validate_perms(request, ('Registrar',
                                             'Volunteer Coordinator',
                                             'Act Coordinator',
                                             'Conference Coordinator',
                                             'Vendor Coordinator',
                                             'Ticketing - Admin'))
    header = Profile().review_header
    profiles = Profile.objects.all()
    rows = []
    for aprofile in profiles:
        bid_row = {}
        bid_row['profile'] = aprofile.review_summary
        bid_row['id'] = aprofile.resourceitem_id
        bid_row['actions'] = []
        if 'Registrar' in request.user.profile.privilege_groups:
            bid_row['actions'] += [
                {'url': reverse('admin_profile',
                                urlconf='gbe.urls',
                                args=[aprofile.resourceitem_id]),
                 'text': "Update"}]
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
