from django.db import models
from django.contrib.auth.models import User

# Create your models here

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

class Profile(models.Model):
    '''
    The core data about any registered user of the GBE site, barring
    the information gathered up in the User object. (which we'll
    expose with properties, I suppose)
    '''
    user_object = models.ForeignKey(User) 
    display_name = models.CharField(max_length=128, blank=True) 
        # let's just let them enter a name if they want to badge as
        # something other than their proper name
    # contact info - I'd like to split this out to its own object
    # so we can do real validation 
    # but for now, let's just take what we get

    address1 = models.CharField(max_length=128)
    address2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=2) # should do a choice list 
                                           # here, I guess
    zip_code = models.CharField(max_length=10)  # allow for ext. ZIP
    country = models.CharField(max_length=128)
    phone = models.CharField(max_length=50)
    best_time = models.CharField(max_length=50, blank=True)
    how_heard = models.TextField(blank=True)
    

    # participant status
    # haven't really thought this bit through yet, could change
    # radically
    # note: these are not privileges. privs are managed through the
    # User object

    is_paid = models.BooleanField()
    is_volunteer = models.BooleanField()
    is_staff = models.BooleanField()
    is_performer = models.BooleanField()
    is_vendor = models.BooleanField()
    

class Bio (models.Model):
    '''
    A single performer, duo or small group, or a troupe.
    '''
    contact = models.ForeignKey(Profile)
    homepage = models.URLField(blank=True)
    bio = models.TextField()
    experience = models.IntegerField()
    awards = models.TextField(blank=True)
    hotel = models.BooleanField()
#    promo_image = models.ImageField(upload_to="uploads/images")
#    promo_video = models.FileField(upload_to="uploads/video", blank=True)

    

class AudioInfo(models.Model):
    '''
    Information about the audio required for a particular Act
    '''
    title = models.CharField(max_length=128)
    artist = models.CharField(max_length=123)
    track = models.FileField(upload_to="uploads/audio")
    duration = models.TextField(max_length=50)  
        # should write a DurationField for this to do it properly
    need_mic = models.BooleanField(default=False)
    notes = models.TextField()    

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

class LightingInfo(models.Model):
    '''
    Information about the lighting needs of a particular Act
    '''
    stage_color = models.CharField(max_length=25,
                                   choices=stage_lighting_options )
    stage_second_color = models.CharField(max_length=25,
                                          choices=stage_lighting_options)
    cyc_color = models.CharField(max_length='25', 
                                 choices=stage_lighting_options)
    follow_spot = models.BooleanField()
    backlight = models.BooleanField()
    notes = models.TextField()

class PropsInfo(models.Model):
    '''
    Information about the props requirements for a particular Act
    '''
    set_props = models.BooleanField()
    clear_props = models.BooleanField()
    cue_props = models.BooleanField()
    notes = models.TextField()
                             
class TechInfo (models.Model):
    audio = models.ForeignKey(AudioInfo)
    lighting = models.ForeignKey(LightingInfo)
    props = models.ForeignKey(PropsInfo)
    order = models.IntegerField()    

vote_options = ((1, "Strong yes"), (2, "Yes"), (3, "Weak Yes"), 
                (4, "No Comment"), (5, "Weak No"), (6, "No"), 
                (7, "Strong No"), (0, "Undecided"), (-1, "Author"))
    

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
    performer_bio = models.ForeignKey(Bio)
    duration = models.CharField(max_length=50)
    intro_text = models.TextField()
    tech = models.ForeignKey(TechInfo)
    performers = models.ManyToManyField(Profile)  # Perhaps should be



class Room(models.Model):
    '''
    A room at the expo center
    '''
    name = models.CharField(max_length=50)
    overbook_size = models.IntegerField()


    
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
    duration = models.IntegerField()  # for now, let's store this 
                                      # as good old half-hour blocks

    ## run-specific info, in case we decide to return to the run idea
    start_time = models.DateTimeField() # this won't last. Will have
                                        # to  implement some scheduling
    room = models.ForeignKey(Room)
    notes = models.TextField()  #internal notes about this event
    organizer = models.ManyToManyField(Profile)  # Perhaps should be
                                                 # more specific?


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
    teacher = models.ForeignKey(Bio)  # not all teachers will be
                                            # performers, but we're
                                            # going to want
                                            # performer-like info, so
                                            # let's make them
                                            # Performers. 
    
    registration = models.ManyToManyField(Profile)  # GBE attendees 
                                                    # may register for classes
    
class Bid(models.Model):
    '''
    A Bid is a proposal for an act, a class, a vendor, or whatnot.
    This is the abstract base for these various bids.
    '''
    bid_item = models.ForeignKey(Biddable)
    bidder = models.ForeignKey(Profile)
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


video_options = ((0, "I don't have any video of myself performing"), 
                 (1, "This is video of me but not the act I'm submitting"),
                 (2, "This is video of the act I would like to perform"))

participate_options = (('Yes', 'Yes'), ('No', 'No'), ('Not Sure', 'Not Sure'))
yesno_options = (("Yes", "Yes"), ("No", "No"))
experience_options = ((0, "I'm not a burlesque performer"),
                      (1, "Less than 1 year"),
                      (2,"1-2 years"),
                      (3,"3-4 years"),
                      (4,"5-6 years"),
                      (5,"more than 6 years"))
 
class ActBid(Bid):
    '''
    An audition: a performer wants to perform in a show
    '''
    title = models.CharField(max_length=128)
    name = models.CharField(max_length=128, blank=True)
    is_group = models.CharField(max_length=20,
                                choices=yesno_options, default="No") 
    homepage = models.URLField(blank=True)
    other_performers = models.TextField(max_length = 500, blank=True)
    experience = models.CharField(max_length=60,
                                  choices=experience_options, default=3 )
    bio =  models.CharField(max_length = 500)
    artist = models.CharField(max_length = 128, blank=True)
    song_name = models.CharField(max_length = 128, blank=True)
    act_length = models.CharField(max_length = 10)
    description = models.CharField(max_length = 128)  
    video_choice = models.CharField(max_length=60,
                                  choices=video_options, default=2 )
    video_link = models.CharField(max_length = 200, blank=True)
    promo_image = models.FileField(upload_to="uploads/images")
    hotel_choice = models.CharField(max_length=20,
                                  choices=participate_options, default='Not Sure')
    volunteer_choice = models.CharField(max_length=20,
                                  choices=participate_options, default='Not Sure')
    conference_choice = models.CharField(max_length=20,
                                  choices=participate_options, default='Not Sure')


class ClassBid(Bid):
    '''
    A proposed class
    Can we use this for all class-like items(panels, workshops, etc?)
    '''

    pass
class VendorBid(Bid):
    '''
    A request for a space in the marketplace.
    Vendors have to bid, too
    '''
    pass
