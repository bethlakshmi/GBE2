from gbe.views import MakeBidView
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms import ModelChoiceField
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
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
    AudioInfoForm,
    StageInfoForm,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
)
from gbe.views.act_display_functions import display_invalid_act


class MakeActView(MakeBidView):
    page_title = 'Act Proposal'
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
    bid_class = Act

    def groundwork(self, request, args, kwargs):
        super(MakeActView, self).groundwork(request, args, kwargs)
        if self.bid_object and (
                self.bid_object.performer.contact != self.owner):
            raise Http404
        elif self.owner:
            self.personae = self.owner.personae.all()
        self.fee_link = performer_act_submittal_link(request.user.id)

    def get_initial(self):
        initial = {}
        if self.bid_object:
            audio_info = self.bid_object.tech.audio
            stage_info = self.bid_object.tech.stage
            initial = {
                'track_title': audio_info.track_title,
                'track_artist': audio_info.track_artist,
                'track_duration': audio_info.track_duration,
                'act_duration': stage_info.act_duration}
        else:
            initial = {
                'owner': self.owner,
                'performer': self.personae[0],
                'b_conference': self.conference}
        return initial

    def user_not_ready_redirect(self):
        if len(self.personae) == 0:
            return HttpResponseRedirect(
                reverse('persona_create', urlconf='gbe.urls') +
                '?next=%s' % reverse('act_create', urlconf='gbe.urls'))

    def set_up_form(self):
        if not self.form:
            if self.bid_object:
                self.form = self.submit_form(
                    prefix='theact',
                    instance=self.bid_object,
                    initial=self.get_initial())
            else:
                self.form = self.submit_form(
                    prefix='theact',
                    initial=self.get_initial())
        q = Performer.objects.filter(contact=self.owner)
        self.form.fields['performer'] = ModelChoiceField(queryset=q)

    def make_context(self):
        context = super(MakeActView, self).make_context()
        context['fee_link'] = self.fee_link
        return context

    def check_validity(self, request):
        self.audioform = AudioInfoForm(request.POST, prefix='theact')
        self.stageform = StageInfoForm(request.POST, prefix='theact')
        if hasattr(self.bid_object, 'tech'):
            self.audioform.instance = self.bid_object.tech.audio
            self.stageform.instance = self.bid_object.tech.stage
        return all([self.form.is_valid(),
                    self.audioform.is_valid(),
                    self.stageform.is_valid()])

    def set_valid_form(self, request):
        if not hasattr(self.bid_object, 'tech'):
            techinfo = TechInfo()
            lightinginfo = LightingInfo()
            lightinginfo.save()
            techinfo.lighting = lightinginfo
        else:
            techinfo = self.bid_object.tech

        techinfo.audio = self.audioform.save()
        techinfo.stage = self.stageform.save()
        techinfo.save()
        self.bid_object.tech = techinfo
        self.bid_object.submitted = False
        self.bid_object.accepted = False
        self.bid_object.save()
        self.form.save()

    def get_invalid_response(self, request):
        return display_invalid_act(
            request,
            self.make_context(),
            self.form,
            self.conference,
            self.owner,
            'MakeActView')

    def fee_paid(self):
        return verify_performer_app_paid(
            self.owner.user_object.username,
            self.bid_object.b_conference)
