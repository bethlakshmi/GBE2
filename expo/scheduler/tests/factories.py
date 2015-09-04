import factory
from factory import DjangoModelFactory
from factory import SubFactory, RelatedFactory
import gbe.models as conf
import scheduler.models as sched
from gbe.duration import Duration
from django.utils.text import slugify
from datetime import datetime
from django.utils import timezone

class ConferenceFactory(DjangoModelFactory):
    class Meta:
        model = conf.Conference

    conference_name = factory.Sequence(lambda n: "Test Conference %d" % n)
    conference_slug = factory.Sequence(lambda n: u"test_conf %d" % n)
    accepting_bids = False

class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.WorkerItem


class UserFactory(DjangoModelFactory):
    class Meta:
        model = conf.User
    first_name = factory.Sequence(lambda n: 'John_%d' % n)
    last_name = 'Smith'
    username = factory.LazyAttribute(lambda a: "%s" % (a.first_name))
    email = '%s@smith.com' % username


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = conf.Profile
    user_object = SubFactory(UserFactory)
    address1 = '123 Main St.'
    address2 = factory.Sequence(lambda n: 'Apt. %d' % n)
    city = 'Smithville'
    state = 'MD'
    zip_code = '12345'
    country = 'USA'
    phone = '617-282-9268'
    display_name = factory.LazyAttribute(lambda a:
                                         "%s_%s" % (a.user_object.first_name,
                                                    a.user_object.last_name))


class ShowFactory(DjangoModelFactory):
    class Meta:
        model = conf.Show
    title = factory.Sequence(lambda n: 'Test Show%d' % n)
    description = 'Test Description'
    duration = Duration(hours=1)
    conference = SubFactory(ConferenceFactory)


class GenericEventFactory(DjangoModelFactory):
    class Meta:
        model = conf.GenericEvent

    type = 'Special'
    volunteer_category = 'VA0'
    conference = SubFactory(ConferenceFactory)
    

class PersonaFactory(DjangoModelFactory):
    class Meta:
        model = conf.Persona
    contact = SubFactory(ProfileFactory)
    performer_profile = factory.LazyAttribute(lambda a: a.contact)
    name = factory.Sequence(lambda n: 'Test Persona %d' % n)
    experience = 4

class AudioInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.AudioInfo

    track_title = factory.Sequence(lambda n: 'Test Track Title %d' % n)
    track_artist = factory.Sequence(lambda n: 'Test Track Artist %d' % n)
#  no track for now  - do we mock this, or what?
    track_duration = Duration(minutes=5)
    need_mic = True
    own_mic = False
    notes = "Notes about test AudioInfo object."
    confirm_no_music = False


class LightingInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.LightingInfo
    notes = "Notes field for test LightingInfo object."
    costume = "Costume field for test LightingInfo object."


class StageInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.StageInfo

    act_duration = Duration(minutes=5)
    intro_text = "intro text field for test StageInfo object"
    confirm = True
    set_props = False
    cue_props = False
    clear_props = False
    notes = "Notes field for test StageInfo object"


class TechInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.TechInfo

    audio = SubFactory(AudioInfoFactory)
    lighting = SubFactory(LightingInfoFactory)
    stage = SubFactory(StageInfoFactory)


class CueInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.CueInfo

    cue_sequence = 1
    cue_off_of = "cue_off_of field for test CueInfo object"
    follow_spot = "follow_spot"
    center_sport = "center_spot"
    backlight = "backlight"
    cyc_color = "WHITE"
    wash = "WHITE"
    sound_note = "sound_note field for test CueInfo object"


class ActFactory(DjangoModelFactory):
    class Meta:
        model = conf.Act

    performer = SubFactory(PersonaFactory)
    tech = SubFactory(TechInfoFactory)
    video_link = ""
    video_choice = ""
    shows_preferences = ""
    why_you = "why_you field for test Act"
    conference = RelatedFactory(ConferenceFactory)


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = conf.Room

    name = factory.Sequence(lambda x: "Test Room #%d" % x)
    capacity = 40
    overbook_size = 50
    

class EventFactory(DjangoModelFactory):
    class Meta:
        model = conf.Event

    title = factory.Sequence(lambda x: "Test Event #%d" % x)
    description = factory.LazyAttribute(lambda a:
                                        "Description for %s" % a.title)
    blurb = factory.LazyAttribute("Blurb for %s" % title)
    duration = Duration(hours=2)
    conference = SubFactory(ConferenceFactory)

class SchedEventFactory(DjangoModelFactory):
    class Meta:
        model = sched.Event

    eventitem = SubFactory(GenericEventFactory)
    starttime = timezone.make_aware(datetime(2016, 02, 4),
                                    timezone.get_current_timezone())


class ClassFactory(DjangoModelFactory):
    class Meta:
        model = conf.Class
    title = factory.Sequence(lambda x: "Test Class #%d" % x)
    teacher = SubFactory(PersonaFactory)
    minimum_enrollment = 1
    maximum_enrollment = 20
    organization = "Some Organization"
    type = "Lecture"
    fee = 0
    length_minutes = 60
    history = factory.LazyAttribute(
        lambda a: "History for test Class %s" % a.title)
    run_before = factory.LazyAttribute(
        lambda a:
        "run_before for test Class %s" % a.title)
    schedule_constraints = factory.LazyAttribute(
        lambda a: "schedule constraints for test Class %s" % a.title)
    space_needs = ''
    physical_restrictions = factory.LazyAttribute(
        lambda a: "physical restrictions for test Class %s" % a.title)
    multiple_run = 'No'
    conference = SubFactory(ConferenceFactory)


class BidEvaluationFactory(DjangoModelFactory):
    class Meta:
        model = conf.BidEvaluation

    evaluator = SubFactory(ProfileFactory)
    vote = 3
    notes = "Notes field for test BidEvaluation"
    bid = SubFactory(ActFactory)


class ProfilePreferencesFactory(DjangoModelFactory):
    class Meta:
        model = conf.ProfilePreferences

    profile = SubFactory(ProfileFactory)
    in_hotel = "No"
    inform_about = True
    show_hotel_infobox = True
