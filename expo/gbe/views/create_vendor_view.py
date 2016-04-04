from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.forms import VendorBidForm
from gbe.models import (
    Conference,
    Vendor,
)
from gbe.functions import validate_profile
from gbe.ticketing_idd_interface import (
    vendor_submittal_link,
    verify_vendor_app_paid,
)


@login_required
@log_func
def CreateVendorView(request):
    title = "Vendor Application"
    fee_link = vendor_submittal_link(request.user.id)

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('vendor_create',
                                            urlconf='gbe.urls'))
    if request.method == 'POST':
        form = VendorBidForm(request.POST, request.FILES)
        if form.is_valid():
            conference = Conference.objects.filter(accepting_bids=True).first()
            vendor = form.save(commit=False)
            vendor.conference = conference
            vendor = form.save()
        else:
            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': [form],
                           'page_title': title,
                           'fee_link': fee_link,
                           'view_title': title})
        if 'submit' in request.POST.keys():
            problems = vendor.validation_problems_for_submit()
            if problems:
                return render(request,
                              'gbe/bid.tmpl',
                              {'forms': [form],
                               'page_title': page_title,
                               'view_title': view_title,
                               'fee_link': fee_link,
                               'errors': problems})
            else:
                '''
                If this is a formal submit request, did they pay?
                They can't submit w/out paying
                '''
                if verify_vendor_app_paid(request.user.username):
                    vendor.submitted = True
                    conference = Conference.objects.filter(
                        accepting_bids=True).first()
                    vendor.conference = conference
                    vendor.save()
                    return HttpResponseRedirect(reverse('home',
                                                        urlconf='gbe.urls'))
                else:
                    page_title = 'Vendor Payment'
                    return render(
                        request, 'gbe/please_pay.tmpl',
                        {'link': fee_link,
                         'page_title': page_title}
                    )
        else:   # saving a draft
            if form.is_valid():
                vendor = form.save()
                return HttpResponseRedirect(reverse('home',
                                                    urlconf='gbe.urls'))
    else:
        form = VendorBidForm(initial={'profile': profile,
                                      'physical_address': profile.address})
        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': [form],
                       'fee_link': fee_link,
                       'page_title': title,
                       'view_title': title})
