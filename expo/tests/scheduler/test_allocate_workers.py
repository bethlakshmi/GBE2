from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.contexts import StaffAreaContext # VolunteerContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)

class TestAllocateWorkers(TestCase):
    view_name = "allocate_workers"

    # def setUp(self):
    #     self.client = Client()
    #     self.staff_user = ProfileFactory()
    #     grant_privilege(self.staff_user, 'Scheduling Mavens')

    # def test_not_post(self):
    #     login_as(ProfileFactory(), self)
    #     url = reverse(self.view_name,
    #                   args=[1],
    #                   urlconf="scheduler.urls")
    #     response = self.client.get(url)
    #     self.assertEqual(404, response.status_code)

    # def test_post_form_not_valid_nonexistent_alloc_id(self):
    #     context = VolunteerContext()
    #     url = reverse(self.view_name,
    #                   args=[context.event.pk],
    #                   urlconf="scheduler.urls")
    #     data = {'worker': context.worker.id,
    #             'alloc_id': "invalid alloc_id",
    #             'role': 'Volunteer'}
    #     login_as(ProfileFactory(), self)
    #     response = self.client.post(url, data=data, follow=True)
    #     self.assertEqual(1,2)

    # def test_post_form_not_valid_good_alloc_id(self):
    #     context = VolunteerContext()
    #     url = reverse(self.view_name,
    #                   args=[context.event.pk],
    #                   urlconf="scheduler.urls")
    #     data = {'worker': "Ralph Kramden",
    #             'alloc_id': context.allocation.id,
    #             'role': 'Volunteer'}
    #     login_as(ProfileFactory(), self)
    #     response = self.client.post(url, data=data, follow=True)
    #     self.assertEqual(1,2)


    # def test_post_form_valid_delete_allocation(self):
    #     context = VolunteerContext()
    #     url = reverse(self.view_name,
    #                   args=[context.event.pk],
    #                   urlconf="scheduler.urls")
    #     data = {'worker': context.worker.id,
    #             'alloc_id': context.allocation.id,
    #             'role': 'Volunteer',
    #             'delete': 1}
    #     login_as(ProfileFactory(), self)
    #     response = self.client.post(url, data=data, follow=True)
    #     self.assertEqual(1,2)


    def test_post_form_valid_alloc_id_lt_zero(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        volunteer = ProfileFactory()
        url = reverse(self.view_name,
                      args=[volunteer_opp.pk],
                      urlconf="scheduler.urls")
        data = {'worker': volunteer.pk,
                'alloc_id': -1, # context.allocation.id,
                'role': 'Volunteer'}

        login_as(self.staff_user, self)
        response = self.client.post(url, data=data, follow=True)
        # self.assertEqual(1,2)

    # def test_post_form_valid_alloc_exists(self):

    #     context = StaffAreaContext()
    #     volunteer_opp = context.add_volunteer_opp()
    #     volunteer = ProfileFactory()
    #     url = reverse(self.view_name,
    #                   args=[volunteer_opp.pk],
    #                   urlconf="scheduler.urls")

    #     data = {'worker': volunteer.pk,
    #             'alloc_id': -1, # context.allocation.id,
    #             'role': 'Volunteer'}

    #     login_as(self.staff_user, self)
    #     import pdb; pdb.set_trace()
    #     response = self.client.post(url, data=data, follow=True)
    #     # self.assertEqual(1,2)
