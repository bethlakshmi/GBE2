# literal text here. Please use good names, meaning short and sensible. Use 
# as much comment as you need to detail where the stuff is used and for what. 
# Scratch may edit this file to his heart's content. 
# use triple-quotes to allow text to run across lines. The rules of triple-quotes in python:
#    three ''' or """ on either end create a multiline string
#    newlines are preserved unless backslash-escaped
#    special characters can be interpolated according to the standard python rules. But there's
#    no real reason why we'd want to put in, for example, newlines and such, so let's don't. 

# ??? I think this file should also contain options bundles, since they're pretty much literal 
# text. But if it gets too unweildy, we can move stuff around. 

example_string = '''this is a multiline string. a newline 
                  will be included after the word "newline" \
                  on the first line, but not after the one \
                  on the second.'''

# models


phone_number_format_error = '''Phone numbers must be in a standard US format, \
                               such as ###-###-###.'''
time_format_error =  '''Time must be in the format ##:##.'''


profile_alerts = {'onsite_phone':  '''We need a number to reach you at during the expo. \
<a href='profile'>Fix this!</a>''',
                  }

contact_options = (('Email', 'Email'), ('Phone call', 'Phone call'),
                   ('Text', 'Text'))


volunteer_shift_options = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]
    

states_options = [('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), 
                  ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), 
                  ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), 
                  ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), 
                  ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), 
                  ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), 
                  ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), 
                  ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), 
                  ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), 
                  ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), 
                  ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), 
                  ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), 
                  ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), 
                  ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), 
                  ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), 
                  ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), 
                  ('WY', 'Wyoming')]


stage_lighting_options = (('White', 'White'), ('Amber', 'Amber'),
                          ('Blue', 'Blue'), ('Cyan', 'Cyan'),
                          ('Green', 'Green'), ('Orange', 'Orange'),
                          ('Pink', 'Pink'), ('Purple', 'Purple'),
                          ('Red', 'Red'), ('Yellow', 'Yellow'), 
                          ('No lights (not recommended)', 'No lights'))

vendor_lighting_options = (('White', 'White'), 
                          ('Blue', 'Blue'), 
                          ('Red', 'Red'),
                          ('No lights (not recommended)', 'No lights'))


acceptance_states = ((0,'No Decision'),
                     (1,'Reject'),
                     (2,'Wait List'), 
                     (3,'Accepted'))

bid_states = (("Draft", "Draft"),
              ("Submitted", "Submitted"),
              ("Paid","Paid"),
              ("Accepted","Accepted"),
              ("Rejected","Rejected"),
              ("On Hold","On Hold"))

vote_options = ((1, "Strong yes"), (2, "Yes"), (3, "Weak Yes"), 
                (4, "No Comment"), (5, "Weak No"), (6, "No"), 
                (7, "Strong No"), (0, "Undecided"), (-1, "Author"))


festival_list = (('GBE', 'The Great Burlesque Exposition'), 
                 ('BHOF', 'Miss Exotic World/Burlesque Hall of Fame'), 
                 ('NYBF', 'New York Burlesque Festival'),
                 ('NOBF','New Orleans Burlesque Festival'),
                 ('TBF','Texas Burlesque Festival'))

festival_experience = ( ('No', 'No'), ('Yes', 'Yes'), ('Won', 'Yes - and Won!'))

yesno_options = (("Yes", "Yes"), ("No", "No"))

video_options = (('0', "I don't have any video of myself performing"), 
                 ('1', "This is video of me but not the act I'm submitting"),
                 ('2', "This is video of the act I would like to perform"))
participate_options = (('Yes', 'Yes'), ('No', 'No'), ('Not Sure', 'Not Sure'))
experience_options = (('0', "I'm not a burlesque performer"),
                      ('1', "Less than 1 year"),
                      ('2',"1-2 years"),
                      ('3',"3-4 years"),
                      ('4',"5-6 years"),
                      ('5',"more than 6 years"))

class_options = (('Lecture', "Lecture"),
                 ('Movement', "Movement"),
                 ('Panel', "Panel"),
                 ('Workshop',"Workshop"))

length_options = ((30, "30"),
                  (60, "60"),
                  (90, "90"),
                  (120,"120"))

space_options = (('Movement Class Floor', (("0","Don't Care about Floor"),
                                           ("1","Carpet"),
                                           ("2","Dance Floor"),
                                           ("3","Both"))),
                 ('Lecture Class Setup',(("4","Don't Care about Seating"),
                                         ("5","Lecture Style - tables and chairs face podium"),
                                         ("6","Conversational - seating in a ring"))))


schedule_options = (('Preferred Time', "Preferred Time"),
                    ('Available', "Available"),
                    ('Not Available', "Not Available"))
time_options = (('Morning', "Morning (before noon)"),
                ('Early Afternoon', "Early Afternoon (12PM-3PM)"),
                ('Late Afternoon', "Late Afternoon (3PM-6PM)"))
day_options = (('Fri', "Friday"),
               ('Sat', "Saturday"),
               ('Sun', "Sunday"))

vend_time_options = ((" "," "),('Saturday & Sunday, noon to 8pm ONLY.',
						 "Saturday & Sunday, noon to 8pm ONLY."))
ad_type_options = (("Full Page, Premium","Full Page, Premium"),
					("Full Page, Interior","Full Page, Interior"),
					("Half Page, Premium","Half Page, Premium"),
					("Half Page, Interior","Half Page, Interior"),
					("Quanter Page, Premium","Quanter Page, Premium"),
					("Quanter Page, Interior","Quanter Page, Interior"))

num_panel_options = (("One Panel","One Panel ($30 includes application fee)"),
					("Two Panels","Two Panels ($75; if your work is not accepted, $45 will be refunded)"),
					("Sculpture","My artwork is sculptural and needs to be displayed on a table ($30 includes app. fee)"))



class_proposal_choices = [ ('Class', 'Class'), ('Panel', 'Panel'), ('Either', 'Either')]
