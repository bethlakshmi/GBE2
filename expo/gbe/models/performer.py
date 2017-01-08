from model_utils.managers import InheritanceManager

from django.db.models import (
    ForeignKey,
    CharField,
    PositiveIntegerField,
    TextField,
    URLField,
    FileField,
)
from gbe.models import Profile
from scheduler.models import WorkerItem


class Performer (WorkerItem):
    '''
    Abstract base class for any solo, group, or troupe - anything that
    can appear in a show lineup or teach a class
    The fields are named as we would name them for a single performer.
    In all cases, when applied to an aggregate (group or troup) they
    apply to the aggregate as a whole. The Boston Baby Dolls DO NOT
    list awards won by members of the troupe, only those won by the
    troup. (individuals can list their own, and these can roll up if
    we want). Likewise, the bio of the Baby Dolls is the bio of the
    company, not of the members, and so forth.
    '''
    objects = InheritanceManager()
    contact = ForeignKey(Profile, related_name='contact')
    name = CharField(max_length=100,     # How this Performer is listed
                     unique=True)        # in a playbill.
    homepage = URLField(blank=True)
    bio = TextField()
    experience = PositiveIntegerField()       # in years
    awards = TextField(blank=True)
    promo_image = FileField(upload_to="uploads/images",
                            blank=True)
    festivals = TextField(blank=True)     # placeholder only

    # looks dead -jpk
    # def append_alerts(self, alerts):
    #     '''
    #     Find any alerts generated by this object's data and append them
    #     to the alerts dict presented as a parameter
    #     '''
    #     return alerts

    def get_promo_image_sizes(self, size):
        '''
        gets the URL for images that have been sized specifically to
        suit GBE layouts
            mini = the size for show/act and fashion fair grids - height = 125p
            thumb = the size for the /gbe page -  height 75-100p
        There is a timebased script that minifies uploaded images in these
        two formats
        '''
        resized = None
        if self.promo_image:
            pieces = self.promo_image.name.split('/')
            pieces.insert(-1, size)
            resized = '/'.join(pieces)
        return resized

    @property
    def promo_mini(self):
        return self.get_promo_image_sizes('mini')

    @property
    def promo_thumb(self):
        return self.get_promo_image_sizes('thumb')

    def get_schedule(self):
        return Performer.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).get_schedule()

    def get_profiles(self):
        '''
        Gets all of the people performing in the act
        '''
        return Performer.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).get_profiles()

    @property
    def contact_email(self):
        return self.contact.user_object.email

    @property
    def contact_phone(self):
        return self.contact.phone

    @property
    def complete(self):
        return True

    @property
    def describe(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        app_label = "gbe"