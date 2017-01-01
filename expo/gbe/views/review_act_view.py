from django.core.urlresolvers import reverse
from django.forms import ModelChoiceField
from gbe.models import (
    Act,
    ActBidEvaluation,
    Show,
)
from gbe.forms import (
    ActBidEvaluationForm,
    ActEditForm,
    BidStateChangeForm,
)
from gbe.views import ReviewBidView
from gbe.views.functions import get_performer_form


class ReviewActView(ReviewBidView):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    '''
    reviewer_permissions = ('Act Reviewers', )
    coordinator_permissions = ('Act Coordinator',)
    bid_prefix = "The Act"
    bidder_prefix = "The Performer(s)"
    bid_form_type = ActEditForm
    object_type = Act
    review_list_view_name = 'act_review_list'
    bid_view_name = 'act_view'
    changestate_view_name = 'act_changestate'
    bid_evaluation_type = ActBidEvaluation
    bid_evaluation_form_type = ActBidEvaluationForm

    def groundwork(self, request, args, kwargs):
        super(ReviewActView, self).groundwork(request, args, kwargs)
        self.bidder = get_performer_form(self.object.performer)

        audio_info = self.object.tech.audio
        stage_info = self.object.tech.stage
        initial = {
            'track_title': audio_info.track_title,
            'track_artist': audio_info.track_artist,
            'track_duration': audio_info.track_duration,
            'act_duration': stage_info.act_duration
        }
        self.create_object_form(initial=initial)
        self.readonlyform_pieces = [self.object_form, self.bidder]

    def create_action_form(self, act):
        self.actionform = BidStateChangeForm(instance=act)

        start = Show.objects.filter(
            scheduler_events__resources_allocated__resource__actresource___item=act).first()
        if start is None:
            start = ""
        q = Show.objects.filter(
            conference=act.conference,
            scheduler_events__isnull=False).order_by(
                'scheduler_events__starttime')
        self.actionform.fields['show'] = ModelChoiceField(
            queryset=q,
            empty_label=None,
            label='Pick a Show',
            initial=start)
        self.actionURL = reverse(self.changestate_view_name,
                                 urlconf='gbe.urls',
                                 args=[act.id])
