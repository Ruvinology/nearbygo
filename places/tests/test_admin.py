"""Administrator authentication and content management (SRS 4.6, 5.3)."""

import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from places.middleware import LAST_ACTIVITY_KEY
from places.models import Category, Place

from .factories import make_category, make_place

PASSWORD = "Str0ng-Test-Passw0rd!"


class AdminTestCase(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("admin", "admin@example.com", PASSWORD)
        self.category = make_category(name="Beaches", slug="beaches")

    def login(self):
        self.assertTrue(self.client.login(username="admin", password=PASSWORD))


class AuthenticationTests(AdminTestCase):
    def test_fr_ad_01_nfr_se_01_login_required(self):
        for url in (reverse("admin:index"), reverse("admin:places_place_changelist"), reverse("admin:places_place_add")):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302)
            self.assertIn(reverse("admin:login"), r["Location"])

    def test_fr_ad_02_invalid_credentials_generic_message(self):
        wrong_password = self.client.post(reverse("admin:login"), {"username": "admin", "password": "nope", "next": "/admin/"})
        unknown_user = self.client.post(reverse("admin:login"), {"username": "ghost", "password": "nope", "next": "/admin/"})
        self.assertEqual(wrong_password.status_code, 200)
        self.assertEqual(
            wrong_password.context["form"].non_field_errors(),
            unknown_user.context["form"].non_field_errors(),
        )
        self.assertNotContains(unknown_user, "does not exist")

    def test_nfr_se_02_password_hashed(self):
        stored = get_user_model().objects.get(username="admin").password
        self.assertNotIn(PASSWORD, stored)
        self.assertTrue(stored.startswith(("pbkdf2_sha256$", "argon2", "bcrypt", "scrypt")))

    def test_non_staff_user_cannot_use_admin(self):
        get_user_model().objects.create_user("visitor", password=PASSWORD)
        self.client.login(username="visitor", password=PASSWORD)
        r = self.client.get(reverse("admin:places_place_changelist"))
        self.assertEqual(r.status_code, 302)

    def test_fr_ad_10_sign_out_invalidates_session(self):
        self.login()
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)
        self.client.post(reverse("admin:logout"))
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)

    @override_settings(ADMIN_IDLE_TIMEOUT=60)
    def test_nfr_se_08_idle_timeout(self):
        self.login()
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)
        session = self.client.session
        session[LAST_ACTIVITY_KEY] = int(time.time()) - 120
        session.save()
        r = self.client.get(reverse("admin:index"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("admin:login"), r["Location"])
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)

    def test_nfr_se_03_admin_forms_use_csrf(self):
        self.login()
        r = self.client.get(reverse("admin:places_place_add"))
        self.assertContains(r, "csrfmiddlewaretoken")


class ContentManagementTests(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.login()

    def place_form(self, **overrides):
        data = {
            "name": "Admin Beach",
            "slug": "",
            "category": self.category.pk,
            "is_active": "on",
            "summary": "Added by an administrator.",
            "description": "Long description.",
            "latitude": "6.700000",
            "longitude": "79.900000",
            "distance_km": "3.5",
            "opening_hours": "",
            "entrance_fee": "",
            "visit_duration_minutes": "60",
            "best_time_to_visit": "",
            "toilets": "unknown",
            "parking": "unknown",
            "seating": "unknown",
            "food": "unknown",
            "facilities_notes": "",
            "accessibility": "",
            "transport": "",
            "family_suitability": "",
            "student_discount": "",
            "travel_tips": "",
            "image_alt": "",
            "image_credit": "",
            "info_verified_on": "",
        }
        data.update(overrides)
        return data

    def test_fr_ad_03_category_create_edit_delete(self):
        r = self.client.post(reverse("admin:places_category_add"), {
            "name": "Museums", "slug": "museums", "description": "", "colour": "indigo", "icon": "easel",
            "display_order": "3", "is_active": "on",
        })
        self.assertEqual(r.status_code, 302)
        museums = Category.objects.get(slug="museums")
        r = self.client.post(reverse("admin:places_category_change", args=[museums.pk]), {
            "name": "Museums and galleries", "slug": "museums", "description": "", "colour": "indigo", "icon": "easel",
            "display_order": "3", "is_active": "on",
        })
        self.assertEqual(r.status_code, 302)
        museums.refresh_from_db()
        self.assertEqual(museums.name, "Museums and galleries")
        r = self.client.post(reverse("admin:places_category_delete", args=[museums.pk]), {"post": "yes"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Category.objects.filter(pk=museums.pk).exists())

    def test_fr_ad_04_place_create_and_edit(self):
        r = self.client.post(reverse("admin:places_place_add"), self.place_form())
        self.assertEqual(r.status_code, 302, r.content[:2000])
        place = Place.objects.get(name="Admin Beach")
        self.assertEqual(place.slug, "admin-beach")
        r = self.client.post(reverse("admin:places_place_change", args=[place.pk]), self.place_form(slug="admin-beach", summary="Updated."))
        self.assertEqual(r.status_code, 302)
        place.refresh_from_db()
        self.assertEqual(place.summary, "Updated.")

    def test_fr_ad_04_activate_and_deactivate_actions(self):
        place = make_place(category=self.category, is_active=True)
        url = reverse("admin:places_place_changelist")
        self.client.post(url, {"action": "make_inactive", "_selected_action": [place.pk]})
        place.refresh_from_db()
        self.assertFalse(place.is_active)
        self.client.post(url, {"action": "make_active", "_selected_action": [place.pk]})
        place.refresh_from_db()
        self.assertTrue(place.is_active)

    def test_fr_ad_07_activate_action_refuses_place_outside_radius(self):
        place = make_place(category=self.category, is_active=False, distance_km=Decimal("30"))
        r = self.client.post(
            reverse("admin:places_place_changelist"),
            {"action": "make_active", "_selected_action": [place.pk]},
            follow=True,
        )
        place.refresh_from_db()
        self.assertFalse(place.is_active)
        self.assertContains(r, "Not activated")

    def test_fr_ad_07_admin_form_rejects_over_radius(self):
        r = self.client.post(reverse("admin:places_place_add"), self.place_form(distance_km="26"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Only places within 25 km can be active")
        self.assertFalse(Place.objects.filter(name="Admin Beach").exists())

    def test_ir_ui_04_field_error_messages(self):
        r = self.client.post(reverse("admin:places_place_add"), self.place_form(name="", latitude="95"))
        self.assertContains(r, "This field is required")
        self.assertContains(r, "less than or equal to 90")

    def test_fr_ad_08_delete_requires_confirmation(self):
        place = make_place(category=self.category)
        r = self.client.get(reverse("admin:places_place_delete", args=[place.pk]))
        self.assertContains(r, "Are you sure")
        self.assertTrue(Place.objects.filter(pk=place.pk).exists())
        self.client.post(reverse("admin:places_place_delete", args=[place.pk]), {"post": "yes"})
        self.assertFalse(Place.objects.filter(pk=place.pk).exists())

    def test_category_in_use_cannot_be_deleted_from_admin(self):
        make_place(category=self.category)
        r = self.client.get(reverse("admin:places_category_delete", args=[self.category.pk]))
        self.assertContains(r, "would require deleting the following protected related objects")

    def test_nfr_sa_03_deactivation_hides_immediately(self):
        place = make_place(category=self.category, name="Unsafe Rocks")
        self.assertContains(self.client.get(reverse("places:list")), "Unsafe Rocks")
        self.client.post(reverse("admin:places_place_changelist"), {"action": "make_inactive", "_selected_action": [place.pk]})
        self.assertNotContains(self.client.get(reverse("places:list")), "Unsafe Rocks")

    def test_radius_check_message_without_reference(self):
        place = make_place(category=self.category)
        r = self.client.get(reverse("admin:places_place_change", args=[place.pk]))
        self.assertContains(r, "Reference location not configured")
