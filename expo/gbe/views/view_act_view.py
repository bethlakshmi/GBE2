from gbe.forms import (
    ActEditForm,
)
from gbe.models import (
    Act,
)
from gbe.views import ViewBidView
from gbe.views.functions import get_performer_form

class ViewActView(ViewBidView):

    bid_type = Act
    viewer_permissions = ('Act Reviewers',)
    object_form_type = ActEditForm
    bid_prefix = "The Act"

    def get_owner_profile(self):
        return self.bid.performer.contact

    def get_display_forms(self):
        audio_info = self.bid.tech.audio
        stage_info = self.bid.tech.stage
        actform = self.object_form_type(
            instance=self.bid,
            prefix=self.bid_prefix,
            initial={'track_title': audio_info.track_title,
                     'track_artist': audio_info.track_artist,
                     'track_duration': audio_info.track_duration,
                     'act_duration': stage_info.act_duration}
        )

        performer_form = get_performer_form(self.bid.performer)
        return (actform, performer_form)
