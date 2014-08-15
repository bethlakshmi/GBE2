# literal text from gbe forms
# see gbetext.py for the rules
# until I copy them over

participant_labels = {
    'display_name': ('Badge Name'),
    'address1': ('Street Address'),
    'address2': ('Street Address (cont.)'),
    'best_time':('Best time to call'),
    'offsite_preferred':('Offsite phone'),
    'how_heard': "How did you hear about The Expo?"

}

profile_preferences_help_texts= {
    'in_hotel':  'It is helpful for us to know who\'s staying in the hotel.'
}

profile_preferences_labels = {
    'inform_about': 'Please let me know about...',
    'in_hotel': 'I am staying at the hotel'
    
}



inform_about_options = [('Pre-event Organizing', 'Pre-event Organizing'), 
                        ('Volunteering', 'Volunteering at the Expo'), 
                        ('Performing', 'Performing'), 
                        ('Vending', 'Vending'), 
                        ('Sponsoring/Advertising',  'Sponsoring/Advertising'), 
                        ('Teaching', 'Teaching'), 
                        ('Exhibiting Art or Costumes', 'Exhibiting Art or Costumes')]



how_heard_options = [('Previous attendee', 'Attended Previously'), 
                     ('Facebook', 'Facebook'), 
                     ('Yahoo! Group', 'Yahoo! Group'), 
                     ('Received a direct email', 'Received a direct email'), 
                     ('Word of mouth', 'Word of mouth'), 
                     ('Saw a postcard', 'Saw a postcard'), 
                     ('Saw a print ad', 'Saw a print ad'), 
                     ('B.A.B.E.', 'B.A.B.E.'), 
                     ('Other', 'Other')]

participant_form_help_texts = {
    'display_name': ('The name you want to be known by as an Expo participant. This can \
be a stage name, or your real-world name, or anything that you want to have printed on your \
Expo badge and other official Expo communications. This defaults to your First and Last Name.'),
    'phone': ('A phone number we can use to reach you when you are at the Expo, \
such as cell phone.'),
    'offsite_preferred': ('Your preferred phone number (if different from above), \
for communication before the Expo.  Use this if you prefer to get phone calls at a \
phone you cannot bring to the Expo.'),
}


phone_validation_error_text = '''If Preferred contact is a Phone call or Text, \
we need your phone number as either an Onsite phone or Offsite preferred.'''


combo_form_help_texts = {
    'contact': ('The person we should contact about this act\'s appearance at the Expo. This \
    can be a member of your combo or an agent, but whoever it is will be authorized to speak \
    for and make decisions for you.'), 
    'name': ('If you leave this blank, it\'ll fill in with the names of the performers involved in \
             this act.'),
    'membership': ('Select the performers who will be on stage with you. If they have not created \
    a persona on the site, you can either create one for them, or just fill in their name in the \
    notes and we\'ll sort it out.'), # edit this text please
}


combo_header_text = '''A combo is a one-off group of performers working together. If \
you want to put together an act with someone you don't usually work with, a combo \
is probably what you're doing. If you have a group that performs together regularly, \
it's probably a <a href='/troupe/create'>troupe</a>. '''


troupe_header_text = '''A troupe is an established group of performers who work \
together regularly under a collective name. If you are performing with a group of \
performers that has a website, mailing list, or engagements as that group, then \
you are probably a troupe. If you want to put something special together just for \
the Expo, it's probably a <a href='/combo/create/'>combo</a>.'''



volunteer_availability_options = [('SH0', 'Thursday evening'), ('SH1', 'Friday morning'), 
                                  ('SH2', 'Friday afternoon'), ('SH3', 'Friday night'), 
                                  ('SH4', 'Friday late night'), ('SH5', 'Saturday morning'), 
                                  ('SH6', 'Saturday afternoon'), ('SH7', 'Saturday night'), 
                                  ('SH8', 'Saturday late night'), ('SH9', 'Sunday morning'), 
                                  ('SH10', 'Sunday afternoon'), ('SH11', 'Sunday night'), 
                                  ('SH12', 'Strike Crew'), ('SH13', 'Monday morning')]

volunteer_interests_options = [('VA0', 'Registration'), ('VA1', 'Security/usher'), 
                          ('VA2', 'Stage crew'), ('VA3', 'Stage Management'), 
                          ('VA4', 'Conference Staff'), ('VA5', 'Tech crew'), 
                          ('VA6', 'Vendor room'), ('VA7', 'Costume Exhibit'), ('VA8', 'Art Show')]

volunteer_labels = {
    'number_shifts': 'How many shifts would you like to work?',
    'interests':'What are your particular areas of interest?',
    'availability': 'I am Available....',
    'unavailability': 'I am Not Available....',
    'opt_outs': 'Are there events that we should make sure to not schedule you during?',
    'pre_event': 'Are you interested in helping with pre-event tasks?',
    'background': 'Tell us about your background, including relevant skills and experience'

}

volunteer_help_texts = {
    'pre_event': ('Pre-event tasks could be anything from marketing \
    to logistics to advertising sales to data entry. In short, \
    anything we need done before the BurlExpo starts') }

phone_error1 = ['Phone number needed here']
phone_error2 = ['... or here ']
phone_error3 = ['...or choose a contact method that does not require a phone.']

audioinfo_labels = {
    'title' : ('Track Title'),
    'artist' : ('Track Artist')}

bidder_info_phone_error = ''''A phone number we can use to reach you when you are at \
the Expo, such as cell phone.'''

act_length_required = ("Act Length (mm:ss) is required.")
act_length_too_long = ("The Act Length is too long.")  # note: this refers to the data 
                                                       # entered, not the time signified

act_help_texts = {
    'shows_preferences':'Check as many as apply to you',
    'act_duration':'Length of entire act in mm:ss - please include any time \
    you are performing before or after your song.', 
    'track_duration':'Please enter the duration of your music or backing track in \
    minutes and seconds. Something that was four minutes and twenty seconds would be \
    entered as "04:20". Remember, the maximum duration for an act in competition in \
    The Main Event is 5 minutes for a soloist, 7 minutes for a group',
    'description':'Please give a brief description of your act. \
    Stage kittens will retrieve costumes and props, but we cannot clean the stage \
    after your act. Please do not leave anything on the stage (water, glitter, \
    confetti, etc.)', 
    'performer': 'Select the stage persona, combo, or troupe who will be \
    performing. Hit "create" to create a new persona, troupe, or combo.',
    'video_link' : 'Link to some video of your performance, or a similar act. This \
    will be used for evaluating your bid, and will not appear on your performer page.',
    'shows_preferences':'Check as many as apply to you',
    'video_link':'Make sure to include \'http://\' '

}

act_bid_labels = {
    'performer' :'Performer',
    'title': 'Name of Act',
    'shows_preferences':'I am interested in:',
    'song_title':'Name of Song',
    'song_artist':'Song Artist',
    'track_duration':'Duration of Song',
    'act_duration':'Duration of Act',
    'description':'Description of Act',
    'video_choice':'Video Notes',
    'why_you':'Why Would You Like to Perform at The Great Burlesque Exposition?',
    'video_link':'URL of Video'
}



bio_required = ("Performer/Troupe history is required.")
bio_too_long = ("The History is too long.")
bio_help_text = 'Please give a brief performer/troupe history.'

act_description_required =  ("Description of the Act is required.")
act_description_too_long =  ("The Description  is too long.")

promo_required = ("Please provide a photo.")
promo_help_text = '''Please_upload a photograph of yourself (photo must be under 10 MB).'''

persona_labels = { 'name'       : ('Stage Name'), 
                   'homepage'   : ('Web Site'),
                   'contact'    : ('Agent/Contact'), 
                   'bio'        : ('Bio'),
                   'experience' : ('Experience'),  
                   'awards'     : ('Awards'),
                   'promo_image': ('Promo Image'),
                   'puffsheet'  : ('Press kit/one-sheet'),
                   'festivals'  : ('Festival Appearances and Honors'),
               }


persona_help_texts = {  
'name' : 
    ('This is the name you will be listed under when performing.'),
'contact' : 
    ('''The person GBE should contact about Expo \
    performances. Usually, this will be you.'''),
'homepage' : 
    ('This will be listed on your performer page.'),
'bio' : 
    ('This will be listed on your performer page.'),
'promo_image' : 
    ('''This may be used by GBE for promotional purposes, and \
    will appear on your performer page.'''),
'puffsheet' : 
    ('''If you have a one-sheet or other prepared presskit, \
    you may upload it, and we'll include it in your promo page. '''),
'experience' : 
    ('''Number of years performing burlesque'''),
'awards' : 
    ('''Other awards and recognition of your work in burlesque, \
    including festival appearances not listed above.'''),
'festivals' : 
    ('''If you have appeared in any of these festivals, let \
    us know how you did. This information will appear on your performer page.'''),
}

bid_review_options = ( 'Accepted', 'Declined', 'Waitlist')

actbid_error_messages = {
    'title': {
        'required': ("The Title is required."),
        'max_length': ("The title of the act is too long."),
    }}

actbid_name_missing = ['...a name is needed']
actbid_otherperformers_missing = ['...please describe the other performers.']
actbid_group_wrong = ['If this is a group... other entries are needed.']
actbid_group_error = '''The submission says this is a group act, but there are \
no other performers listed'''

video_error1 = ['Either say that no video is provided.']
video_error2 = ['... or provide video']
video_error3 = '''The Video Description suggests a Video Link would be provided, \
but none was provided.'''

description_required = ("Description is required.")
description_too_long = ("The Description is too long.")
description_help_text = '''For use on the The Great Burlesque Expo website, in \
advertising and in any schedule of events. The description should be 1-2 paragraphs.'''

classbid_labels = {
	'min_size': ('Minimum Size'),
	'maximum_enrollment': ('Maximum Students'),
	'history': ('Have You Taught This Class Before?'),
	'other_teachers': ('Fellow Teachers'),
	'run_before': 'Has the Class been run Before?',
	'fee': 'Materials Fee',
	'space_needs': 'Room Preferences',
	'schedule_constraints': 'Preferred Teaching Times',
	'multiple_run': 'Are you willing to run the class more than once?',
	'length_minutes': ('Length in Minutes'),
}

classbid_help_texts = {
	'min_size': ('''The minimum number of people required for your class. This guideline \
	helps the convention meet both teacher expectations and class size needs. If \
	you\'re not sure, make the minimum 1'''),
	'max_size': ('The maximum number of people that the class can accomodate.'),
	'history': ('Have you taught this class before? Where and when?'),
	'run_before': ('If the class has been run before, please let us know where and when.'),
	'fee': ('We strongly suggest that your materials fee not exceed $10'), 
	'space_needs': ('Room Preferences'),
	'physical_restrictions': ('Physical Restrictions'),
	'schedule_constraints': ('Scheduling Constraints'),
	'multiple_run': ('Are you willing to run the class more than once?'),
	'length_minutes': ('''Please note that classes are \
        asked to end 10 minutes shorter than the full slot length, \
        so a 60 minute class is really 50 minutes.'''),
}
classbid_error_messages = {
    'length_minutes': {
        'required': ("Class Length (in minutes) is required."),
        'max_length': ("The Class Length is too long."),
    }}

class_schedule_options = [('0', 'Friday Afternoon'), 
                           ('1', 'Saturday Morning'), 
                           ('2', 'Saturday Afternoon'), 
                           ('3', 'Sunday Morning'), 
                           ('4', 'Sunday Afternoon')] 




space_error1 = ('''A class of workshop type cannot have space choices.''')
space_type_error1 = ('''A workshop has seating in a ring around the room, other options are not \
available.''')
space_error2 = ('''A class of movement type cannot have lecture space choices.''')
space_type_error2 = ('''A movement class may have room preferences listed for movement \
classes, but the chosen lecture style arrangement is not an option.''')
space_error3 = ('''A class of lecture type cannot have movement space choices.''')
space_type_error3 = ('''A lecture class may have room preferences listed for lecture \
classes, but the chosen movement style arrangement is not an option.''')

panel_labels = {
	'other_teachers': ('Recommended Panelists'),
	'run_before': 'Has the Panel been run Before?',
}

panel_help_texts = {
	'other_teachers': ('''It is far more likely that your panel may be run at The \
	Great Burlesque Expo 2014if we can find qualified panelists and a moderator - \
	let us know any recommendations.'''),
	'run_before': ('''The Great Burlesque Expo 2014 is looking for convention \
	content that is new and that have successfully presented before, either at \
	a convention, or elsewhere. If this content has run before, please describe \
	where and when.'''),
}

vendor_description_help_text = '''Please describe your good or services in 250 words \
or less. We will publish this text on the website.'''

vendor_labels = {
    'description': 'Description of Goods or Services',
    'title':'Company or business name',
    'vend_time':  ('I\'d like to vend...'),
    'want_help': ('Help Wanted'),
    'help_times': ('I\'d like someone to help me... (Check All That Apply)'),
    'help_description': ('Tell Us About the Person You\'d Like to Hire '),
    'website':'Company website',
    'physical_address':'Business Address',
    'publish_physical_address':'Publish my business address'

}
vendor_help_texts = {
    'vend_time':  ('I\'d like to vend...'),
    'want_help': ('''Would you like us to help you find someone to work at your \
    booth or table with you?'''),
    'logo': ('''Please provide any logo you would like displayed on our website \
    and advertising'''),
    'description':('''The information you enter here will be displayed on the website \
    exactly as you enter it, so please double-check it before hitting submit'''),
    'physical_address':('''If your business address is different from the address \
    you used when you registered for the website, please enter your business address here.'''),

    'help_description':('''The Great Burlesque Exposition can help you find people \
    to work for you. Please use this field to describe what sort of work you want done \
    (booth staff, models, hand out flyers, set-up or teardown staff) and any \
    requirements (for example, "must be able to lift 40 pounds", "must be knowledgeable \
    about corsets", "must be able to drive a standard").'''),
}

vendor_schedule_options = [('VSH0', 'Saturday, 9am to noon'), 
                           ('VSH1', 'Saturday, 12p to 4pm'), 
                           ('VSH2', 'Saturday, 4pm to 8pm'), 
                           ('VSH3', 'Saturday after 8pm'), 
                           ('VSH4', 'Sunday, 9am to noon'), 
                           ('VSH5', 'Sunday, 12p to 4pm'), 
                           ('VSH6', 'Sunday, 4pm to 8pm'), 
                           ('VSH7', 'Sunday after 8pm')]


help_time_choices = (('Saturday, 9am to noon', 'Saturday, 9am to noon'),
					('Saturday, 12p to 4pm','Saturday, 12p to 4pm'),
					('Saturday, 4pm to 8pm', 'Saturday, 4pm to 8pm'),
					('Saturday after 8pm', 'Saturday after 8pm'),
					('Sunday, 9am to noon', 'Sunday, 9am to noon'),
					('Sunday, 12p to 4pm', 'Sunday, 12p to 4pm'),
					('Sunday, 4pm to 8pm', 'Sunday, 4pm to 8pm'),
					('Sunday after 8pm', 'Sunday after 8pm'))




# Would like to be able to insert this into the class proposal form from upstream

class_proposal_form_text = {
    'header': '''Thanks for your interest in the Great Burlesque Expo. Suggestions \
    are welcome for classes you\'d like to see offered. 
    Name and email address are optional: fill in if you\'d like updates about \
    classes and panels at the next Expo. '''
}

class_proposal_help_texts = {
    'name' : 'If you\'d like to get updates about classes and panels at the Expo, \
    fill in your name and email address. Or don\'t, if you prefer, it\'s up to you.',
    'title': 'Your suggested title for this class or panel',
    'proposal': 'What does this class look like in your mind? Consider telling us about material to \
    cover, target audience, etc',
    'type': 'Is this a class? A panel? Do you care?'
}

ticket_item_labels = {
    'ticket_id': 'Ticket Item Id:',
    'title':'Title:',
    'active': 'Display Item to Users?:',
    'cost': 'Ticket Price:',

}

username_label = 'Login'
username_help = 'Required. 30 characters or fewer. Letters, digits and @ . + - _ only.'
