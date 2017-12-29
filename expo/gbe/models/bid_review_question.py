from django.db.models import (
    Model,
    BooleanField,
    CharField,
    IntegerField,
    TextField,
)


from gbetext import bid_types


class BidReviewQuestion(Model):
    question = CharField(blank=False, max_length=200)
    bid_type = CharField(choices=bid_types,
                         max_length=20)
    visible = BooleanField(default=True)
    help_text = TextField(blank=True, max_length=500)
    order = IntegerField()

    def __str__(self):
        return "%d - %s" % (self.order, self.question)

    class Meta:
        app_label = "gbe"
        unique_together = (
            ('question', 'bid_type'),
            ('order', 'bid_type'),)
