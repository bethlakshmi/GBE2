from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.ticketing_idd_interface import (
    vendor_submittal_link,
    verify_vendor_app_paid,
)
from gbe.forms import VendorBidForm
from gbe.functions import validate_profile
from gbe.models import (
    UserMessage,
    Vendor
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg
)


@login_required
@log_func
def EditVendorView(request, vendor_id):
    page_title = 'Edit Vendor Application'
    view_title = 'Edit Your Vendor Application'
    form = VendorBidForm(prefix='thebiz')
    fee_link = vendor_submittal_link(request.user.id)
    profile = validate_profile(request, require=False)

    if not profile:
        return HttpResponseRedirect(reverse('profile', urlconf='gbe.urls'))

    vendor = get_object_or_404(Vendor, id=vendor_id)
    if vendor.profile != profile:
        raise Http404

    if request.method == 'POST':
        '''
        If this is a formal submit request, then do all the checking.
        If this is a draft, only a few fields are needed, use a form with fewer
        required fields (same model)
        '''
        form = VendorBidForm(request.POST,
                             request.FILES,
                             instance=vendor,
                             prefix='thebiz')
        if form.is_valid():
            form.save()
        else:
            return render(
                request,
                'gbe/bid.tmpl',
                {'forms': [form],
                 'page_title': page_title,
                 'view_title': view_title,
                 'fee_link': fee_link}
            )

        if 'submit' in request.POST.keys():
            '''
            If this is a formal submit request, did they pay?
            They can't submit w/out paying
            '''
            if verify_vendor_app_paid(request.user.username):
                vendor.submitted = True
                vendor.save()
                user_message = UserMessage.objects.get_or_create(
                    view='EditVendorView',
                    code="SUBMIT_SUCCESS",
                    defaults={
                        'summary': "Vendor Edit & Submit Success",
                        'description': default_vendor_submit_msg})
            else:
                page_title = 'Vendor Payment'
                return render(
                    request, 'gbe/please_pay.tmpl',
                    {'link': fee_link,
                     'page_title': page_title}
                )
        else:
            user_message = UserMessage.objects.get_or_create(
                view='EditVendorView',
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "Vendor Edit Draft Success",
                    'description': default_vendor_draft_msg})
        messages.success(request, user_message[0].description)
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else:
        if len(vendor.help_times.strip()) > 0:
            help_times_initial = eval(vendor.help_times)
        else:
            help_times_initial = []
        form = VendorBidForm(instance=vendor,
                             prefix='thebiz',
                             initial={'help_times': help_times_initial})

        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [form],
             'page_title': page_title,
             'view_title': view_title,
             'fee_link': fee_link}
        )
