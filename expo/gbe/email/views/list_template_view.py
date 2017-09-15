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
from django.contrib import messages
from gbe.models import UserMessage
from gbetext import (
    no_profile_msg,
)
from gbe.functions import validate_profile
from gbe.email.functions import get_user_email_templates


class ListTemplateView(View):
    page_title = 'Manage Email Templates'
    view_title = 'Choose a Template'

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

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)
        return render(
            request,
            'gbe/email/list_email_template.tmpl',
            {"email_templates": get_user_email_templates(self.user),
             "page_title": self.page_title,
             "view_title": self.view_title, }
            )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListTemplateView, self).dispatch(*args, **kwargs)
