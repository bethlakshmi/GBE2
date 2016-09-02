from gbe.forms import (
    PersonaForm,
    ClassBidForm,
    ParticipantForm,
)
from gbe.models import Class
from gbe.views import ReviewBidView


class ReviewClassView(ReviewBidView):
    reviewer_permissions = ('Class Reviewers',)
    coordinator_permissions = ('Class Coordinator',)
    bid_prefix = "The Class"
    bidder_prefix = "The Teacher(s)"
    bidder_form_type = PersonaForm
    bid_form_type = ClassBidForm
    object_type = Class
    bid_view_name = 'class_view'
    review_list_view_name = 'class_review_list'
    changestate_view_name = 'class_changestate'

    def groundwork(self, request, args, kwargs):
        super(ReviewClassView, self).groundwork(request, args, kwargs)
        self.create_object_form()
        self.teacher = self.bidder_form_type(instance=self.object.teacher,
                                             prefix=self.bidder_prefix)
        initial = {
            'email': self.object.teacher.performer_profile.user_object.email,
            'first_name':
            self.object.teacher.performer_profile.user_object.first_name,
            'last_name':
            self.object.teacher.performer_profile.user_object.last_name}
        self.contact = ParticipantForm(
            instance=self.object.teacher.performer_profile,
            prefix='Teacher Contact Info', initial=initial)
        self.readonlyform_pieces = (self.object_form,
                                    self.teacher, self.contact)
