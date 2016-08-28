from gbe.forms import (
    ActEditForm,
    PersonaForm,
    TroupeForm,
)
from gbe.models import (
    Act,
    Troupe,
)
from gbe.views import ViewBidView


class ViewActView(ViewBidView):

    bid_type = Act
    viewer_permissions = ('Act Reviewers',)
    object_form_type = ActEditForm
    bid_prefix = "The Act"
    performer_prefix = "The Performer(s)"
    troupe_prefix = "The Troupe"

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

        if Troupe.objects.filter(pk=self.bid.performer.pk).exists():
            instance = Troupe.objects.get(pk=self.bid.performer.pk)
            performer_form = TroupeForm(instance=instance,
                                        prefix=self.troupe_prefix)
        else:
            performer_form = PersonaForm(instance=self.bid.performer,
                                         prefix=self.performer_prefix)
        return (actform, performer_form)
