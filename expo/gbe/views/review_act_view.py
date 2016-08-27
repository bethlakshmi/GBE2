from django.core.urlresolvers import reverse
from django.forms import ModelChoiceField
from gbe.models import (
    Act,
    Show,
)
from gbe.forms import (
    ActEditForm,
    BidStateChangeForm,
    PersonaForm,
)
from gbe.views import ReviewBidView


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
    bidder_form_type = PersonaForm
    bid_form_type = ActEditForm
    object_type = Act
    review_list_view_name = 'act_review_list'
    bid_view_name = 'act_view'
    changestate_view_name = 'act_changestate'

    def groundwork(self, request, args, kwargs):
        super(ReviewActView, self).groundwork(request, args, kwargs)
        self.bidder = self.bidder_form_type(instance=self.object.performer,
                                            prefix=self.bidder_prefix)

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

<<<<<<< HEAD
def _create_action_form(act):
    actionform = BidStateChangeForm(instance=act)
    # This requires that the show be scheduled - seems reasonable in
    # current workflow and lets me order by date.  Also - assumes
    # that shows are only scheduled once
    start = Show.objects.filter(
        scheduler_events__resources_allocated__resource__actresource___item=act).first()
    if not start:
        start = ""
    q = Show.objects.filter(
        e_conference=act.b_conference,
        scheduler_events__isnull=False).order_by(
            'scheduler_events__starttime')
    actionform.fields['show'] = ModelChoiceField(
        queryset=q,
        empty_label=None,
        label='Pick a Show',
        initial=start)
    actionURL = reverse('act_changestate',
                        urlconf='gbe.urls',
                        args=[act.id])
    return actionform, actionURL
||||||| merged common ancestors
def _create_action_form(act):
    actionform = BidStateChangeForm(instance=act)
    # This requires that the show be scheduled - seems reasonable in
    # current workflow and lets me order by date.  Also - assumes
    # that shows are only scheduled once
    try:
        start = Show.objects.filter(
            scheduler_events__resources_allocated__resource__actresource___item=act)[0]
    except:
        start = ""
    q = Show.objects.filter(
        conference=act.conference,
        scheduler_events__isnull=False).order_by(
            'scheduler_events__starttime')
    actionform.fields['show'] = ModelChoiceField(
        queryset=q,
        empty_label=None,
        label='Pick a Show',
        initial=start)
    actionURL = reverse('act_changestate',
                        urlconf='gbe.urls',
                        args=[act.id])
    return actionform, actionURL
=======
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
        self.actionURL = reverse('act_changestate',
                                 urlconf='gbe.urls',
                                 args=[act.id])
>>>>>>> master
