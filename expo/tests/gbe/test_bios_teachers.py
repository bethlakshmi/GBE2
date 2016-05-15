import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ClassProposalFactory,
    ProfileFactory,
    PersonaFactory
)
from gbe.models import (
    Conference
)
from django.core.urlresolvers import reverse
from scheduler.models import Event as sEvent
from datetime import datetime, date, time
import pytz
from scheduler.models import (
    Worker,
    EventContainer
)
from tests.factories.scheduler_factories import ResourceAllocationFactory
from tests.functions.gbe_functions import login_as
from nt import skip


class TestBiosTeachers(TestCase):
    '''Tests for bios_teachers view'''
    view_name = 'bios_teacher'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_bios_teachers_authorized_user(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)

    @skip('test not working')
    def test_view_teachers_given_slug(self):
        '''/bios/teachers/ should return all teachers in the selected
        conference, given the conference slug in the get request'''
        conf = ConferenceFactory()
        other_conf = ConferenceFactory()
        this_class = ClassFactory(accepted=3,
                                  conference=conf,
                                  title="xyzzy")
        that_class = ClassFactory(accepted=3,
                                  conferenceother_conf,
                                  title="plugh")
        this_sched_class = sEvent(
            eventitem=this_class,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
        this_sched_class.save()
        worker = Worker(_item=this_class.teacher, role='Teacher')
        worker.save()
        this_class_assignment = ResourceAllocationFactory(
                event=this_sched_class,
                resource=worker
        )
        this_class_assignment.save()
        that_sched_class = sEvent(
            eventitem=that_class,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
        that_sched_class.save()
        that_worker = Worker(_item=that_class.teacher, role='Teacher')
        that_worker.save()
        that_class_assignment = ResourceAllocationFactory(
                event=that_sched_class,
                resource=that_worker
        )
        that_class_assignment.save()
        url = reverse(self.view_name, urlconf="gbe.urls")
        data = {"conference": conf.conference_slug}
        login_as(ProfileFactory(), self)
        response = self.client.get(url, data=data)
        nt.assert_true(this_class.title in response.content)
        nt.assert_false(that_class.title in response.content)

    @skip('test not working')
    def test_view_teachers_default_view_current_conf_exists(self):
        '''/bios/teachers/ should return all teachers in the current
        conference, assuming a current conference exists'''
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        other_conf = ConferenceFactory(status='completed')
        accepted_class = ClassFactory(accepted=3,
                                      conference=conf,
                                      title='accepted')
        previous_class = ClassFactory(accepted=3,
                                      conference=other_conf,
                                      title='previous')
        rejected_class = ClassFactory(accepted=1,
                                      conference=conf,
                                      title='reject')

        accepted_sched_class = sEvent(
            eventitem=accepted_class,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
        accepted_sched_class.save()
        worker = Worker(_item=accepted_class.teacher, role='Teacher')
        worker.save()
        accepted_class_assignment = ResourceAllocationFactory(
                event=accepted_sched_class,
                resource=worker
        )
        accepted_class_assignment.save()

        previous_sched_class = sEvent(
            eventitem=previous_class,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
        previous_sched_class.save()
        previous_worker = Worker(_item=previous_class.teacher, role='Teacher')
        previous_worker.save()
        previous_class_assignment = ResourceAllocationFactory(
                event=previous_sched_class,
                resource=previous_worker
        )
        previous_class_assignment.save()

        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_true(accepted_class.title in response.content)
        nt.assert_false(rejected_class.title in response.content)
        nt.assert_false(previous_class.title in response.content)
