from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from django.test import (
    Client,
    TestCase,
)
from tests.contexts import ActTechInfoContext
from gbe.models import Conference
from scheduler.models import EventItem
from tests.functions.gbe_functions import (
    bad_id_for,
    login_as,
    set_image,
)
from django.contrib.auth.models import User


class TestDetailView(TestCase):
    view_name = 'detail_view'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.context = ActTechInfoContext()
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.show.pk])

    def test_no_permission_required(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.context.show.e_title)

    def test_bad_id_raises_404(self):
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[bad_id_for(EventItem)])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)

    def test_repeated_lead_shows_once(self):
        show = ShowFactory()
        sched_events = [
            SchedEventFactory.create(
                eventitem=show.eventitem_ptr) for i in range(2)]
        staff_lead = ProfileFactory()
        lead_worker = WorkerFactory(_item=staff_lead.workeritem_ptr,
                                    role="Staff Lead")
        for se in sched_events:
            ResourceAllocationFactory.create(event=se,
                                             resource=lead_worker)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[show.pk]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.content.count(staff_lead.display_name))

    def test_bio_grid(self):
        self.context.performer.homepage = "www.testhomepage.com"
        self.context.performer.save()
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.context.performer.homepage)

    def test_feature_performers(self):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted By...")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.show.pk])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, context.performer.name)
        self.assertContains(response, "Hosted By...")

    def test_bio_grid_for_admin(self):
        superuser = User.objects.create_superuser('test_bio_grid_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        login_as(superuser, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/gbe/performer/%d" % self.context.performer.pk)

    def test_feature_grid_for_admin(self):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted By...")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.show.pk])
        superuser = User.objects.create_superuser('test_feature_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        set_image(context.performer)
        login_as(superuser, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/gbe/performer/%d" % context.performer.pk)

    def test_bio_grid_for_admin_w_image(self):
        superuser = User.objects.create_superuser('test_bio_grid_img_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        login_as(superuser, self)
        set_image(self.context.performer)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/filer/image/%d/?_pick=file&_popup=1" % (
                self.context.performer.img.pk))

    def test_feature_grid_for_admin_w_image(self):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted By...")
        set_image(context.performer)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.show.pk])
        superuser = User.objects.create_superuser('test_feature_img_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        login_as(superuser, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/filer/image/%d/?_pick=file&_popup=1" % (
                context.performer.img.pk))
