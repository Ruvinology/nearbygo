"""Model and validation tests. Requirement IDs refer to the NearbyGo SRS v1.0."""

import time
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase, override_settings

from places import geo
from places.models import Category, Place

from .factories import make_category, make_place


def with_reference(lat, lng):
    config = dict(settings.NEARBYGO, REFERENCE_LAT=lat, REFERENCE_LNG=lng)
    return override_settings(NEARBYGO=config)


class GeoTests(TestCase):
    def test_haversine_known_distance(self):
        # Panadura town centre to Kalutara Bodhiya is roughly 15 km in a straight line.
        d = geo.haversine_km(6.7133, 79.9042, 6.5869, 79.9603)
        self.assertAlmostEqual(d, 15.3, delta=0.3)

    def test_haversine_zero(self):
        self.assertAlmostEqual(geo.haversine_km(6.7, 79.9, 6.7, 79.9), 0.0)

    def test_reference_not_configured_returns_none(self):
        with with_reference(None, None):
            self.assertIsNone(geo.distance_from_reference_km(6.7, 79.9))


class PlaceValidationTests(TestCase):
    def setUp(self):
        self.category = make_category(name="Beaches", slug="beaches")

    def build(self, **kwargs):
        data = {
            "name": "Test Beach",
            "category": self.category,
            "summary": "A beach.",
            "description": "A long beach.",
            "latitude": Decimal("6.7"),
            "longitude": Decimal("79.9"),
            "distance_km": Decimal("3.0"),
            "is_active": True,
        }
        data.update(kwargs)
        return Place(**data)

    def test_fr_ad_05_required_fields(self):
        """FR-AD-05: name, category, description, coordinates and distance are required."""
        place = Place()
        with self.assertRaises(ValidationError) as ctx:
            place.full_clean()
        for field in ("name", "category", "summary", "description", "latitude", "longitude", "distance_km"):
            self.assertIn(field, ctx.exception.message_dict)

    def test_fr_ad_05_non_negative_distance(self):
        with self.assertRaises(ValidationError) as ctx:
            self.build(distance_km=Decimal("-1")).full_clean()
        self.assertIn("distance_km", ctx.exception.message_dict)

    def test_fr_ad_05_dr_04_unique_name_ignores_case(self):
        """FR-AD-05 / DR-04: names are unique regardless of letter case."""
        self.build().save()
        duplicate = self.build(name="TEST beach")
        with self.assertRaises(ValidationError) as ctx:
            duplicate.full_clean()
        self.assertIn("name", ctx.exception.message_dict)

    def test_fr_ad_06_latitude_range(self):
        for bad in ("-90.5", "90.1"):
            with self.subTest(lat=bad), self.assertRaises(ValidationError) as ctx:
                self.build(latitude=Decimal(bad)).full_clean()
            self.assertIn("latitude", ctx.exception.message_dict)

    def test_fr_ad_06_longitude_range(self):
        for bad in ("-180.5", "180.1"):
            with self.subTest(lng=bad), self.assertRaises(ValidationError) as ctx:
                self.build(longitude=Decimal(bad)).full_clean()
            self.assertIn("longitude", ctx.exception.message_dict)

    def test_fr_ad_06_boundary_values_accepted(self):
        with with_reference(None, None):
            self.build(latitude=Decimal("-90"), longitude=Decimal("180")).full_clean()

    def test_fr_ad_07_active_place_over_radius_rejected(self):
        """FR-AD-07 / BR-01: an active place cannot be more than 25 km away."""
        with self.assertRaises(ValidationError) as ctx:
            self.build(distance_km=Decimal("25.1")).full_clean()
        self.assertIn("distance_km", ctx.exception.message_dict)

    def test_fr_ad_07_exactly_on_radius_accepted(self):
        self.build(distance_km=Decimal("25.0")).full_clean()

    def test_fr_ad_07_inactive_place_over_radius_can_be_saved(self):
        self.build(distance_km=Decimal("40.0"), is_active=False).full_clean()

    def test_fr_ad_07_coordinates_checked_against_private_reference(self):
        """When the reference point is configured, coordinates outside the radius are refused."""
        with with_reference(6.7133, 79.9042):
            far = self.build(latitude=Decimal("6.9271"), longitude=Decimal("79.8612"), distance_km=Decimal("20"))  # Colombo Fort, ~24 km
            far.full_clean()  # inside
            too_far = self.build(name="Far", latitude=Decimal("7.2906"), longitude=Decimal("80.6337"))  # Kandy
            with self.assertRaises(ValidationError) as ctx:
                too_far.full_clean()
            self.assertIn("latitude", ctx.exception.message_dict)
            self.assertNotIn("6.7133", str(ctx.exception))  # NFR-SE-07: reference never echoed

    def test_nfr_qa_02_image_requires_alt_text(self):
        place = self.build(image="places/example.jpg", image_alt="")
        with self.assertRaises(ValidationError) as ctx:
            place.full_clean()
        self.assertIn("image_alt", ctx.exception.message_dict)

    def test_fr_ad_09_timestamps(self):
        """FR-AD-09: created and last-updated timestamps are recorded."""
        place = self.build()
        place.save()
        self.assertIsNotNone(place.created_at)
        first_update = place.updated_at
        time.sleep(0.01)
        place.summary = "Changed."
        place.save()
        place.refresh_from_db()
        self.assertGreaterEqual(place.updated_at, first_update)
        self.assertLessEqual(place.created_at, place.updated_at)

    def test_slug_generated_and_unique(self):
        a = self.build(name="Lake View")
        a.save()
        self.assertEqual(a.slug, "lake-view")
        b = self.build(name="Lake  View!")
        b.save()
        self.assertEqual(b.slug, "lake-view-2")

    def test_unicode_names_supported(self):
        """OR-02: Unicode text is stored, ready for Sinhala and Tamil content."""
        place = self.build(name="රන්කොත් විහාරය")
        place.save()
        place.refresh_from_db()
        self.assertEqual(place.name, "රන්කොත් විහාරය")


class CategoryTests(TestCase):
    def test_dr_04_category_name_unique_ignoring_case(self):
        make_category(name="Nature", slug="nature")
        with self.assertRaises(ValidationError):
            Category(name="NATURE").full_clean()

    def test_dr_05_category_with_places_cannot_be_deleted(self):
        """DR-05 / SRS 4.6.2: deleting a category in use is prevented."""
        category = make_category()
        make_place(category=category)
        with self.assertRaises(ProtectedError):
            category.delete()

    def test_public_queryset_rules(self):
        """FR-PL-04, BR-01, BR-03: only active places in active categories within the radius are public."""
        live = make_category()
        hidden = make_category(is_active=False)
        visible = make_place(category=live)
        make_place(category=live, is_active=False)
        make_place(category=hidden)
        Place.objects.filter(pk=make_place(category=live).pk).update(distance_km=Decimal("30"))  # bypasses validation
        self.assertEqual(list(Place.objects.public()), [visible])
