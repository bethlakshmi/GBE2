from django.core.urlresolvers import reverse
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)
from gbe.forms import (
    ClassBidForm,
    PersonaForm
)


def get_scheduling_info(bid_class):
    if bid_class.__class__.__name__ != 'Class':
        return None

    schedule_opt = dict(class_schedule_options)
    scheduling_info = {
        'display_info': [
            (classbid_labels['schedule_constraints'],
             ', '.join(
                [j for i, j in class_schedule_options
                 if i in bid_class.schedule_constraints])),
            (classbid_labels['avoided_constraints'],
             ', '.join(
                [j for i, j in class_schedule_options
                 if i in bid_class.avoided_constraints])),
            ('Format', bid_class.type),
            ('Space Needs', bid_class.get_space_needs_display()),
            ],
        'reference': reverse('class_view',
                             urlconf='gbe.urls',
                             args=[bid_class.id]),
        }

    return scheduling_info

def get_class_forms(bid_class):
    bid_form = ClassBidForm(instance=bid_class,
                                     prefix='The Class')
    persona_form = PersonaForm(instance=bid_class.teacher,
                               prefix='The Teacher(s)')
    return (bid_form, persona_form)

