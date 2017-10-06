from django.core.urlresolvers import reverse

special_menu_tree = [
    {'title': 'Contact',
     'url': '',
     'parent_id': 1,
     'id': 2,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'By Email',
     'url': reverse('mail_to_bidders',
                    urlconf='gbe.email.urls'),
     'parent_id': 2,
     'id': 46,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'Performers',
     'url': reverse('contact_by_role',
                    urlconf='scheduler.urls',
                    args=['Performers']),
     'parent_id': 2,
     'id': 3,
     'groups': ['Act Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Teachers',
     'url': reverse('contact_by_role',
                    urlconf='scheduler.urls',
                    args=['Teachers']),
     'parent_id': 2,
     'id': 4,
     'groups': ['Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Vendors',
     'url': reverse('contact_by_role',
                    urlconf='scheduler.urls',
                    args=['Vendors']),
     'parent_id': 2,
     'id': 5,
     'groups': ['Vendor Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Volunteers',
     'url': reverse('contact_by_role',
                    urlconf='scheduler.urls',
                    args=['Volunteers']),
     'parent_id': 2,
     'id': 6,
     'groups': ['Volunteer Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Manage',
     'url': '',
     'parent_id': 1,
     'id': 10,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Registrar',
                'Ticketing - Admin',
                'Ticketing - Transactions',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'Email Templates',
     'url': reverse('list_template', urlconf='gbe.email.urls'),
     'parent_id': 10,
     'id': 45,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                ]},
    {'title': 'Tickets',
     'url': reverse('ticket_items', urlconf='ticketing.urls'),
     'parent_id': 10,
     'id': 11,
     'groups': ['Ticketing - Admin',
                ]},
    {'title': 'Ticket Transactions',
     'url': reverse('transactions', urlconf='ticketing.urls'),
     'parent_id': 10,
     'id': 12,
     'groups': ['Ticketing - Transactions',
                ]},
    {'title': 'Users',
     'url': reverse('manage_users', urlconf='gbe.urls'),
     'parent_id': 10,
     'id': 13,
     'groups': ['Registrar',
                ]},
    {'title': 'Report',
     'url': reverse('reporting:report_list'),
     'parent_id': 1,
     'id': 20,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Costume Coordinator',
                'Vendor Coordinator',
                'Volunteer Coordinator',
                'Tech Crew',
                'Scheduling Mavens',
                'Ticketing - Admin',
                'Registrar',
                ]},
    {'title': 'Review',
     'url': '',
     'parent_id': 1,
     'id': 30,
     'groups': ['Act Reviewers',
                'Act Coordinator',
                'Class Reviewers',
                'Class Coordinator',
                'Costume Reviewers',
                'Costume Coordinator',
                'Vendor Reviewers',
                'Vendor Coordinator',
                'Volunteer Reviewers',
                'Volunteer Coordinator',
                'Tech Crew']},
    {'title': 'Acts',
     'url': reverse('act_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 31,
     'groups': ['Act Reviewers',
                'Act Coordinator']},
    {'title': 'Act Tech Info',
     'url': reverse('act_techinfo_review', urlconf='gbe.reporting.urls'),
     'parent_id': 30,
     'id': 32,
     'groups': ['Tech Crew']},
    {'title': 'Classes',
     'url': reverse('class_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 33,
     'groups': ['Class Reviewers',
                'Class Coordinator']},
    {'title': 'Costumes',
     'url': reverse('costume_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 34,
     'groups': ['Costume Reviewers',
                'Costume Coordinator']},
    {'title': 'Proposals',
     'url': reverse('proposal_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 35,
     'groups': ['Class Coordinator']},
    {'title': 'Vendors',
     'url': reverse('vendor_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 36,
     'groups': ['Vendor Reviewers',
                'Vendor Coordinator']},
    {'title': 'Volunteers',
     'url': reverse('volunteer_review_list', urlconf='gbe.urls'),
     'parent_id': 30,
     'id': 37,
     'groups': ['Volunteer Reviewers',
                'Volunteer Coordinator']},
    {'title': 'Schedule',
     'url': '',
     'parent_id': 1,
     'id': 40,
     'groups': ['Act Coordinator',
                'Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Acts',
     'url': reverse('schedule_acts', urlconf='scheduler.urls'),
     'parent_id': 40,
     'id': 41,
     'groups': ['Act Coordinator',
                'Scheduling Mavens']},
    {'title': 'Classes',
     'url': reverse('event_schedule',
                    urlconf='scheduler.urls',
                    args=['Class']),
     'parent_id': 40,
     'id': 42,
     'groups': ['Class Coordinator',
                'Scheduling Mavens',
                ]},
    {'title': 'Export',
     'url': reverse('export_calendar',
                    urlconf='scheduler.urls'),
     'parent_id': 40,
     'id': 43,
     'groups': ['Class Coordinator',
                'Scheduling Mavens']},
    {'title': 'General Events',
     'url': reverse('event_schedule',
                    urlconf='scheduler.urls',
                    args=['GenericEvent']),
     'parent_id': 40,
     'id': 43,
     'groups': ['Scheduling Mavens']},
    {'title': 'Shows',
     'url': reverse('event_schedule',
                    urlconf='scheduler.urls',
                    args=['Show']),
     'parent_id': 40,
     'id': 44,
     'groups': ['Scheduling Mavens']},
]
