from django.contrib.auth.decorators import login_required
from django.template import (
    loader,
    RequestContext,
)
from django.http import HttpResponse

from expo.gbe_logging import log_func
from gbe.forms import ClassProposalForm


@log_func
def ProposeClassView(request):
    '''
    Handle suggestions for classes from the great unwashed
    '''
    if request.method == 'POST':
        form = ClassProposalForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
            # TO DO: this should be a better redirect
        else:
            template = loader.get_template('gbe/class_proposal.tmpl')
            context = RequestContext(request, {'form': form})
            return HttpResponse(template.render(context))
    else:
        form = ClassProposalForm()
        template = loader.get_template('gbe/class_proposal.tmpl')
        context = RequestContext(request, {'form': form})
        return HttpResponse(template.render(context))
