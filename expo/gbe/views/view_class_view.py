from gbe.models import Class
from gbe.forms import (
    ClassBidForm,
    PersonaForm,
)
from gbe.views import ViewBidView


class ViewClassView(ViewBidView):
    bid_type = Class
    object_form_type = ClassBidForm
    viewer_permissions = ('Class Reviewers',)
    bid_prefix = 'The Class'
    owner_prefix = 'The Teacher(s)'

    def get_display_forms(self):
        bid_form = self.object_form_type(instance=self.bid,
                                         prefix=self.bid_prefix)
        self.performer = self.bid.teacher
        return (bid_form, )

    def get_owner_profile(self):
        return self.bid.teacher.contact
