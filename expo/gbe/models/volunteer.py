from django.db.models import (
    TextField,
    ForeignKey,
    IntegerField,
    BooleanField,
    ManyToManyField,
)
from gbetext import (
    acceptance_states,
    boolean_options,
    volunteer_shift_options,
)
from profile import Profile
from remains import (
    Biddable,
    VolunteerWindow,
    visible_bid_query,
)

class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer.
    '''
    profile = ForeignKey(Profile, related_name="volunteering")
    number_shifts = IntegerField(choices=volunteer_shift_options,
                                        default=1)
    availability = TextField(blank=True)
    unavailability = TextField(blank=True)
    opt_outs = TextField(blank=True)
    pre_event = BooleanField(choices=boolean_options, default=False)
    background = TextField(blank=True)
    available_windows = ManyToManyField(
        VolunteerWindow,
        related_name="availablewindow_set",
        blank=True)
    unavailable_windows = ManyToManyField(
        VolunteerWindow,
        related_name="unavailablewindow_set",
        blank=True)

    def __unicode__(self):
        return self.profile.display_name

    @property
    def interest_list(self):
        return [
            interest.interest.interest
            for interest in self.volunteerinterest_set.filter(rank__gt=3)]

    @property
    def bid_review_header(self):
        return (['Name',
                 'Email',
                 'Hotel',
                 '# of Hours',
                 'Scheduling Info',
                 'Interests',
                 'Pre-event',
                 'Background',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        interest_string = ''
        for interest in self.interest_list:
            interest_string += interest + ', \n'
        availability_string = ''
        unavailability_string = ''
        for window in self.available_windows.all():
            availability_string += unicode(window) + ', \n'
        for window in self.unavailable_windows.all():
            unavailability_string += unicode(window) + ', \n'

        commitments = ''

        for event in self.profile.get_schedule(self.conference):
            start_time = event.start_time.strftime("%a, %b %d, %-I:%M %p")
            end_time = event.end_time.strftime("%-I:%M %p")

            commitment_string = "%s - %s to %s, \n " % (
                str(event),
                start_time,
                end_time)
            commitments += commitment_string
        format_string = "Availability: %s\n Conflicts: %s\n Commitments: %s"
        scheduling = format_string % (availability_string,
                                      unavailability_string,
                                      commitments)
        return (self.profile.display_name,
                self.profile.user_object.email,
                self.profile.preferences.in_hotel,
                self.number_shifts,
                scheduling,
                interest_string,
                self.pre_event,
                self.background,
                acceptance_states[self.accepted][1])

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    class Meta:
        app_label = "gbe"
