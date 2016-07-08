from django.shortcuts import render
from expo.gbe_logging import log_func
from gbe.models import (
    Conference,
    Vendor,
)


@log_func
def FashionFaireView(request):
    '''
    The Vintage Fashion Faire.  Glorified vendor list
    '''
    current_conference = Conference.current_conf()
    if request.GET:
        conference = Conference.by_slug(request.GET.get('conference', None))
    else:
        conference = current_conference
    vendors = list(Vendor.objects.filter(
        accepted=3,
        b_conference=conference))
    vendor_rows = [vendors[i*3:i*3+3] for i in range(len(vendors)/3)]
    if len(vendors) % 3 > 0:
        vendor_rows.append(vendors[-(len(vendors) % 3):])
    template = 'gbe/fashionfair.tmpl'
    context = {'vendor_rows': vendor_rows}
    return render(request, template, context)
