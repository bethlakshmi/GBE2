from django.test import TestCase
from django.test import Client
from gbe.models import Conference
from post_office.models import Email
from django.core.management import call_command
from django.conf import settings


class TestSendDailySchedule(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"

    def setUp(self):
        self.client = Client()
        Email.objects.all().delete()
        Conference.objects.all().delete()

    def test_call_command(self):
        call_command("send_daily_schedule")
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)
