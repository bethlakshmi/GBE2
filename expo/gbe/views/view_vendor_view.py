from gbe.models import Vendor
from gbe.forms import VendorBidForm
from gbe.views import ViewBidView


class ViewVendorView(ViewBidView):
    bid_type = Vendor
    viewer_permissions = ('Vendor Reviewers',)
    object_form_type = VendorBidForm
    bid_prefix = "The Business"
    owner_prefix = "The Contact Info"

    def get_display_forms(self):
        pass

    def make_context(self):
        display_forms = self.get_display_forms()
        context = {'vendor': self.bid, }
        return context
