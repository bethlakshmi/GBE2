from django.db.models import ManyToManyField
from gbe.models import (
    Performer,
    Persona,
)

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
    membership = ManyToManyField(Persona,
                                 related_name='troupes')

    '''
        Gets all of the people performing in the act.
        For troupe, that is every profile of every member in membership
    '''
    def get_profiles(self):
        profiles = []
        for member in Persona.objects.filter(troupes=self):
            profiles += member.get_profiles()
        return profiles

    def get_schedule(self):
        return []

    def append_alerts(self, alerts):
        '''
        Find any alerts generated by this object's data and append them
        to the alerts dict presented as a parameter
        '''
        alerts = super(Troupe, self).append_alerts()
        return alerts

    class Meta:
        app_label = "gbe"
