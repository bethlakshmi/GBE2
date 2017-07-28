from django.core.urlresolvers import reverse
from django.forms import (
    ChoiceField,
    ModelChoiceField,
)
from gbe.models import (
    Act,
    ActBidEvaluation,
    Show,
)
from scheduler.models import ActResource
from gbe.forms import (
    ActBidEvaluationForm,
    ActEditForm,
    BidStateChangeForm,
    SummerActForm,
)
from gbe.views import ReviewBidView
from gbe.views.functions import get_performer_form
from gbe.views.act_display_functions import (
    get_act_casting,
    get_act_form,
)
from gbetext import (
    act_casting_label,
)


class ReviewActView(ReviewBidView):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    '''
    reviewer_permissions = ('Act Reviewers', )
    coordinator_permissions = ('Act Coordinator',)
    object_type = Act
    review_list_view_name = 'act_review_list'
    bid_view_name = 'act_view'
    changestate_view_name = 'act_changestate'
    bid_evaluation_type = ActBidEvaluation
    bid_evaluation_form_type = ActBidEvaluationForm

    def groundwork(self, request, args, kwargs):
        super(ReviewActView, self).groundwork(request, args, kwargs)
        self.bidder = get_performer_form(self.object.performer)
        if self.object.b_conference.act_style == "summer":
            self.object_form = get_act_form(
                self.object,
                SummerActForm,
                "The Summer Act")
        else:
            self.object_form = get_act_form(
                self.object,
                ActEditForm,
                "The Act")
        self.readonlyform_pieces = [self.object_form, self.bidder]

    def create_action_form(self, act):

        self.actionform = BidStateChangeForm(instance=act)
        start = Show.objects.filter(
            scheduler_events__resources_allocated__resource__actresource___item=act
            ).first()
        if not start:
            start = ""
            casting = ""
        else:
            casting = ActResource.objects.filter(
                allocations__event__eventitem=start,
                _item=act).first().role
        q = Show.objects.filter(
            e_conference=act.b_conference,
            scheduler_events__isnull=False).order_by(
                'scheduler_events__starttime')
        self.actionform.fields['show'] = ModelChoiceField(
            queryset=q,
            empty_label=None,
            label='Pick a Show',
            initial=start)
        self.actionform.fields['casting'] = ChoiceField(
            choices=get_act_casting(),
            required=False,
            label=act_casting_label,
            initial=casting)
        self.actionURL = reverse(self.changestate_view_name,
                                 urlconf='gbe.urls',
                                 args=[act.id])
