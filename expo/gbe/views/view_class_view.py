from gbe.models import Class
from gbe.forms import (
    ClassBidForm,
    PersonaForm,
)
from gbe.views import ViewBidView
from gbe.views.class_display_functions import get_class_forms


class ViewClassView(ViewBidView):
    bid_type = Class
    viewer_permissions = ('Class Reviewers',)

    def get_display_forms(self):
        return get_class_forms(self.bid)

    def get_owner_profile(self):
        return self.bid.teacher.contact
