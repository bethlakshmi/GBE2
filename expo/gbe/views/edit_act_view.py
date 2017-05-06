from gbe.views import EditBidView
from django.http import Http404
from django.forms import ModelChoiceField
from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)
from gbe.models import (
    Act,
    Performer,
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


class EditActView(EditBidView):
    page_title = 'Edit Act Proposal'
    view_title = 'Edit Your Act Proposal'
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
        super(EditActView, self).groundwork(request, args, kwargs)
        if self.bid_object.performer.contact != self.owner:
            raise Http404

    def get_initial(self):
        audio_info = self.bid_object.tech.audio
        stage_info = self.bid_object.tech.stage
        return {'track_title': audio_info.track_title,
                'track_artist': audio_info.track_artist,
                'track_duration': audio_info.track_duration,
                'act_duration': stage_info.act_duration}

    def set_up_form(self):
        if not self.form:
            self.form = self.submit_form(
                instance=self.bid_object,
                prefix='theact',
                initial=self.get_initial())
        q = Performer.objects.filter(contact=self.owner)
        self.form.fields['performer'] = ModelChoiceField(queryset=q)

    def make_context(self):
        context = super(EditActView, self).make_context()
        context['fee_link'] = self.fee_link
        return context

    def check_validity(self, request):
        self.audioform = AudioInfoForm(request.POST, prefix='theact',
                                  instance=self.bid_object.tech.audio)
        self.stageform = StageInfoForm(request.POST, prefix='theact',
                                  instance=self.bid_object.tech.stage)
        return all([self.form.is_valid(),
                    self.audioform.is_valid(),
                    self.stageform.is_valid()])

    def set_valid_form(self, request):
        self.bid_object.tech.audio = self.audioform.save()
        self.bid_object.tech.stage = self.stageform.save()
        self.bid_object.tech.save()
        self.form.save()

    def get_invalid_response(self, request):
        return display_invalid_act(
            request,
            self.make_context(),
            self.form,
            self.bid_object.b_conference,
            self.owner,
            'EditActView')

    def fee_paid(self):
        return verify_performer_app_paid(
            self.owner.user_object.username,
            self.bid_object.b_conference)
