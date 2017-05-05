from gbe.views import CreateBidView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms.models import ModelChoiceField
from django.core.urlresolvers import reverse
from gbe.duration import Duration
from gbe.models import (
    Persona,
)
from gbe_forms_text import avoided_constraints_popup_text
from gbe.forms import (
    ClassBidForm,
    ClassBidDraftForm,
)
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)


class CreateClassView(CreateBidView):
    page_title = "Submit a Class"
    view_title = "Submit a Class"
    draft_fields = ['b_title', 'teacher']
    submit_fields = ['b_title',
                     'teacher',
                     'b_description',
                     'schedule_constraints']
    bid_type = "Class"
    has_draft = True
    submit_msg = default_class_submit_msg
    draft_msg = default_class_draft_msg
    submit_form = ClassBidForm
    draft_form = ClassBidDraftForm
    prefix = "theclass"

    def set_up_form(self):
        if not self.form:
            self.form = self.submit_form(
                initial={'owner': self.owner,
                         'teacher': self.teachers[0]},
                prefix=self.prefix)

        q = Persona.objects.filter(
        performer_profile_id=self.owner.resourceitem_id)
        self.form.fields['teacher'] = ModelChoiceField(queryset=q)

    def user_not_ready_redirect(self):
        if len(self.teachers) == 0:
            return HttpResponseRedirect(reverse(
                'persona_create',
                urlconf='gbe.urls') +
                '?next=' + reverse(
                    'class_create',
                    urlconf='gbe.urls'))

    def make_context(self):
        context = super(CreateClassView, self).make_context()
        context['popup_text'] = avoided_constraints_popup_text
        return context

    def groundwork(self, request, args, kwargs):
        super(CreateClassView, self).groundwork(request, args, kwargs)
        self.teachers = self.owner.personae.all()

    def set_valid_form(self, request):
        self.bid_object.duration = Duration(
            minutes=self.bid_object.length_minutes)
        self.bid_object.b_conference = self.conference
        self.bid_object.e_conference = self.conference
        self.bid_object = self.form.save(commit=True)

    def fee_paid(self):
        return True
    
    def get_invalid_response(self, request):
        self.get_create_form(request)
        context = self.make_context()
        return render(
            request,
            'gbe/bid.tmpl',
            context
            )

    
