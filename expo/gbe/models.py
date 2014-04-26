from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from gbetext import *    # all literal text including option sets lives in gbetext.py


class Biddable (models.Model):
    '''
    Abstract base class for items which can be Bid
    Essentially, specifies that we want something with a title
    '''
    title = models.CharField(max_length=128)  
    description = models.TextField(blank=True)
    accepted = models.IntegerField(choices=acceptance_states, default=0 )    
    class Meta:
        verbose_name="biddable item"
        verbose_name_plural = "biddable items"

phone_regex='(\d{3}[-\.]?\d{3}[-\.]?\d{4})'

class Profile(models.Model):
    '''
    The core data about any registered user of the GBE site, barring
    the information gathered up in the User object. (which we'll
    expose with properties, I suppose)
    '''
    user_object = models.OneToOneField(User) 
    display_name = models.CharField(max_length=128, blank=True) 
      
    # used for linking tickets  
    purchase_email = models.CharField(max_length=64, default = '') 
 
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
    onsite_phone = models.CharField(max_length=50, 
                                    blank=True, 
                                    validators=[
                                        RegexValidator(regex=phone_regex,
                                                       message=phone_number_format_error)])
    offsite_preferred = models.CharField(max_length=50, 
                                         blank=True,
                                         validators=[
                                             RegexValidator(regex=phone_regex,
                                                            message=phone_number_format_error)])

    best_time = models.CharField(max_length=50, blank=True)
    how_heard = models.TextField(blank=True)
    preferred_contact = models.CharField(max_length=50, choices=contact_options, default="Email");
 
    def get_warnings(self, own_profile):
        if not own_profile:     
            return None
        return {'profile':["This is a test warning about your profile"]}
    def get_performers(self, own_profile):
        solos = self.personae.all()
        performers = list(solos)
        for solo in solos:
            performers += solo.combos.all()
            performers += solo.troupes.all()
        return performers
    def get_acts(self, own_profile):
        acts = []
        performers = self.get_performers(own_profile)
        for performer in performers:
            acts += performer.acts.all()
        return acts
    def get_shows(self, own_profile):
        shows = []
        for act in self.get_acts(own_profile):
            shows += act.appearing_in.all()
        return shows
    def is_teaching(self, own_profile):
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
    experience = models.IntegerField ()       # in years
    awards = models.TextField (blank = True)    
    promo_image = models.FileField(upload_to="uploads/images", 
                                   blank=True)

    video_link = models.URLField (blank = True)
    puffsheet  = models.FileField (upload_to="uploads/files", 
                                   blank = True)  # "printed" press kit
    festivals = models.TextField (blank = True)     # placeholder only

    def __str__(self):
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
    is_teacher = models.BooleanField(default=False)
    is_performer = models.BooleanField(default=False)
    
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
    creator = models.TextField (blank = True) # just to keep track of who made this



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


###################
# Techinical info #
###################
class AudioInfo(models.Model):
    '''
    Information about the audio required for a particular Act
    '''
    title = models.CharField (max_length=128, blank=True)
    artist = models.CharField (max_length=123, blank=True)
    track = models.FileField (upload_to='uploads/audio', blank=True)
    duration = models.CharField (max_length=128,blank=True)  
    need_mic = models.BooleanField (default=False, blank=True)
    notes = models.TextField (blank=True)    
    confirm_no_music = models.BooleanField (default=False)

    @property
    def is_complete(self):
        return (confirm_no_music or
                (  title and
                   artist and
                   track and
                   duration))

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
        return ( stage_color and cyc_color)

class PropsInfo(models.Model):
    '''
    Information about the props requirements for a particular Act
    confirm field should be offered if the user tries to save with all values false and
    no notes
    '''
    set_props = models.BooleanField (default=False)
    clear_props = models.BooleanField (default=False)
    cue_props = models.BooleanField (default=False)
    notes = models.TextField (blank=True)
    confirm = models.BooleanField (default = False)

    
    @property
    def is_complete(self):
        return (self.set_props or self.clear_props or self.cue_props or confirm)

class TechInfo (models.Model):
    '''
    Gathers up technical info about an act in a show. 
    '''
    audio = models.OneToOneField (AudioInfo, blank=True)
    lighting = models.OneToOneField (LightingInfo, blank=True)
    props = models.OneToOneField (PropsInfo, blank=True)
    
    @property
    def is_complete(self):
        return (self.audio.is_complete and
                self.lighting.is_complete and
                self.props.is_complete)
    

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
    #title = models.CharField(max_length=128)  
    #description = models.TextField(blank=True)
    # inherit title and description from Biddable
    owner = models.ForeignKey(Profile)
    performer = models.ForeignKey(Performer,
                                  related_name='acts')  # limit choices to the owner's Performers
    intro_text = models.TextField()
    tech = models.ForeignKey(TechInfo, blank = True)
    in_draft = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)


    def _get_bid_fields(self):
        return  ( ['owner',
                    'title', 
                    'description', 
                    'performer', 
                    'intro_text', ], 
                   [ 'title', 
                     'duration', 
                     'description'],
               )
    bid_fields = property(_get_bid_fields)

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
    duration = models.CharField(max_length=128) #Should be stored as durations


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
    
                                                
class Class (Event, Biddable):
    '''
    A Class is an Event where one or a few people
    teach/instruct/guide/mediate and a number of participants
    spectate/participate. Usually, there will be a limited space and
    pre-registration will be at least permitted and usually
    encourged. 
    '''
    teacher = models.ForeignKey(Persona,  
                                related_name='is_teaching')
    
    registration = models.ManyToManyField(Profile, 
                                          related_name='classes')
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
    length_minutes = models.IntegerField(choices=length_options, 
                                         default=60)
    history =  models.TextField(max_length = 500, blank=True)
    run_before = models.TextField(max_length=500, blank=True)
    schedule_constraints = models.CharField(max_length=128, blank=True)
    space_needs = models.CharField(max_length=128, 
                                   choices=space_options, 
                                   blank=True, 
                                   default='Please Choose an Option')
    physical_restrictions =  models.TextField(max_length = 500, blank=True)
    multiple_run =  models.CharField(max_length=20,
                                choices=yesno_options, default="No") 
    @property
    def get_bid_fields(self):
        return  (['title',
                  'teacher',
                  'description', 
                  'blurb', 
                  'maximum_enrollment',
                  'minimum_enrollment',
                  'organization',
                  'type', 
                  'fee', 
                  'length_minutes',
                  'history',
                  'schedule_constraints',
                  'space_needs',
                  'physical_restrictions'
              ], 
                 ['title', 
                  'teacher',
                  'description',
                  'maximum_enrollment', 
                  'minimum_enrollment',
                  'length_minutes',
                  ])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural='classes'

class Bid(models.Model):
    '''
    A Bid is a proposal for an act, a class, a vendor, or whatnot.
    This is the abstract base for these various bids.
    '''
    bid_item = models.ForeignKey(Biddable, null=True, blank=True)
    bidder = models.ForeignKey(Profile)
    state = models.CharField(max_length=20,
                             choices=bid_states, default="Draft") 
    last_update = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'bid'
        verbose_name_plural = 'bids'
    
class BidEvaluation(models.Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    evaluator = models.ForeignKey(Profile)
    vote = models.IntegerField(choices = vote_options)
    notes = models.TextField()
    bid = models.ForeignKey(Biddable)

class PerformerFestivals(models.Model):
    festival = models.CharField(max_length=20, choices=festival_list)
    experience = models.CharField(max_length=20,
                                  choices=festival_experience, default='No')
    act = models.ForeignKey(Act)


class ClassBid(Bid):
    '''
    A proposed class
    we can use this for all class-like items
    '''
    
    def __unicode__(self):  
        return self.type+':  '+self.title;

class VendorBid(Bid):
    '''
    A request for a space in the marketplace.
    Vendors have to bid, too
    '''
    vend_time = models.CharField(max_length=128, choices=vend_time_options, default=" ")
    company = models.CharField(max_length=128, blank=True)
    description = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    logo = models.FileField(upload_to="uploads/images", blank=True)
    want_help = models.CharField(max_length=128, choices=yesno_options, blank=True)
    Saturday_9AM_to_12PM = models.BooleanField()
    Saturday_12PM_to_4PM = models.BooleanField()
    Saturday_4PM_to_8PM = models.BooleanField()
    Saturday_after_8PM = models.BooleanField()
    Sunday_9AM_to_12PM = models.BooleanField()
    Sunday_12PM_to_4PM = models.BooleanField()
    Sunday_4PM_to_8PM = models.BooleanField()
    Sunday_after_8PM = models.BooleanField()
    help_description = models.TextField(max_length=500, blank=True)
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.company;
	
class AdBid(Bid):
    '''
    A request for a space in the marketplace.
    Vendors have to bid, too
    '''
    company = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=128, choices=ad_type_options)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.company;


class ArtBid(Bid):
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
                
