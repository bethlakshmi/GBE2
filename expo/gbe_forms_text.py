# literal text from gbe forms
# see gbetext.py for the rules
# until I copy them oer

participant_form_help_texts = {
    'stage_name': ('The name used in your performance.  The Expo will include this \
name in advertising, and it will be on your badge.  If you leave it blank, we will \
use first and last name.'),
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
this is your troupe name.  If you are a group, but not a troupe, please give the \
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
