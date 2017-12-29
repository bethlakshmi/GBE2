from django.db.models import (
    Model,
    ForeignKey,
    TextField,
)
from gbe.models import (
    Biddable,
    Profile,
)

from gbetext import grade_options


class BidReviewComment(Model):
    comment = TextField(blank=True, max_length=500)
    profile = ForeignKey(Profile)
    bid = ForeignKey(Biddable)

    class Meta:
        app_label = "gbe"
        unique_together = (('profile', 'bid'),)
