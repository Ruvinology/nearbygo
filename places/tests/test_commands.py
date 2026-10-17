import shutil
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings

from places.models import Category, Place


class SeedCommandTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)

    def test_dr_07_seed_loads_ten_places_within_radius(self):
        call_command("seed_places", stdout=StringIO())
        self.assertEqual(Category.objects.count(), 5)
        self.assertEqual(Place.objects.count(), 10)
        self.assertEqual(Place.objects.public().count(), 10)
        self.assertEqual(
            Place.objects.get(slug="richmond-castle-kalutara").distance_km,
            Place.objects.get(slug="richmond-castle-kalutara").distance_km.__class__("12.8"),
        )
        self.assertFalse(Place.objects.filter(info_verified_on__isnull=False).exists())

    def test_seed_attaches_a_picture_with_alt_text_to_every_place(self):
        out = StringIO()
        call_command("seed_places", stdout=out)
        self.assertIn("Pictures added: 10.", out.getvalue())
        for place in Place.objects.all():
            self.assertTrue(place.image, place.name)
            self.assertTrue(place.image_alt.strip(), place.name)
            self.assertTrue(place.image.storage.exists(place.image.name), place.name)
            place.full_clean()

    def test_seed_adds_pictures_to_existing_places_without_changing_their_text(self):
        call_command("seed_places", stdout=StringIO())
        Place.objects.update(image="", image_alt="")
        Place.objects.filter(slug="panadura-beach").update(summary="Edited by admin.")
        out = StringIO()
        call_command("seed_places", stdout=out)
        self.assertIn("Pictures added: 10.", out.getvalue())
        beach = Place.objects.get(slug="panadura-beach")
        self.assertEqual(beach.summary, "Edited by admin.")
        self.assertTrue(beach.image)
        # A third run adds nothing new.
        out = StringIO()
        call_command("seed_places", stdout=out)
        self.assertIn("Pictures added: 0.", out.getvalue())

    def test_seed_is_idempotent_and_keeps_admin_edits(self):
        call_command("seed_places", stdout=StringIO())
        Place.objects.filter(slug="panadura-beach").update(summary="Edited by admin.")
        call_command("seed_places", stdout=StringIO())
        self.assertEqual(Place.objects.count(), 10)
        self.assertEqual(Place.objects.get(slug="panadura-beach").summary, "Edited by admin.")

    def test_card_and_detail_show_the_picture(self):
        call_command("seed_places", stdout=StringIO())
        beach = Place.objects.get(slug="panadura-beach")
        r = self.client.get("/")
        self.assertContains(r, beach.image.url)
        self.assertContains(r, 'alt="The sun setting over the sea at Panadura Beach')
        r = self.client.get(beach.get_absolute_url())
        self.assertContains(r, beach.image.url)
        self.assertContains(r, "<figcaption>AI-generated illustration</figcaption>", html=True)

    def test_check_radius_command(self):
        call_command("seed_places", stdout=StringIO())
        out = StringIO()
        call_command("check_radius", stdout=out)
        self.assertIn("All active places pass the radius check.", out.getvalue())


class CleanupPlansTests(TestCase):
    def test_cleanup_removes_plans_without_live_session(self):
        from planner.models import VisitPlan

        VisitPlan.objects.create(session_key="expired-session-key")
        out = StringIO()
        call_command("cleanup_plans", stdout=out)
        self.assertEqual(VisitPlan.objects.count(), 0)
        self.assertIn("Deleted 1", out.getvalue())
