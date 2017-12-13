from django.test import TestCase
from django.test import Client
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
)
from tests.factories.gbe_factories import ConferenceDayFactory
from tests.contexts import (
    ClassContext,
    ShowContext,
)
from post_office.models import Email
from django.core.management import call_command
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
import pytz
from gbe.scheduling.schedule_email import schedule_email


class TestSendDailySchedule(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_conference_day(self):
        num = schedule_email()
        self.assertEqual(0, num)

    def test_conf_day_no_receivers(self):
        ConferenceDayFactory(day=date.today() + timedelta(days=1))
        num = schedule_email()
        self.assertEqual(0, num)

    def test_send_to_teacher(self):
        start_time = datetime.combine(
            date.today() + timedelta(days=1),
            time(0, 0, 0, 0, tzinfo=pytz.utc))
        context = ClassContext(starttime=start_time)
        num = schedule_email()
        print context.sched_event.starttime
        print date.today() + timedelta(days=1)
        self.assertEqual(1, num)
