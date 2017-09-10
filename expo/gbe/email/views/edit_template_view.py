from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from post_office.models import EmailTemplate
from gbe.models import UserMessage
from gbetext import (
    no_profile_msg,
)
from gbe.email.forms import EmailTemplateForm
from expo.gbe_logging import log_func
from gbe.functions import validate_profile


class EditTemplateView(View):
    page_title = 'Edit Email Template'
    view_title = 'Edit Email Template'
    submit_button = 'Save Template'

    def groundwork(self, request, args, kwargs):
        self.user = validate_profile(request, require=False)
        if not self.user or not self.user.complete:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PROFILE_INCOMPLETE",
                defaults={
                    'summary': "%s Profile Incomplete",
                    'description': no_profile_msg})
            messages.warning(request, user_message[0].description)
            return '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'),
                reverse('%s_create' % self.bid_type.lower(),
                        urlconf='gbe.urls'))

        self.template = None
        if "template_name" in kwargs:
            template_name = kwargs.get("template_name")
            self.template = EmailTemplate.objects.get(
                name=template_name)
        else:
            raise Http404

    def get_edit_template_form(self, request):
        self.form = EmailTemplateForm(
            instance=self.template)

        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [self.form],
             'nodraft': self.submit_button,
             'page_title': self.page_title,
             'view_title': self.view_title}
        )

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)

        return self.get_edit_template_form(request) 

    @never_cache
    @log_func
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditTemplateView, self).dispatch(*args, **kwargs)
