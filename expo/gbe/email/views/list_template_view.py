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
from gbe.models import (
    Show,
    UserMessage
)
from gbetext import (
    acceptance_states,
    email_template_desc,
    no_profile_msg,
    unique_email_templates,
)
from gbe.functions import validate_profile


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

        template_set = []
        for priv in self.user.get_email_privs():
            template_set += [{
                'name': "%s submission notification" % priv,
                'description': email_template_desc[
                    "submission notification"] % priv,
                'category': priv,}]
            for state in acceptance_states:
                if priv == "act" and state[1] == "Accepted":
                    for show in Show.objects.filter(
                            e_conference__status__in=('upcoming', 'ongoing')):
                        template_set += [{
                            'name': "%s %s - %s" % (priv,
                                                  state[1].lower(),
                                                  show.e_title.lower()),
                            'description': email_template_desc[
                                "%s %s" % (priv,
                                           state[1].lower())] % show.e_title,
                            'category': priv}]
                else:
                    template_set += [{
                        'name': "%s %s" % (priv, state[1].lower()),
                        'description': email_template_desc[state[1]] % priv,
                        'category': priv}]
            if priv in unique_email_templates:
                template_set += unique_email_templates[priv]
        return render(
            request,
            'gbe/email/list_email_template.tmpl',
            {"email_templates": sorted(
                template_set,
                key=lambda item: (item['name'], item['category'])),
             "page_title": self.page_title,
             "view_title": self.view_title,}
            )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListTemplateView, self).dispatch(*args, **kwargs)
