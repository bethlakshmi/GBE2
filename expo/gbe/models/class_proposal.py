from django.db.models import (
    Model,
    CharField,
    EmailField,
    TextField,
    BooleanField,
    ForeignKey,
)

from gbetext import class_proposal_choices
from remains import Conference

class ClassProposal(Model):
    '''
    A proposal for a class that someone else ought to teach.
    This is NOT a class bid, this is just a request that someone
    implement this idea.
    '''
    title = CharField(max_length=128)
    name = CharField(max_length=128, blank=True)
    email = EmailField(blank=True)
    proposal = TextField()
    type = CharField(max_length=20,
                            choices=class_proposal_choices,
                            default='Class')
    display = BooleanField(default=False)
    conference = ForeignKey(
        Conference,
        default=lambda: Conference.objects.filter(status="upcoming").first())

    def __unicode__(self):
        return self.title

    @property
    def bid_review_header(self):
        return (['Title',
                 'Proposal',
                 'Type',
                 'Submitter',
                 'Published',
                 'Action'])

    @property
    def bid_review_summary(self):
        if self.display:
            published = "Yes"
        else:
            published = ""
        return (self.title, self.proposal, self.type, self.name, published)

    @property
    def presenter_bid_header(self):
        return (['Title', 'Proposal'])

    @property
    def presenter_bid_info(self):
        return (self.title, self.proposal, self.type)

    class Meta:
        app_label = "gbe"
