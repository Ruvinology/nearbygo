"""One-day visit plan tests (SRS 4.5, BR-04, BR-05, DR-06)."""


from django.test import Client, TestCase
from django.urls import reverse

from places.tests.factories import make_category, make_place
from planner import services
from planner.models import PlanItem, VisitPlan


class PlanTestCase(TestCase):
    def setUp(self):
        category = make_category(name="Beaches", slug="beaches")
        self.a = make_place(category=category, name="Alpha Beach", visit_duration_minutes=60)
        self.b = make_place(category=category, name="Bravo Lake", visit_duration_minutes=90)
        self.c = make_place(category=category, name="Charlie Temple", visit_duration_minutes=None)

    def add(self, place, client=None, follow=False, **extra):
        return (client or self.client).post(reverse("planner:add"), {"place_id": place.pk, **extra}, follow=follow)

    def names_in_order(self):
        plan = VisitPlan.objects.get()
        return list(plan.items.order_by("visit_order").values_list("place__name", flat=True))

    def item(self, place):
        return PlanItem.objects.get(place=place)


class AddRemoveTests(PlanTestCase):
    def test_fr_vp_01_add_place(self):
        r = self.add(self.a, next=self.a.get_absolute_url())
        self.assertRedirects(r, self.a.get_absolute_url())
        self.assertEqual(self.names_in_order(), ["Alpha Beach"])
        r = self.client.get(reverse("planner:plan"))
        self.assertContains(r, "Alpha Beach")

    def test_fr_vp_01_confirmation_message(self):
        r = self.add(self.a, follow=True)
        self.assertContains(r, "Added Alpha Beach to your plan.")

    def test_fr_vp_02_br_04_no_duplicates(self):
        self.add(self.a)
        r = self.client.post(reverse("planner:add"), {"place_id": self.a.pk}, follow=True)
        self.assertContains(r, "Alpha Beach is already in your plan.")
        self.assertEqual(PlanItem.objects.count(), 1)

    def test_fr_vp_01_inactive_place_cannot_be_added(self):
        self.a.is_active = False
        self.a.save()
        self.assertEqual(self.add(self.a).status_code, 404)
        self.assertEqual(PlanItem.objects.count(), 0)

    def test_add_requires_post(self):
        self.assertEqual(self.client.get(reverse("planner:add")).status_code, 405)

    def test_invalid_place_id_returns_404(self):
        self.assertEqual(self.client.post(reverse("planner:add"), {"place_id": "abc"}).status_code, 404)

    def test_fr_vp_03_numbered_order(self):
        for p in (self.a, self.b, self.c):
            self.add(p)
        r = self.client.get(reverse("planner:plan"))
        self.assertContains(r, "Stop 1: ")
        self.assertContains(r, "Stop 3: ")
        self.assertEqual([i.visit_order for i in PlanItem.objects.order_by("visit_order")], [1, 2, 3])

    def test_fr_vp_04_remove(self):
        for p in (self.a, self.b, self.c):
            self.add(p)
        self.client.post(reverse("planner:remove", args=[self.item(self.b).pk]))
        self.assertEqual(self.names_in_order(), ["Alpha Beach", "Charlie Temple"])
        self.assertEqual([i.visit_order for i in PlanItem.objects.order_by("visit_order")], [1, 2])

    def test_cannot_remove_another_visitors_item(self):
        other = Client()
        self.add(self.a, client=other)
        item = PlanItem.objects.get()
        self.add(self.b)  # gives this client its own plan
        r = self.client.post(reverse("planner:remove", args=[item.pk]), follow=True)
        self.assertContains(r, "That place is not in your plan.")
        self.assertTrue(PlanItem.objects.filter(pk=item.pk).exists())

    def test_open_redirect_blocked(self):
        r = self.add(self.a, next="https://evil.example.com/")
        self.assertRedirects(r, self.a.get_absolute_url(), fetch_redirect_response=False)

    def test_plan_size_limit(self):
        category = make_category()
        plan = services.get_plan(self._request_with_session(), create=True)
        for _ in range(services.MAX_PLAN_ITEMS):
            services.add_place(plan, make_place(category=category))
        with self.assertRaises(services.PlanFullError):
            services.add_place(plan, make_place(category=category))

    def _request_with_session(self):
        from django.contrib.sessions.backends.db import SessionStore
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.session = SessionStore()
        return request


class OrderTests(PlanTestCase):
    def setUp(self):
        super().setUp()
        for p in (self.a, self.b, self.c):
            self.add(p)

    def test_fr_vp_05_move_earlier(self):
        self.client.post(reverse("planner:move", args=[self.item(self.c).pk]), {"direction": "up"})
        self.assertEqual(self.names_in_order(), ["Alpha Beach", "Charlie Temple", "Bravo Lake"])

    def test_fr_vp_05_move_later(self):
        self.client.post(reverse("planner:move", args=[self.item(self.a).pk]), {"direction": "down"})
        self.assertEqual(self.names_in_order(), ["Bravo Lake", "Alpha Beach", "Charlie Temple"])

    def test_fr_vp_05_first_cannot_move_up(self):
        self.client.post(reverse("planner:move", args=[self.item(self.a).pk]), {"direction": "up"})
        self.assertEqual(self.names_in_order(), ["Alpha Beach", "Bravo Lake", "Charlie Temple"])

    def test_fr_vp_05_invalid_direction(self):
        r = self.client.post(reverse("planner:move", args=[self.item(self.a).pk]), {"direction": "sideways"}, follow=True)
        self.assertContains(r, "That change could not be made")
        self.assertEqual(self.names_in_order(), ["Alpha Beach", "Bravo Lake", "Charlie Temple"])

    def test_fr_vp_06_distance_and_duration_shown(self):
        r = self.client.get(reverse("planner:plan"))
        self.assertContains(r, "5.0 km from Panadura")
        self.assertContains(r, "Allow 1 h 30 min")
        self.assertContains(r, "Visit time not available")
        self.assertContains(r, "about 2 h 30 min of visiting time")

    def test_planned_time(self):
        item = self.item(self.a)
        self.client.post(reverse("planner:set_time", args=[item.pk]), {"planned_time": "09:30"})
        item.refresh_from_db()
        self.assertEqual(item.planned_time.strftime("%H:%M"), "09:30")
        r = self.client.post(reverse("planner:set_time", args=[item.pk]), {"planned_time": "late"}, follow=True)
        self.assertContains(r, "Enter the time as hours and minutes")

    def test_fr_vp_07_plan_kept_for_session(self):
        self.client.get(reverse("places:list"))
        r = self.client.get(reverse("planner:plan"))
        self.assertEqual(len(r.context["items"]), 3)
        self.assertEqual(r.context["plan_count"], 3)
        # A different browser has its own empty plan.
        r = Client().get(reverse("planner:plan"))
        self.assertEqual(len(r.context["items"]), 0)

    def test_fr_vp_08_clear_asks_for_confirmation(self):
        r = self.client.get(reverse("planner:clear"))
        self.assertContains(r, "Clear your plan?")
        self.assertEqual(PlanItem.objects.count(), 3)
        r = self.client.post(reverse("planner:clear"), follow=True)
        self.assertContains(r, "Your plan is now empty.")
        self.assertEqual(PlanItem.objects.count(), 0)

    def test_fr_vp_09_guidance_notice(self):
        r = self.client.get(reverse("planner:plan"))
        self.assertContains(r, "This plan is a guide")
        self.assertContains(r, "does not plan routes, check live traffic")

    def test_br_05_no_booking_or_payment_controls(self):
        r = self.client.get(reverse("planner:plan")).content.decode().lower()
        for word in ("pay now", "book now", "checkout", "buy ticket"):
            self.assertNotIn(word, r)

    def test_deactivated_place_removed_from_plan(self):
        self.b.is_active = False
        self.b.save()
        r = self.client.get(reverse("planner:plan"))
        self.assertContains(r, "One place in your plan is no longer listed")
        self.assertEqual(self.names_in_order(), ["Alpha Beach", "Charlie Temple"])

    def test_plan_markers_numbered(self):
        r = self.client.get(reverse("planner:plan"))
        self.assertEqual([m["order"] for m in r.context["markers"]], [1, 2, 3])


class EmptyPlanTests(PlanTestCase):
    def test_ir_ui_05_empty_plan_message(self):
        r = self.client.get(reverse("planner:plan"))
        self.assertContains(r, "Your plan is empty")
        self.assertEqual(VisitPlan.objects.count(), 0)  # visiting the page does not create a plan

    def test_or_05_no_personal_data_collected(self):
        self.add(self.a)
        plan = VisitPlan.objects.get()
        fields = {f.name for f in VisitPlan._meta.get_fields()}
        self.assertEqual(fields, {"id", "session_key", "created_at", "updated_at", "items"})
        self.assertTrue(plan.session_key)


class CsrfTests(PlanTestCase):
    def test_nfr_se_03_csrf_enforced(self):
        client = Client(enforce_csrf_checks=True)
        r = client.post(reverse("planner:add"), {"place_id": self.a.pk})
        self.assertEqual(r.status_code, 403)
