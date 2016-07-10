from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.forms import VendorBidForm
from gbe.models import (
    Conference,
    Vendor,
    UserMessage
)
from gbe.functions import validate_profile
from gbe.ticketing_idd_interface import (
    vendor_submittal_link,
    verify_vendor_app_paid,
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg
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
                user_message = UserMessage.objects.get_or_create(
                    view='CreateVendorView',
                    code="SUBMIT_SUCCESS",
                    defaults={
                        'summary': "Vendor Submit Success",
                        'description': default_vendor_submit_msg})
                messages.success(request, user_message[0].description)
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
                user_message = UserMessage.objects.get_or_create(
                    view='CreateVendorView',
                    code="DRAFT_SUCCESS",
                    defaults={
                        'summary': "Vendor Draft Success",
                        'description': default_vendor_draft_msg})
                vendor = form.save()
                messages.success(request, user_message[0].description)
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
