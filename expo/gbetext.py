# literal text here. Please use good names, meaning short and sensible. Use
# as much comment as you need to detail where the stuff is used and for what.


# models

stageinfo_incomplete_warning = ("Please confirm that you have no props "
                                "requirements")

lightinginfo_incomplete_warning = "Please check your lighting info."
audioinfo_incomplete_warning = ("Please confirm that you will have no audio "
                                "playback for your performance")

conference_statuses = (
    ('upcoming', 'upcoming'),
    ('ongoing', 'ongoing'),
    ('completed', 'completed'),
)

act_format = (
    ('normal', 'normal'),
    ('summer', 'summer'),
)

landing_page_no_profile_alert = ("There's been an issue with your "
                                 "registration. Contact "
                                 "registrar@burlesque-expo.com")

phone_number_format_error = ("Phone numbers must be in a standard US format, "
                             "such as ###-###-###.")

time_format_error = "Time must be in the format ##:##."

conf_volunteer_save_error = ("There was an error saving your presentation "
                             "request, please try again.")

not_yours = "You don't own that bid."

ONSITE_PHONE = ("We need a number to reach you at during the expo. "
                "<a href=' %s '>Fix this!</a>")
EMPTY_PROFILE = ("Your profile needs an update, please review it, and save "
                 "it. <a href=' %s '>Update it now!</a>")
SCHEDULE_REHEARSAL = ('You need to schedule a rehearsal slot and/or update '
                      'act tech info for "%s". <a href = " %s ">'
                      'Fix this now!</a>')

profile_alerts = {'onsite_phone': ONSITE_PHONE,
                  'empty_profile': EMPTY_PROFILE,
                  'schedule_rehearsal': SCHEDULE_REHEARSAL}

ACT_COMPLETE_NOT_SUBMITTED = ("This act is complete and can be submitted "
                              "whenever you like. "
                              "<a href = '{% url 'gbe:act_edit' act_id %}'>"
                              "Review and Submit Now </a>")
ACT_COMPLETE_SUBMITTED = ("This act is complete and has been submitted for "
                          "review.")
ACT_INCOMPLETE_NOT_SUBMITTED = ("This act is not complete and cannot be "
                                "submitted for a show.")
ACT_INCOMPLETE_NOT_SUBMITTED = ("This act is not complete but it has been "
                                "submitted for a show.")

act_alerts = {'act_complete_not_submitted': ACT_COMPLETE_NOT_SUBMITTED,
              'act_complete_submitted': ACT_COMPLETE_SUBMITTED,
              'act_incomplete_not_submitted': ACT_INCOMPLETE_NOT_SUBMITTED,
              'act_incomplete_submitted': ACT_INCOMPLETE_NOT_SUBMITTED}

act_shows_options = [(0, 'The Bordello (Fri. Late)'),
                     (1, 'The Main Event, in competition'),
                     (2, 'The Main Event, not in competition'),
                     (3, 'The Newcomer\'s Showcase')]

more_shows_options = [
    (4, 'Friday, July 28'),
    (5, 'Saturday, July 29'),
    (6, 'Sunday, July 30'),
    (7, 'Please also consider this act for GBE12, January 5-7, 2018')]

act_other_perf_options = [(0, ("Go-go dance during one or more of the shows "
                               "(we'll ask which one later)")),
                          (1, ("Be part of the opening number for The Main "
                               "Event")),
                          (2, "Model in the Fashion Show (Sunday afternoon)"),
                          (3, ("Model in the Swimsuit Show (Saturday night "
                               "late)"))]

summer_other_perf_options = [
    (0, "Go-go dance during a show"),
    (1, "Be part of the opening number."),
    (2, "Model in the Fashion Show (Saturday afternoon)")]

all_shows_options = act_shows_options + [(4, 'The Rhinestone Review')]

cue_options = [('Theater', 'Theater'),
               ('Alternate', 'Alternate'),
               ('None', 'None')]

best_time_to_call_options = [('Any', 'Any'),
                             ('Mornings', 'Mornings'),
                             ('Afternoons', 'Afternoons'),
                             ('Evenings', 'Evenings')]

volunteer_shift_options = [(2, 2),
                           (3, 3),
                           (4, 4),
                           (5, 5),
                           (6, 6),
                           (7, 7),
                           (8, 8),
                           (9, 9),
                           (10, 10),
                           (11, 11),
                           (12, 12)]

states_options = [('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'),
                  ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
                  ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'),
                  ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
                  ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
                  ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
                  ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'),
                  ('MI', 'Michigan'), ('MN', 'Minnesota'),
                  ('MS', 'Mississippi'),
                  ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
                  ('NV', 'Nevada'), ('NH', 'New Hampshire'),
                  ('NJ', 'New Jersey'),
                  ('NM', 'New Mexico'), ('NY', 'New York'),
                  ('NC', 'North Carolina'),
                  ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
                  ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
                  ('RI', 'Rhode Island'),
                  ('SC', 'South Carolina'), ('SD', 'South Dakota'),
                  ('TN', 'Tennessee'),
                  ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
                  ('VA', 'Virginia'),
                  ('WA', 'Washington'), ('WV', 'West Virginia'),
                  ('WI', 'Wisconsin'),
                  ('WY', 'Wyoming'), ('OTHER', 'Other/Non-US')]

offon_options = (("Off", "OFF"), ("ON", "ON"))

stage_lighting_options = (('White', 'White'),
                          ('Blue', 'Blue'),
                          ('Green', 'Green'),
                          ('OFF', 'OFF'),
                          ('Pink', 'Pink'),
                          ('Purple', 'Purple'),
                          ('Red', 'Red'),
                          ('Yellow', 'Yellow'))

follow_spot_options = (('White', 'White'), ('Blue', 'Blue'), ('OFF', 'OFF'),
                       ('Pink', 'Pink'), ('Purple', 'Purple'), ('Red', 'Red'))

cyc_color_options = (('Blue', 'Blue'), ('Green', 'Green'), ('OFF', 'OFF'),
                     ('Pink', 'Pink'), ('Purple', 'Purple'), ('Red', 'Red'),
                     ('White', 'White'), ('Yellow', 'Yellow'))


vendor_lighting_options = (('White', 'White'),
                           ('Blue', 'Blue'),
                           ('Red', 'Red'),
                           ('No lights (not recommended)', 'No lights'))


acceptance_states = ((0, 'No Decision'),
                     (1, 'Reject'),
                     (2, 'Wait List'),
                     (3, 'Accepted'),
                     (4, 'Withdrawn'),
                     (5, 'Duplicate'))

class_acceptance_states = ((1, 'Reject'),
                           (2, 'Wait List'),
                           (3, 'Accepted'))

vote_options = ((1, "Strong yes"),
                (2, "Yes"),
                (3, "Weak Yes"),
                (4, "No Comment"),
                (5, "Weak No"),
                (6, "No"),
                (7, "Strong No"),
                (-1, "Abstain"))


festival_list = (('GBE', 'The Great Burlesque Exposition'),
                 ('BHOF', 'Miss Exotic World/Burlesque Hall of Fame'),
                 ('NYBF', 'New York Burlesque Festival'),
                 ('NOBF', 'New Orleans Burlesque Festival'),
                 ('TBF', 'Texas Burlesque Festival'))

festival_experience = (('No', 'No'),
                       ('Yes', 'Yes'),
                       ('Won', 'Yes - and Won!'))

yesno_options = (("Yes", "Yes"), ("No", "No"))
yes_no_maybe_options = (("Yes", "Yes"), ("No", "No"), ('Maybe', 'Maybe'))
boolean_options = ((True, "Yes"), (False, "No"))

video_options = (('0', "I don't have any video of myself performing"),
                 ('1', "This is video of me but not the act I'm submitting"),
                 ('2', "This is video of the act I would like to perform"))
participate_options = (('Yes', 'Yes'), ('No', 'No'), ('Not Sure', 'Not Sure'))
experience_options = (('0', "I'm not a burlesque performer"),
                      ('1', "Less than 1 year"),
                      ('2', "1-2 years"),
                      ('3', "3-4 years"),
                      ('4', "5-6 years"),
                      ('5', "more than 6 years"))

event_options = (('Special', "Special Event"),
                 ('Volunteer', "Volunteer Opportunity"),
                 ('Master', "Master Class"),
                 ('Drop-In', "Drop-In Class"),
                 ('Staff Area', 'Staff Area'),
                 ('Rehearsal Slot', 'Rehearsal Slot'))

new_event_options = (('Special', "Special Event"),
                     ('Master', "Master Class"),
                     ('Drop-In', "Drop-In Class"),
                     ('Staff Area', 'Staff Area'),
                     ('Rehearsal Slot', 'Rehearsal Slot'))

class_options = (('Lecture', "Lecture"),
                 ('Movement', "Movement"),
                 ('Panel', "Panel"),
                 ('Workshop', "Workshop"))

length_options = ((30, "30"),
                  (60, "60"),
                  (90, "90"),
                  (120, "120"))

class_length_options = ((60, "60"),
                        (90, "90"),
                        (120, "120"))

space_options = (('Movement Class Floor',
                  (("0", "Don't Care about Floor"),
                   ("1", "Carpet"),
                   ("2", "Dance Floor"),
                   ("3", "Both"))),
                 ('Lecture Class Setup',
                  (("4", "Don't Care about Seating"),
                   ("5", "Lecture Style - tables and chairs face podium"),
                   ("6", "Conversational - seating in a ring"))))

schedule_options = (('Preferred Time', "Preferred Time"),
                    ('Available', "Available"),
                    ('Not Available', "Not Available"))
time_options = (('Morning', "Morning (before noon)"),
                ('Early Afternoon', "Early Afternoon (12PM-3PM)"),
                ('Late Afternoon', "Late Afternoon (3PM-6PM)"))
day_options = (('Fri', "Friday"),
               ('Sat', "Saturday"),
               ('Sun', "Sunday"))

role_options = (('Teacher', "Teacher"),
                ('Performer', "Performer"),
                ('Volunteer', "Volunteer"),
                ('Panelist', "Panelist"),
                ('Moderator', "Moderator"),
                ('Staff Lead', "Staff Lead"),
                ('Technical Director', "Technical Director"),
                ('Producer', "Producer"))

act_casting_label = "Section"

vend_time_options = (
    (" ",
     " "),
    ('Saturday & Sunday, noon to 8pm ONLY.',
     "Saturday & Sunday, noon to 8pm ONLY."))
ad_type_options = (("Full Page, Premium", "Full Page, Premium"),
                   ("Full Page, Interior", "Full Page, Interior"),
                   ("Half Page, Premium", "Half Page, Premium"),
                   ("Half Page, Interior", "Half Page, Interior"),
                   ("Quarter Page, Premium", "Quarter Page, Premium"),
                   ("Quarter Page, Interior", "Quarter Page, Interior"))

num_panel_options = (
    ("One Panel",
     "One Panel ($30 includes application fee)"),
    ("Two Panels",
     "Two Panels ($75; if your work is not accepted, $45 will be refunded)"),
    ("Sculpture",
     "My artwork is sculptural and needs to be displayed on a table " +
     "($30 includes app. fee)"))

class_proposal_choices = [
    ('Class', 'Class'),
    ('Panel', 'Panel'),
    ('Either', 'Either')]

###############
#  Static Text options for the Scheduler
###############
#    Options for schedule blocking
blocking_text = (('False', False), ('Hard', 'Hard'), ('Soft', 'Soft'))

#    Options for time types
time_text = (('Start Time', 'Start Time'),
             ('Stop Time', 'Stop Time'),
             ('Hard Time', 'Hard Time'),
             ('Soft Time', 'Soft Time'))

event_labels = {'type': 'Type',
                'fee': 'Materials Fee',
                'parent_event': 'Part of',
                'volunteer_category': 'Opportunity Category'
                }

overlap_location_text = ' (alt)'


calendar_type = {0: 'General',
                 1: 'Conference',
                 2: 'Volunteer'}

calendar_for_event = {
    'Special': "General",
    'Volunteer': "Volunteer",
    'Master': "General",
    'Drop-In': "General",
    'Staff Area': None,
    'Rehearsal Slot': None,
    'Class': 'Conference',
    'Show': 'General'
}

default_class_submit_msg = "Your class was successfully submitted"
default_class_draft_msg = "Your draft was successfully saved"
default_act_submit_msg = "Your act was successfully submitted"
default_act_draft_msg = "Your draft was successfully saved"
default_costume_submit_msg = "Your costume was successfully submitted"
default_costume_draft_msg = "Your draft was successfully saved"
default_propose_submit_msg = "Your idea was successfully submitted"
default_vendor_submit_msg = "Your vendor proposal was sucessfully submitted"
default_vendor_draft_msg = "Your draft was successfully saved"
default_volunteer_submit_msg = \
    "Your offer to volunteer was successfully submitted"
default_volunteer_edit_msg = "You have successfully edited a volunteer."
default_volunteer_no_interest_msg = \
    "You must have at least one interest to volunteer."
default_volunteer_no_bid_msg = \
    "We are not accepting volunteer bids at this time."
existing_volunteer_msg = \
    "You've already offered to volunteer, " + \
    "would you like to update your proposal?"
default_window_schedule_conflict = "Your change caused a conflict.  " + \
    "You were scheduled for:"
default_clone_msg = "You have successfully made a new copy."
default_update_profile_msg = "Your profile has been updated."
default_create_persona_msg = "Your persona has been created."
default_edit_persona_msg = "Your persona has been updated."
default_edit_troupe_msg = "Your troupe has been updated."
default_update_act_tech = "Your Act Technical Details have been updated."
default_act_title_conflict = '''You've aready created a draft or made a \
submission for this act.  View or edit that act here:  <a href="%s">%s</a>'''
act_not_unique = '''Please name this act with a different title, \
or edit the existing act.'''
no_casting_msg = '''The casting role you've specified is not one our defined \
roles.  Check the dropdown and try again.'''
no_profile_msg = '''Your profile is not complete, you must provide a first \
and last name, a name we can use on your badge, and a phone number we can \
use to notify you of changes to the schedule at run time.'''
no_login_msg = '''Please set up and account and give us some ways to \
contact you, or login, if you already have an account.'''
full_login_msg = '''%s - <a href="%s">Login</a>'''
default_deactivate_profile_admin_msg = '''This user is involved in one or \
more activities on this site.  To protect unintended changes, the user was \
deactivated.  To delete, reactivate, or review the details, go to the admin: \
'''
default_delete_profile_admin_msg = '''No relevant site data found, this user \
has been completely deleted'''
