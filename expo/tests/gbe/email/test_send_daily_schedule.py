from django.test import TestCase
from django.test import Client
from tests.functions.gbe_functions import (
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
from django.conf import settings


class TestSendDailySchedule(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"

    def setUp(self):
        self.client = Client()
        Email.objects.all().delete()

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
        self.assertEqual(1, num)
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(context.bid.e_title in queued_email[0].html_message)
        self.assertTrue(context.teacher.user_object.email in queued_email[0].html_message)
