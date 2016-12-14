import pytz
from django.db.models import (
    BooleanField,
    FileField,
    ForeignKey,
    TextField,
    URLField,
)
from gbe.models import (
    Biddable,
    Profile,
    visible_bid_query
)
from gbetext import (
    acceptance_states,
    boolean_options,
)


class Vendor(Biddable):
    '''
    A request for space in the Expo marketplace.
    Note that company name is stored in the title field inherited
    from Biddable, and description is also inherited
    '''
    profile = ForeignKey(Profile)
    website = URLField(blank=True)
    physical_address = TextField()  # require physical address
    publish_physical_address = BooleanField(default=False)
    logo = FileField(upload_to="uploads/images", blank=True)
    want_help = BooleanField(choices=boolean_options,
                             blank=True,
                             default=False)
    help_description = TextField(blank=True)
    help_times = TextField(blank=True)

    def __unicode__(self):
        return self.title  # "title" here is company name

    def clone(self):
        vendor = Vendor(profile=self.profile,
                        website=self.website,
                        physical_address=self.physical_address,
                        publish_physical_address=self.publish_physical_address,
                        logo=self.logo,
                        want_help=self.want_help,
                        help_description=self.help_description,
                        help_times=self.help_times,
                        title=self.title,
                        description=self.description,
                        conference=Conference.objects.filter(
                            status="upcoming").first())

        vendor.save()
        return vendor

    @property
    def bid_review_header(self):
        return (['Bidder',
                 'Business Name',
                 'Website',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        return (self.profile.display_name, self.title, self.website,
                self.updated_at.astimezone(pytz.timezone('America/New_York')),
                acceptance_states[self.accepted][1])

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    class Meta:
        app_label = "gbe"
