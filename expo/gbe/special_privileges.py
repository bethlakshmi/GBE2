
from django.core.urlresolvers import reverse



special_privileges= {'Act Reviewers':
                     {'url':reverse('act_review_list', urlconf='gbe.urls'),
                      'title':'Review Acts'},
                    'Act Coordinator':
                        {'url': '','title':''},
                    'Class Reviewers':
                        {'url':reverse('class_review_list', urlconf='gbe.urls'),
                         'title':'Review Classes'},
                    'Class Coordinator':
                        {'url':reverse('proposal_review_list', urlconf='gbe.urls'),
                         'title':'Review Proposals'},
                    'Volunteer Reviewers':
                        {'url':reverse('volunteer_review_list',urlconf='gbe.urls'),
                         'title':'Review Volunteers'},
                    'Volunteer Coordinator':
                        {'url': '',
                         'title': ''},
                    'Vendor Reviewers':
                        {'url':reverse('vendor_review_list',urlconf='gbe.urls'),
                         'title':'Review Vendors'}, 
                    'Vendor Coordinator':
                        {'url': '',
                         'title':''},
                    'Scheduling Mavens': 
                        {'url': reverse('event_schedule',urlconf='scheduler.urls'),
                         'title':'Schedule Events'},
                    'Ticketing - Admin':
                        {'url':reverse('ticket_items',urlconf='ticketing.urls'),
                         'title':'Ticket Items'},
                    'Ticketing - Edit Item':
                        {'url':reverse('ticket_item_edit',urlconf='ticketing.urls'),
                         'title':'Ticket Item Edit'},
                    'Ticketing - Transactions':
                        {'url':reverse('transactions', urlconf='ticketing.urls'),
                         'title':'Ticketing Transactions'},
                    'Registrar':
                        {'url':reverse('manage_users', urlconf='gbe.urls'),
                         'title':'User Administration'},
                    }

