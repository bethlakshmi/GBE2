# literal text from gbe forms
# see gbetext.py for the rules
# until I copy them over

participant_labels = {
    'address1': ('Street Address'),
    'address2': ('Street Address (cont.)'),
}

participant_form_help_texts = {
    'display_name': ('The name you want to be known by as an expo participant. This can \
be a stage name, or your real-world name, or anything that you want to have printed on your \
expo badge and other official expo communications. This defaults to your First and Last Name.'),
    'onsite_phone': ('A phone number we can use to reach you when you are at the Expo, \
such as cell phone.'),
    'offsite_preferred': ('Your preferred phone number (if different from above), \
for communication before the Expo.  Use this if you prefer to get phone calls at a \
phone you cannot bring to the Expo.'),
}


phone_validation_error_text = '''If Preferred contact is a Phone call or Text, \
we need your phone number as either an Onsite phone or Offsite preferred.'''


phone_error1 = ['Phone number needed here']
phone_error2 = ['... or here ']
phone_error3 = ['...or choose a contact method that does not require a phone.']

bidder_info_phone_error = ''''A phone number we can use to reach you when you are at \
the Expo, such as cell phone.'''

act_length_required = ("Act Length (mm:ss) is required.")
act_length_too_long = ("The Act Length is too long.")  # note: this refers to the data 
                                                       # entered, not the time signified

act_length_help_text = 'Length of entire act in mm:ss - please include any time \
you are performing before or after your song.'

bio_required = ("Performer/Troupe history is required.")
bio_too_long = ("The History is too long.")
bio_help_text = 'Please give a brief performer/troupe history.'

act_description_required =  ("Description of the Act is required.")
act_description_too_long =  ("The Description  is too long.")
act_description_help_text = '''Please give a brief description of your act. \
Stage kittens will retrieve costumes and props, but we cannot clean the stage \
after your act. Please do not leave anything on the stage (water, glitter, \
confetti, etc.)'''

promo_required = ("Please provide a photo.")
promo_help_text = '''Please_upload a photograph of yourself (photo must be under 10 MB).'''

persona_labels = { 'name'       : ('Stage Name'), 
                   'homepage'   : ('Web Site'),
                   'contact'    : ('Agent/Contact'), 
                   'bio'        : ('Bio'),
                   'experience' : ('Experience'),  
                   'awards'     : ('Awards'),
                   'promo_image': ('Promo Image'),
                   'video_link' : ('Performance Video'),
                   'puffsheet'  : ('Press kit/one-sheet'),
                   'festivals'  : ('Festival Appearances and Honors'),
               }


persona_help_texts = {  
'name' : 
    ('This is the name you will be listed under when performing.'),
'contact' : 
    ('''The person GBE should contact about expo \
    performances. Usually, this will be you.'''),
'homepage' : 
    ('This will be listed on your performer page.'),
'bio' : 
    ('This will be listed on your performer page.'),
'video_link' : 
    ('''Link to some video of you performing. This will be used for
    evaluating your bid, and will not appear on your performer page.'''),
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

bid_review_options = { 'Accepted', 'Declined', 'Waitlist'}

actbid_labels = {
    'name': ('Stage Name or Troupe'),
    'homepage': ('Web Site'),
    'is_group': ('Is this a Troupe Performance?'),
    'other_performers': ('Fellow performers'),
    'song_name': 'Title of Song',
    'artist': 'Name of Artist',
    'video_choice': 'Video Description',
    'video_link': 'Link to Video',
    'hotel_choice': 'Are you staying in the hotel?',
    'volunteer_choice': 'Are you volunteering for the event?',
    'conference_choice': 'Are you attending the conference?',
}

actbid_help_texts = {
    'name': ('''If you are a soloist, this is your stage name.  If you are a troupe, \
This is your troupe name.  If you are a group, but not a troupe, please give the \
names you would like to be introduced by.'''),
    'other_performers': ('Please list other people involved/required for this act.'),
}

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
	'max_size': ('Maxiumum Size'),
	'history': ('Previous Experience'),
	'other_teachers': ('Fellow Teachers'),
	'run_before': 'Has the Class been run Before?',
	'fee': 'Materials Fee',
	'space_needs': 'Room Preferences',
	'physical_restrictions': 'Physical Restrictions',
	'schedule_constraints': 'Scheduling Constraints',
	'multiple_run': 'Are you willing to run the class more than once?',
	'length_minutes': ('Class Length'),
}

classbid_help_texts = {
	'min_size': ('''The minimum number of people required for your class. This guideline \
	helps the convention meet both teacher expectations and class size needs. If \
	you\'re not sure, make the minimum 1'''),
	'max_size': ('The maximum number of people that the class can accomodate.'),
	'history': ('Previous Experience'),
	'other_teachers': ('''This is a preliminary list. You\'ll be asked to confirm \
	fellow teachers if the class is confirmed. Additional teachers are eligible for \
	discounts, however a large number of teachers for a single event is likely to \
	diminish the discount level provided for the group.'''),
	'run_before': ('If the class has been run before, please let us know where and when.'),
	'fee': ('Materials Fee'),
	'space_needs': ('Room Preferences'),
	'physical_restrictions': ('Physical Restrictions'),
	'schedule_constraints': ('Scheduling Constraints'),
	'multiple_run': ('Are you willing to run the class more than once?'),
	'length_minutes': ('''Length class in minutes - please note that classes are \
asked to end 10 minutes shorter than the full slot length, so a 60 minute class is \
really 50 minutes.'''),
}
classbid_error_messages = {
    'length_minutes': {
        'required': ("Class Length (in minutes) is required."),
        'max_length': ("The Class Length is too long."),
    }}

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

offsite_vendor_help_text = '''A phone number for your business landline, if \
different from above.'''
vendor_description_help_text = '''Please describe your good or services in 250 words \
or less. We will publish this text on the website.'''
vendor_labels = {
	'vend_time':  ('I\'d like to vend...'),
	'want_help': ('Help Wanted'),
	'help_times': ('I\'d like someone to help me... (Check All That Apply)'),
	'help_description': ('Tell Us About the Person You\'d Like to Hire ')
}
vendor_help_texts = {
	'vend_time':  ('I\'d like to vend...'),
	'want_help': ('''Would you like us to help you find someone to work at your \
	booth or table with you?'''),
	'logo': ('''Please provide any logo you would like displayed on our website \
	and advertising'''),
}

help_time_choices = (('Saturday, 9am to noon', 'Saturday, 9am to noon'),
					('Saturday, 12p to 4pm','Saturday, 12p to 4pm'),
					('Saturday, 4pm to 8pm', 'Saturday, 4pm to 8pm'),
					('Saturday after 8pm', 'Saturday after 8pm'),
					('Sunday, 9am to noon', 'Sunday, 9am to noon'),
					('Sunday, 12p to 4pm', 'Sunday, 12p to 4pm'),
					('Sunday, 4pm to 8pm', 'Sunday, 4pm to 8pm'),
					('Sunday after 8pm', 'Sunday after 8pm'))
