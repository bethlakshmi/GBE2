from gbe.forms import (
    ActEditForm,
)
from gbe.models import (
    Act,
)
from gbe.views import ViewBidView
from gbe.views.functions import get_performer_form
from gbe.views.act_display_functions import get_act_form


class ViewActView(ViewBidView):

    bid_type = Act
    viewer_permissions = ('Act Reviewers',)
    object_form_type = ActEditForm
    bid_prefix = "The Act"

    def get_owner_profile(self):
        return self.bid.performer.contact

    def get_display_forms(self):
        actform = get_act_form(self.bid)

        performer_form = get_performer_form(self.bid.performer)
        return (actform, performer_form)
