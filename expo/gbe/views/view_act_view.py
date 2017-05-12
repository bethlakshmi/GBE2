from django.core.urlresolvers import reverse
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

    def check_bid(self):
        if self.bid and self.bid.is_summer and (
                self.__class__.__name__ != "ViewSummerActView"):
            return reverse(
                'summer_act_view',
                urlconf='gbe.urls',
                args=[self.bid.pk])
        elif self.bid and not self.bid.is_summer and (
                self.__class__.__name__ == "ViewSummerActView"):
            return reverse(
                'act_view',
                urlconf='gbe.urls',
                args=[self.bid.pk])
        return None

    def get_owner_profile(self):
        return self.bid.performer.contact

    def get_display_forms(self):
        actform = get_act_form(
            self.bid,
            self.object_form_type,
            self.bid_prefix)
        performer_form = get_performer_form(self.bid.performer)
        return (actform, performer_form)
