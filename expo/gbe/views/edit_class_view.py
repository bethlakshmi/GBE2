from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from expo.gbe_logging import log_func
from gbe.forms import (
    ClassBidForm,
    ClassBidDraftForm,
)
from gbe.models import (
    Class,
    UserMessage
)
from gbe.duration import Duration
from gbe.functions import validate_profile
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)


@login_required
@log_func
def EditClassView(request, class_id):
    '''
    Edit an existing class.
    '''
    page_title = "Edit Class"
    view_title = "Edit Your Class Proposal"

    owner = validate_profile(request, require=True)

    the_class = get_object_or_404(Class, id=class_id)
    teachers = owner.personae.all()
    draft_fields = Class().get_draft_fields

    if the_class.teacher not in teachers:
        raise Http404

    if request.method == 'POST':
        if 'submit' in request.POST.keys():
            form = ClassBidForm(request.POST, instance=the_class)
            user_message = UserMessage.objects.get_or_create(
                view='EditClassView',
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "Class Edit & Submit Success",
                    'description': default_class_submit_msg})
        else:
            form = ClassBidDraftForm(request.POST, instance=the_class)
            user_message = UserMessage.objects.get_or_create(
                view='EditClassView',
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "Class Edit Draft Success",
                    'description': default_class_draft_msg})

        if form.is_valid():
            the_class = form.save(commit=False)
            the_class.duration = Duration(minutes=the_class.length_minutes)
            the_class = form.save(commit=True)

            if 'submit' in request.POST.keys():
                if the_class.complete:
                    the_class.submitted = True
                else:
                    return render(
                        request,
                        'gbe/bid.tmpl',
                        {'forms': [form],
                         'page_title': page_title,
                         'view_title': view_title,
                         'draft_fields': draft_fields,
                         'errors': ['Cannot submit, class is not complete']}
                    )
            the_class.save()
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            fields, requiredsub = Class().get_bid_fields
            return render(
                request,
                'gbe/bid.tmpl',
                {'forms': [form],
                 'page_title': page_title,
                 'view_title': view_title,
                 'draft_fields': draft_fields,
                 'submit_fields': requiredsub}
            )
    else:
        form = ClassBidForm(instance=the_class)
        draft_fields = Class().get_draft_fields
        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [form],
             'page_title': page_title,
             'view_title': view_title,
             'draft_fields': draft_fields}
        )
