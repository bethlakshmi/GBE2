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
    class Meta:
#        abstract=True
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
        # we really do need both legal and display name, we use the legal to verify 
        # tickets purchased, and I'd like to add a switch for which name gets shown where 
        # for bios

        # stage name is now linked with the stage persona (ie, Performer)
        # Can still have a display name for people who want to use something
        # other than their legit name: if present, this is used on all badges
        # and such
      
    # used for linking tickets  
    # ???? How does this differ from their other email? -jpk
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
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.display_name;
        
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
    name = models.CharField(max_length=100)     # How this Performer is listed
                                                # in a playbill. 
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

class IndividualPerformer (Performer):
    '''
    One person who performs or teaches. May be aggregated into a group or a troupe, 
    or perform solo, or both. A single person might conceivably maintain two
    distinct performance identities and therefore have multiple
    IndividualPerformer objects associated with their profile. 
    '''
    performer_profile = models.ForeignKey(Profile)    # the performer's identity on the site


class Troupe(Performer):
    '''
    Two or more performers working together as an established entity. A troupe
    connotes an entity with a stable membership, a history, and hopefully a
    future. This suggests that a troupe should have some sort of legal
    existence, though this is not required for GBE. Further specification
    welcomed. 
    '''
    membership = models.ManyToManyField (IndividualPerformer, 
                                         related_name='memberships')
    creator = models.TextField (blank = True) # just to keep track of who made this



class Combo (Performer):
    '''
    Two or more Performers, working together, on a temporary or ad-hoc
    basis. For example, two performers who put together a routine for the GBE
    but do not otherwise perform together would be a Combo and not a Troupe. The
    distinction between Combo is basically semantic, and the separation is
    intended to aid in maintaining that semantic distinction. If it is
    inconvenient, the separation need not persist in the code. 
    '''
    membership = models.ManyToManyField (IndividualPerformer, 
                                         related_name='combos')

                                      


class AudioInfo(models.Model):
    '''
    Information about the audio required for a particular Act
    '''
    title = models.CharField(max_length=128, blank=True)
    artist = models.CharField(max_length=123, blank=True)
    track = models.FileField(upload_to="uploads/audio", blank=True)
    duration = models.CharField(max_length=128,blank=True)  
    need_mic = models.BooleanField(default=False, blank=True)
    notes = models.TextField(blank=True)    

class LightingInfo(models.Model):
    '''
    Information about the lighting needs of a particular Act
    '''
    stage_color = models.CharField(max_length=25,
                                   choices=stage_lighting_options, blank=True)
    stage_second_color = models.CharField(max_length=25,
                                          choices=stage_lighting_options, blank=True)
    cyc_color = models.CharField(max_length='25', 
                                 choices=stage_lighting_options, blank=True)
    follow_spot = models.BooleanField(default=True)
    backlight = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

class PropsInfo(models.Model):
    '''
    Information about the props requirements for a particular Act
    '''
    set_props = models.BooleanField(default=True)
    clear_props = models.BooleanField(default=True)
    cue_props = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
                             
class TechInfo (models.Model):
    audio = models.OneToOneField(AudioInfo, blank=True)
    lighting = models.OneToOneField(LightingInfo, blank=True)
    props = models.OneToOneField(PropsInfo, blank=True)


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
    performer = models.ForeignKey(Performer)  # limit choices to the owner's Performers
    intro_text = models.TextField()
    tech = models.ForeignKey(TechInfo, blank = True)
    in_draft = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)
    accepted = models.IntegerField(choices=acceptance_states, default=0 )    

    def __str__ (self):
        return str(self.performer) + ": "+self.title


class Room(models.Model):
    '''
    A room at the expo center
    '''
    name = models.CharField(max_length=50)
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
    start_time = models.DateTimeField() # this won't last. Will have
                                        # to  implement some scheduling
    room = models.ForeignKey(Room)
    notes = models.TextField()  #internal notes about this event
    organizer = models.ManyToManyField(Profile)  # Perhaps should be
                                                 # more specific?
                                                
    def __str__(self):
        return self.title

class Show (Event):
    '''
    A Show is an Event consisting of a sequence of performances by Acts. 
    '''
    acts = models.ManyToManyField(Act, related_name="appearing_in")
    mc = models.ManyToManyField(Profile, related_name="mc_for")      
    
                                                
class Class (Event):
    '''
    A Class is an Event where one or a few people
    teach/instruct/guide/mediate and a number of participants
    spectate. Usually, there will be a limited space and
    pre-registration will be at least permitted and usually
    encourged. 
    '''
    teacher = models.ForeignKey(Performer)  # not all teachers will be
                                            # performers, but we're
                                            # going to want
                                            # performer-like info, so
                                            # let's make them
                                            # Performers. 
    
    registration = models.ManyToManyField(Profile)  # GBE attendees 
                                                    # may register for classes
    def __str__(self):
        return self.title
                                                    

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
    bid = models.ForeignKey(Bid)

class ActBid(Bid):
    '''
    An audition: a performer wants to perform in a show
    '''
    title = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=128, blank=True)
    is_group = models.CharField(max_length=20,
                                choices=yesno_options, default="No") 
    homepage = models.URLField(blank=True)
    other_performers = models.TextField(max_length = 500, blank=True)
    experience = models.CharField(max_length=60,
                                  choices=experience_options, default=3 )
    bio =  models.TextField(max_length = 500, blank=True)
    artist = models.CharField(max_length = 128, blank=True)
    song_name = models.CharField(max_length = 128, blank=True)
    act_length = models.TimeField(blank=True)
    description = models.TextField(max_length = 500, blank=True)  
    hotel_choice = models.CharField(max_length=20,
                                  choices=participate_options, default='Not Sure')
    volunteer_choice = models.CharField(max_length=20,
                                  choices=participate_options, default='Not Sure')
    conference_choice = models.CharField(max_length=20,
                                  choices=participate_options, default='Not Sure')
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.bidder.display_name+':  '+self.title;

class PerformerFestivals(models.Model):
    festival = models.CharField(max_length=20, choices=festival_list)
    experience = models.CharField(max_length=20,
                                  choices=festival_experience, default='No')
    actbid = models.ForeignKey(ActBid)


class ClassBid(Bid):
    '''
    A proposed class
    we can use this for all class-like items
    '''
						
    title = models.CharField(max_length=128, blank=True)
    organization = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=128, 
                            choices=class_options, 
                            blank=True, 
                            default="Lecture")
    homepage = models.URLField(blank=True)
    fee = models.IntegerField(blank=True, default=0)
    other_teachers = models.CharField(max_length=128, blank=True)
    description = models.TextField(max_length = 500, blank=True)  
    length_minutes = models.IntegerField(choices=length_options, 
                                         default=60)
    min_size = models.IntegerField(blank=True, default=1)
    max_size = models.IntegerField(blank=True, default=20)
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
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.type+':  '+self.title;


class ClassSchedule(models.Model):
    day = models.CharField(max_length=128, choices=day_options)
    time = models.CharField(max_length=128, choices=time_options)
    availability = models.CharField(max_length=128, choices=schedule_options)
    class_bid = models.ForeignKey(ClassBid)
    bidder = models.ForeignKey(Profile)

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
                
