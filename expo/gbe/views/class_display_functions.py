from django.core.urlresolvers import reverse


def get_scheduling_info(bid_class):
    
    scheduling_info = {
        'display_info': [
            ('schedule_constraints', bid_class.schedule_constraints),
            ('avoided_constraints', bid_class.avoided_constraints),
            ('format', bid_class.type),
            ('space_needs', bid_class.space_needs),
            ],
        'reference': reverse('class_view',
                             urlconf='gbe.urls',
                             args=[item.id]),
        }
    
    return scheduling_info
