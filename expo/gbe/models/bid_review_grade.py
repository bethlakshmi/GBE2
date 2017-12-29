from django.db.models import (
    Model,
    ForeignKey,
    CharField,
)
from gbe.models import (
    Biddable,
    BidReviewQuestion,
    Profile,
)

from gbetext import grade_options


class BidReviewGrade(Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    question = ForeignKey(BidReviewQuestion)
    rating = CharField(choices=grade_options,
                       blank=True,
                       max_length=10)
    profile = ForeignKey(Profile)
    bid = ForeignKey(Biddable)

    class Meta:
        app_label = "gbe"
        unique_together = (('question', 'profile', 'bid'),)
