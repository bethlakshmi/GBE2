from gbe.views import CreateBidView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms import ModelChoiceField
from gbe.forms import (
    ActEditForm,
    ActEditDraftForm,
    AudioInfoForm,
    LightingInfoForm,
    StageInfoForm,
)

from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)

from gbe.models import (
    Act,
    AudioInfo,
    LightingInfo,
    Performer,
    StageInfo,
    TechInfo,
)
from gbe.views.act_display_functions import display_invalid_act
from gbe.functions import validate_profile
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
)


class CreateActView(CreateBidView):
    page_title = 'Propose Act'
    view_title = 'Propose an Act'
    draft_fields = ['b_title', 'performer']
    submit_fields = ['b_title',
                     'b_description',
                     'shows_preferences',
                     'performer', ]
    bid_type = "Act"
    has_draft = True
    submit_msg = default_act_submit_msg
    draft_msg = default_act_draft_msg
    submit_form = ActEditForm
    draft_form = ActEditDraftForm
    prefix = "theact"

    def set_up_form(self):
        if not self.form:
            self.form = ActEditForm(
                initial={'owner': self.owner,
                         'performer': self.personae[0],
                         'b_conference': self.conference,
                         },
                prefix='theact')
        q = Performer.objects.filter(contact=self.owner)
        self.form.fields['performer'] = ModelChoiceField(queryset=q)

    def user_not_ready_redirect(self):
        if len(self.personae) == 0:
            return HttpResponseRedirect(
                reverse('persona_create',
                        urlconf='gbe.urls') +
                        '?next=' +
                        reverse('act_create',
                                urlconf='gbe.urls'))

    def make_context(self):
        context = super(CreateActView, self).make_context()
        context['fee_link'] = self.fee_link
        return context
    
    def groundwork(self, request, args, kwargs):
        super(CreateActView, self).groundwork(request, args, kwargs)
        self.personae = self.owner.personae.all()
        self.fee_link = performer_act_submittal_link(request.user.id)

    def set_valid_form(self, request):
        techinfo = TechInfo()
        audioinfoform = AudioInfoForm(request.POST, prefix='theact')
        techinfo.audio = audioinfoform.save()
        stageinfoform = StageInfoForm(request.POST, prefix='theact')
        techinfo.stage = stageinfoform.save()
        lightinginfo = LightingInfo()
        lightinginfo.save()
        techinfo.lighting = lightinginfo
        techinfo.save()
        self.bid_object.tech = techinfo
        self.bid_object.submitted = False
        self.bid_object.accepted = False
        self.bid_object.save()

    def get_invalid_response(self, request):
        return display_invalid_act(
            request,
            {'forms': [self.form],
             'page_title': self.page_title,
             'view_title': self.view_title,
             'draft_fields': self.draft_fields,
             'fee_link': self.fee_link,
             'submit_fields': self.submit_fields},
             self.form,
             self.conference,
             self.owner,
             'CreateActView')

    def fee_paid(self):
        return verify_performer_app_paid(
            self.owner.user_object.username,
            self.conference)
