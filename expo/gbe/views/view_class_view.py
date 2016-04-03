from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)


from expo.gbe_logging import log_func
from gbe.models import Class
from gbe.forms import (
    ClassBidForm,
    PersonaForm,
)
from gbe.functions import validate_perms

@login_required
@log_func
def ViewClassView(request, class_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''
    classbid = get_object_or_404(Class, id=class_id)
    if classbid.teacher.contact != request.user.profile:
        validate_perms(request, ('Class Reviewers',), require=True)
    classform = ClassBidForm(instance=classbid, prefix='The Class')
    teacher = PersonaForm(instance=classbid.teacher,
                          prefix='The Teacher(s)')

    return render(request, 'gbe/bid_view.tmpl',
                  {'readonlyform': [classform, teacher]})
