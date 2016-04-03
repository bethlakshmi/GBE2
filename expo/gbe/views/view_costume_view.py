from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from expo.gbe_logging import log_func
from gbe.functions import validate_perms
from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
)
from gbe.models import Costume

@login_required
@log_func
def ViewCostumeView(request, costume_id):
    '''
    Show a costume proposal
    '''
    costumebid = get_object_or_404(Costume, id=costume_id)
    if costumebid.profile != request.user.profile:
        validate_perms(request, ('Costume Reviewers',), require=True)
    form = CostumeBidSubmitForm(instance=costumebid, prefix='')
    details = CostumeDetailsSubmitForm(instance=costumebid)

    return render(request, 'gbe/bid_view.tmpl',
                  {'readonlyform': [form, details]})
