from django.test import TestCase
from django.test import Client
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
)
from gbetext import (
    acceptance_states,
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
)
from post_office.models import Email
from subprocess import check_output


class TestScheduleSend(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_conference_day(self):
        output = check_output(["python", "schedule_send.py"])
        print output
        self.assertTrue("0 schedule notifications sent." in output)
