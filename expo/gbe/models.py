from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from gbetext import *    # all literal text including option sets lives in gbetext.py
from gbe_forms_text import *
from datetime import datetime
from  expomodelfields import DurationField



import pytz

group_perms_map = {
    'Act Reviewers': 'Act',
    'Class Reviewers':'Class',
    'Volunteer Reviewers':'Volunteer',
    'Vendor Reviewers':'Vendor' 
}



phone_regex='(\d{3}[-\.]?\d{3}[-\.]?\d{4})'

class Biddable (models.Model):
    '''
    Abstract base class for items which can be Bid
    Essentially, specifies that we want something with a title
    '''
    title = models.CharField(max_length=128)  
    description = models.TextField(blank=True)
    submitted = models.BooleanField(default=False)
                              
    accepted = models.IntegerField(choices=acceptance_states, 
                                   default=0, 
                                   blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name="biddable item"
        verbose_name_plural = "biddable items"
    def __unicode__(self):
        return self.title

    def typeof(self):
        return self.__class__

    @property
    def ready_for_review(self):
        return self.submitted and self.accepted==0


class Profile(models.Model):
    '''
    The core data about any registered user of the GBE site, barring
    the information gathered up in the User object. (which we'll
    expose with properties, I suppose)
    '''
    user_object = models.OneToOneField(User) 
    display_name = models.CharField(max_length=128, blank=True) 
      
    # used for linking tickets  
    purchase_email = models.CharField(max_length=64, blank=True, default='') 
 
    # contact info - I'd like to split this out to its own object
    # so we can do real validation 
    # but for now, let's just take what we get

    address1 = models.CharField(max_length=128, blank=True)
    address2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=2, 
                             choices = states_options,
                             blank=True) 
    zip_code = models.CharField(max_length=10, blank=True)  # allow for ext. ZIP
    country = models.CharField(max_length=128, blank=True)
    # must have = a way to contact teachers & performers on site
    # want to have = any other primary phone that may be preferred offsite
    phone = models.CharField(max_length=50, 
                             validators=[ RegexValidator(regex=phone_regex,
                                                         message=phone_number_format_error) ])

    best_time = models.CharField(max_length=50, 
                                 choices=best_time_to_call_options, 
                                 default='Any', 
                                 blank=True)
    how_heard = models.TextField(blank=True)
                
    def bids_to_review(self):
#        review_groups = [group_perms_map.get(g.name, None) for g in self.user_object.groups.all()]
#        return [rg for rg in review_groups if eval(rg).bids_to_review]
        return []

    @property 
    def address(self):
        address_string =str(self.address1.strip() + '\n' + self.address2.strip()).strip()
        if len(address_string) == 0:
            return ''
        if     (len(self.city) == 0 or 
                len(self.country) == 0 or 
                len (self.state) == 0 or 
                len(self.zip_code) == 0):
            return ''
        return address_string + '\n' + ' '.join ((self.city + ',', 
                                                  self.state,  
                                                  self.zip_code, 
                                                  self.country))
        
    @property
    def special_privs(self):
        from gbetext import special_privileges
        privs = [ special_privileges.get(group, None) for group in 
                  self.privilege_groups]
        return privs

    @property
    def privilege_groups(self):
        groups =  [ group.name for group in self.user_object.groups.all() ]
        return groups

    @property
    def alerts(self):
        import gbetext
        profile_alerts = []
        if ( len(self.display_name.strip()) == 0 or
             len(self.purchase_email.strip()) == 0  ):
            profile_alerts.append(gbetext.profile_alerts['empty_profile'])
        expo_commitments = []
        expo_commitments += self.get_shows()
        expo_commitments += self.is_teaching()
        if (len(expo_commitments) > 0 and 
            len(self.phone.strip()) == 0):
            profile_alerts.append(gbetext.profile_alerts['onsite_phone'])
 
        return profile_alerts
    

    def get_performers(self):
        solos = self.personae.all()
        performers = list(solos)
        for solo in solos:
            performers += solo.combos.all()
            performers += solo.troupes.all()
        return performers
    def get_acts(self):
        acts = []
        performers = self.get_performers()
        for performer in performers:
            acts += performer.acts.all()
        return acts
    def get_shows(self):
        shows = []
        for act in self.get_acts():
            shows += act.appearing_in.all()
        return shows
    def is_teaching(self):
        '''
        return a list of classes this user is teaching
        (not a list of classes they are taking, that's another list)
        '''
        classes = []
        for teacher in self.personae.all():
            classes += teacher.is_teaching.all()
        return classes


    def __unicode__(self):  # Python 3: def __str__(self):
        return self.display_name
        
class Performer (models.Model):
    '''
    Abstract base class for any solo, group, or troupe - anything that can appear
    in a show lineup or teach a class
    The fields are named as we would name them for a single performer. In all cases, 
    when applied to an aggregate (group or troup) they apply to the aggregate as a 
    whole. The Boston Baby Dolls DO NOT list awards won by members of the troupe, only
    those won by the troup. (individuals can list their own, and these can roll up if 
    we want). Likewise, the bio of the Baby Dolls is the bio of the company, not of 
    the members, and so forth. 
    '''
    contact = models.ForeignKey(Profile, related_name='contact')
                                             # the single person the expo should 
                                             # talk to about Expo stuff. Could be the 
                                             # solo performer, or a member of the troupe,
                                             # or a designated agent, but this person
                                             # is authorized to make decisions about 
                                             # the Performer's expo appearances. 
    name = models.CharField(max_length=100,     # How this Performer is listed
                            unique=True)        # in a playbill. 
    homepage = models.URLField (blank = True)
    bio = models.TextField ()
    experience = models.PositiveIntegerField ()       # in years
    awards = models.TextField (blank = True)    
    promo_image = models.FileField(upload_to="uploads/images", 
                                   blank=True)

    festivals = models.TextField (blank = True)     # placeholder only
    def append_alerts(self, alerts):
        '''
        Find any alerts generated by this object's data and append them to the alerts dict
        presented as a parameter
        '''
        return alerts
    
    @property
    def complete(self):
        return True

    def __unicode__(self):
        return self.name

class Persona (Performer):
    '''
    The public persona of one person who performs or teaches. 
    May be aggregated into a group or a troupe, 
    or perform solo, or both. A single person might conceivably maintain two
    distinct performance identities and therefore have multiple
    Persona objects associated with their profile. For example, a
    person who dances under one name and teaches under another would have multiple
    Personae. 
    performer_profile is the profile of the user who dons this persona. 
    '''
    performer_profile = models.ForeignKey(Profile, related_name="personae")   


    @property
    def complete(self):
        return (self.performer_profile.complete and
                self.name is not '' and
                self.bio is not '')
        
    def append_alerts(self, alerts):
        '''
        Find any alerts generated by this object's data and append them to the alerts dict
        presented as a parameter
        '''
        alerts = super(Persona, self).append_alerts(alerts)
        return alerts
    
    class Meta:
        verbose_name_plural= 'personae'


            
class Troupe(Performer):
    '''
    Two or more performers working together as an established entity. A troupe
    connotes an entity with a stable membership, a history, and hopefully a
    future. This suggests that a troupe should have some sort of legal
    existence, though this is not required for GBE. Further specification
    welcomed. 
    Troupes are distinct from Combos in their semantics, but at this time they 
    share the same behavior. 
    '''
    membership = models.ManyToManyField (Persona, 
                                         related_name='troupes')
    def append_alerts(self, alerts):
        '''
        Find any alerts generated by this object's data and append them to the alerts dict
        presented as a parameter
        '''
        alerts = super(Troupe, self).append_alerts()
        return alerts



class Combo (Performer):
    '''
    Two or more performers (Personae), working together, on a temporary or ad-hoc
    basis. For example, two performers who put together a routine for the GBE
    but do not otherwise perform together would be a Combo and not a Troupe. 
    The distinction between Combo and Troupe is basically semantic, and the 
    separation is intended to aid in maintaining that semantic distinction. If 
    it is inconvenient, the separation need not persist in the code. 
    '''
    membership = models.ManyToManyField (Persona, 
                                         related_name='combos')

    def append_alerts(self, alerts):
        '''
        Find any alerts generated by this object's data and append them to the alerts dict
        presented as a parameter
        '''
        alerts = super(Combo, self).append_alerts()
        return alerts


###################
# Techinical info #
###################
class AudioInfo(models.Model):
    '''
    Information about the audio required for a particular Act
    '''
    track_title = models.CharField (max_length=128, blank=True)
    track_artist = models.CharField (max_length=123, blank=True)
    track = models.FileField (upload_to='uploads/audio', blank=True)
    track_duration = DurationField(blank=True)
    need_mic = models.BooleanField (default=False, blank=True)
    notes = models.TextField (blank=True)    
    confirm_no_music = models.BooleanField (default=False)

    @property
    def is_complete(self):
        return (self.confirm_no_music or
                (  (self.title and
                   self.artist)  or
                   self.track
                   ))


    def __unicode__(self):
        try:
            return "AudioInfo: "+ self.techinfo.act.title
        except:
            return "AudioInfo: (deleted act)" 

class LightingInfo (models.Model):
    '''
    Information about the lighting needs of a particular Act
    '''
    stage_color = models.CharField (max_length=25,
                                    choices=stage_lighting_options, 
                                    blank=True)
    stage_second_color = models.CharField (max_length=25,
                                           choices=stage_lighting_options, 
                                           blank=True)
    cyc_color = models.CharField (max_length='25', 
                                  choices=stage_lighting_options, 
                                  blank=True)
    follow_spot = models.BooleanField (default=True)
    backlight = models.BooleanField (default=True)
    notes = models.TextField (blank=True)

    @property
    def is_complete (self):
        return ( self.stage_color and self.cyc_color)


    def __unicode__(self):
        try:
            return "LightingInfo: "+self.techinfo.act.title
        except:
            return "LightingInfo: (deleted act)"

class StageInfo(models.Model):
    '''
    Information about the stage requirements for a particular Act
    confirm field should be offered if the user tries to save with all values false and
    no notes
    '''
    act_duration = DurationField(blank=True)
    intro_text = models.TextField(blank=True)
    set_props = models.BooleanField (default=False)
    clear_props = models.BooleanField (default=False)
    cue_props = models.BooleanField (default=False)
    notes = models.TextField (blank=True)
    confirm = models.BooleanField (default = False)

    
    @property
    def is_complete(self):
        return (self.set_props or self.clear_props or self.cue_props or self.confirm)

    def __unicode__(self):
        try:
            return "StageInfo: " +self.techinfo.act.title
        except:
            return "StageInfo: (deleted act)"

class TechInfo (models.Model):
    '''
    Gathers up technical info about an act in a show. 
    '''
    
    audio = models.OneToOneField (AudioInfo, blank=True)
    lighting = models.OneToOneField (LightingInfo, blank=True)
    stage = models.OneToOneField (StageInfo, blank=True)
    
    @property
    def is_complete(self):
        return (self.audio.is_complete and
                self.lighting.is_complete and
                self.stage.is_complete)
    
    def __unicode__(self):
        try:
            return "Techinfo: "+ self.act.title
        except:
            return "Techinfo: (deleted act)"

#######
# Act #
#######

class Act (Biddable):
    '''
    A performance, either scheduled or proposed.
    Until approved, an Act is simply a proposal. 
    Note: Act contains only information about a particular item that 
    can occupy a particular time slot in a particular performance. All
    information about performers is carried in Performer objects
    linked to Acts. 
    '''
    performer = models.ForeignKey(Performer,
                                  related_name='acts', blank=True, null=True )
         

    tech = models.OneToOneField(TechInfo, blank = True)
    video_link = models.URLField (blank = True)
    video_choice = models.CharField(max_length=2, 
                             choices = video_options,
                             blank=True) 
    shows_preferences = models.TextField(blank=True)
    why_you = models.TextField(blank=True)

    is_not_blank = ('len(%s) > 0', '%s cannot be blank')

    validation_list = [ (('title', 'Title'), is_not_blank),
                        (('description', 'Description'), is_not_blank),
                        ]
    
    def validation_problems_for_submit(self):
        return [fn[1] %field[1] for (field, fn) in self.validation_list if 
                not eval(fn[0] % ('self.' + field[0]))]
 
    def typeof(self):
        return self.__class__

    @property
    def bids_to_review(self):
        return type(self).objects.filter(submitted=True).filter(accepted=0)
 
    @property
    def bid_review_header(self):
        return  (['Performer', 'Act Title', 'Last Update', 'Reviews', 'Action'])

    @property
    def bid_review_summary(self):
        return  (self.performer.name, 
                   self.title, 
                   self.updated_at.astimezone(pytz.timezone('America/New_York')))

    @property
    def complete(self):
        return (self.performer.complete and
                len(self.title) > 0 and
                len(self.description) >0 and
                len(self.intro_text) >0 and
                len(self.video_choice) >0)

    @property
    def tech_ready(self):
        return (self.tech.is_complete and
                self.performer.complete and
                self.intro_text is not '')

    @property
    def alerts(self):
        '''
        Return a list of alerts pertaining to this object
        '''
        this_act_alerts=[]
        if self.complete:     ### TODO: jpk: refactor this, please, it's awful. -jpk
            if self.submitted:
                this_act_alerts.append(act_alerts['act_complete_submitted'] % self.id)
            else:
                this_act_alerts.append(act_alerts['act_complete_not_submitted'] % self.id)
        else:
            if self.submitted:
                this_act_alerts.append(act_alerts['act_incomplete_submitted'] % self.id)
            else:
                this_act_alerts.append(act_alerts['act_incomplete_not_submitted'] % self.id)
        
        return this_act_alerts

    @property
    def bid_fields(self):
        return (['performer',
                 'shows_preferences',
                 'title', 
                 'track_title',
                 'track_artist', 
                 'track_duration',
                 'act_duration',
                 'video_link',
                 'video_choice',
                 'description',
                 'why_you'],
                [ 'title', 'description', 'shows_preferences', 'performer'],
              )
    
    @property
    def bid_draft_fields(self):
        return (['title', 'performer'])

    def __str__ (self):
        return str(self.performer) + ": "+self.title


class Room(models.Model):
    '''
    A room at the expo center
    '''
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    overbook_size = models.IntegerField()
    def __str__ (self):
        return self.name
    
class Event (models.Model):
    '''
    Event is the base class for any scheduled happening at the expo. 
    Events fall broadly into "shows" and "classes". Classes break down
    further into master classes, panels, workshops, etc. Shows are not
    biddable (though the Acts comprising them are) , but classes arise
    from participant bids.  
    '''
    title = models.CharField(max_length=128)
    description = models.TextField()  # public-facing description 
    blurb = models.TextField()        # short description
    duration = DurationField()


    ## run-specific info, in case we decide to return to the run idea
  #  room = models.ForeignKey(Room, blank=True)
    notes = models.TextField()  #internal notes about this event
    owner = models.ManyToManyField(Profile)  # Responsible party
                                                
    def __str__(self):
        return self.title

class Show (Event):
    '''
    A Show is an Event consisting of a sequence of Acts. 
    '''
    acts = models.ManyToManyField(Act, related_name="appearing_in")
    mc = models.ManyToManyField(Persona, related_name="mc_for")      
    
                                                
class Class (Biddable, Event):
    '''
    A Class is an Event where one or a few people
    teach/instruct/guide/mediate and a number of participants
    spectate/participate.  Participation *may* be limited for workshops,
    but is rarely limited for anything else.  Occupancy information is requested to
    give us a general sense of the teacher's expectations.
    '''
    teacher = models.ForeignKey(Persona,  
                                related_name='is_teaching')
    
    registration = models.ManyToManyField(Profile, 
                                          related_name='classes',
                                          blank=True)
    type = models.IntegerField(choices=((0, "Lecture"), (1, "Movement"),
                                        (2,"Workshop")))
    minimum_enrollment = models.IntegerField (blank=True, default=1)
    maximum_enrollment = models.IntegerField (blank=True, default=20)
    organization = models.CharField(max_length=128, blank=True)    
    type = models.CharField(max_length=128, 
                            choices=class_options, 
                            blank=True, 
                            default="Lecture")
    fee = models.IntegerField(blank=True, default=0)
    other_teachers = models.CharField(max_length=128, blank=True)
    length_minutes = models.IntegerField(choices=class_length_options, 
                                         default=60, blank=True)
    history =  models.TextField(max_length = 500, blank=True)
    run_before = models.TextField(max_length=500, blank=True)
    schedule_constraints = models.TextField(blank=True)
    space_needs = models.CharField(max_length=128, 
                                   choices=space_options, 
                                   blank=True, 
                                   default='Please Choose an Option')
    physical_restrictions =  models.TextField(max_length = 500, blank=True)
    multiple_run =  models.CharField(max_length=20,
                                choices=yesno_options, default="No") 



    @property
    def bids_to_review(self):
        return type(self).objects.filter(submitted=True).filter(accepted=0)

    @property
    def get_bid_fields(self):
        return  (['title',
                  'teacher',
                  'description', 
                  'maximum_enrollment',
                  'type', 
                  'fee', 
                  'length_minutes',
                  'history',
                  'schedule_constraints',
                  'space_needs',
              ], 
                 [ 'title', 'teacher', 'description', 'schedule_constraints'])


    @property
    def get_draft_fields(self):
        return  (['title', 'teacher'])

    @property
    def complete(self):
        return (self.title is not '' and
                self.teacher is not None and
                self.description is not '' and
                self.blurb is not '' 
                )
    @property
    def bid_review_header(self):
        return  (['Title', 'Teacher', 'Type', 'Last Update', 'Reviews', 'Action'])

    @property
    def bid_review_summary(self):
        return  (self.title, self.teacher, self.type, self.updated_at.astimezone(pytz.timezone('America/New_York')))
    
    
    def __str__(self):
        return self.title
        

    class Meta:
        verbose_name_plural='classes'
    

    
class BidEvaluation(models.Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    evaluator = models.ForeignKey(Profile)
    vote = models.IntegerField(choices = vote_options)
    notes = models.TextField(blank='True')
    bid = models.ForeignKey(Biddable)
    
    def __unicode__(self):
        return self.bid.title+": "+self.evaluator.display_name

class PerformerFestivals(models.Model):
    festival = models.CharField(max_length=20, choices=festival_list)
    experience = models.CharField(max_length=20,
                                  choices=festival_experience, default='No')
    act = models.ForeignKey(Act)

    

class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer. 
    '''
    profile = models.ForeignKey(Profile)
    number_shifts = models.IntegerField(choices = volunteer_shift_options, default=1)
    availability = models.TextField()
    unavailability = models.TextField()
    interests = models.TextField()
    opt_outs = models.TextField(blank=True)
    pre_event = models.BooleanField(choices= boolean_options, default=False)
    background = models.TextField(blank=True)

    def __unicode__(self):
        return 'Volunteer: '+ self.profile.display_name
    @property
    def bid_review_header(self):
        return  (['Name', 'Interests', 'Reviews', 'Action'])

    @property
    def bid_review_summary(self):
        interest_string = ''
        for option_id, option_value in volunteer_interests_options:
            if option_id in self.interests:
                interest_string += option_value + ', '
        return  (self.profile.display_name, interest_string)


class Vendor(Biddable):
    '''
    A request for space in the Expo marketplace. 
    Note that company name is stored in the title field inherited from Biddable, 
    and description is also inherited
    '''
    profile = models.ForeignKey(Profile)
    website = models.URLField(blank=True)
    physical_address = models.TextField()  # require physical address
    publish_physical_address = models.BooleanField(default=False)
    logo = models.FileField(upload_to="uploads/images", blank=True)
    want_help = models.BooleanField(choices = boolean_options, blank=True, default=False)
    help_description = models.TextField(blank=True)
    help_times = models.TextField(blank=True)
    def __unicode__(self): 
        return self.title  # "title" here is company name
    def validation_problems_for_submit(self):
        return []

    @property
    def bid_review_header(self):
        return  (['Bidder', 'Business Name', 'Website', 'Last Update', 'Reviews', 'Action'])

    @property
    def bid_review_summary(self):
        return (self.profile.display_name, self.title, self.website,self.updated_at.astimezone(pytz.timezone('America/New_York')))


class AdBid(Biddable):
    '''
    A request for a space in the marketplace.
    Vendors have to bid, too
    '''
    company = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=128, choices=ad_type_options)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.company;


class ArtBid(Biddable):
    '''
    A request for a space in the marketplace.
    Vendors have to bid, too
    '''
    bio = models.TextField(max_length=500, blank=True)
    works = models.TextField(max_length=500, blank=True)
    art1 = models.FileField(upload_to="uploads/images", blank=True)
    art2 = models.FileField(upload_to="uploads/images", blank=True)
    art3 = models.FileField(upload_to="uploads/images", blank=True)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.bidder.display_name;
                



class ClassProposal(models.Model):
    title = models.CharField(max_length = 128)
    name = models.CharField(max_length = 128, blank = True)
    email = models.EmailField(blank=True)
    proposal = models.TextField()
    type = models.CharField (max_length = 20, 
                             choices = class_proposal_choices,
                             default = 'Class')
    display = models.BooleanField(default = False)
    
    def __unicode__(self):
        return self.title
    
    @property
    def bid_review_header(self):
        return  (['Title', 'Proposal', 'Type', 'Submitter', 'Published','Action'])

    @property
    def bid_review_summary(self):
        if self.display:
            published = "Yes"
        else:
            published = ""
        return  (self.title, self.proposal, self.type, self.name, published)

    @property
    def presenter_bid_header(self):
        return  (['Title', 'Proposal', 'Type'])

    @property
    def presenter_bid_info(self):
        return  (self.title, self.proposal, self.type)


class ProfilePreferences(models.Model):
    '''
    User-settable preferences controlling interaction with the 
    Expo and with the site. 
    '''
    profile = models.OneToOneField(Profile,
                                   related_name='preferences')
    in_hotel = models.CharField(max_length=10, 
                                blank=True, 
                                choices= yes_no_maybe_options)
    inform_about = models.TextField(blank=True)
    show_hotel_infobox = models.BooleanField(default=True)

    
