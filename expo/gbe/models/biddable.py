from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
)
from gbe.models import Conference
from gbetext import acceptance_states
from django.db.models import Q


visible_bid_query = (Q(biddable_ptr__conference__status='upcoming') |
                     Q(biddable_ptr__conference__status='ongoing'))


class Biddable(Model):
    '''
    Abstract base class for items which can be Bid
    Essentially, specifies that we want something with a title
    '''
    title = CharField(max_length=128)
    description = TextField(blank=True)
    submitted = BooleanField(default=False)
    accepted = IntegerField(choices=acceptance_states,
                            default=0,
                            blank=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    conference = ForeignKey(
        Conference,
        default=lambda: Conference.objects.filter(status="upcoming").first())

    class Meta:
        verbose_name = "biddable item"
        verbose_name_plural = "biddable items"
        app_label = "gbe"

    def __unicode__(self):
        return self.title

    def typeof(self):
        return self.__class__

    @property
    def ready_for_review(self):
        return (self.submitted and
                self.accepted == 0)

    @property
    def is_current(self):
        return self.conference.status in ("upcoming", "current")
