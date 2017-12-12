from django.test import TestCase
from django.test import Client
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
)
from tests.contexts.class_context import (
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


class TestScheduleSend(TestCase):
    def setUp(self):
        self.client = Client()
