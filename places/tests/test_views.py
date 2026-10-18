"""Public visitor page tests (SRS 4.1 to 4.4, Section 5)."""

import json
import time
from decimal import Decimal

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from places.models import Place

from .factories import make_category, make_place


class BrowseTests(TestCase):
    def setUp(self):
        self.beach = make_category(name="Beaches", slug="beaches")
        self.temple = make_category(name="Temples", slug="temples")
        self.a = make_place(category=self.beach, name="Sunny Beach", summary="Golden sand.", distance_km=Decimal("2.6"))
        self.b = make_place(category=self.temple, name="Old Temple", distance_km=Decimal("1.9"))
        self.hidden = make_place(category=self.beach, name="Closed Cove", is_active=False)

    def test_fr_pl_01_lists_active_places(self):
        r = self.client.get(reverse("places:list"))
        self.assertContains(r, "Sunny Beach")
        self.assertContains(r, "Old Temple")

    def test_fr_pl_02_summary_fields(self):
        """FR-PL-02: name, category, approximate distance and short description."""
        r = self.client.get(reverse("places:list"))
        self.assertContains(r, "Golden sand.")
        self.assertContains(r, "2.6 km")
        self.assertContains(r, "Beaches")

    def test_fr_pl_03_link_to_details(self):
        r = self.client.get(reverse("places:list"))
        self.assertContains(r, self.a.get_absolute_url())

    def test_fr_pl_04_inactive_hidden(self):
        r = self.client.get(reverse("places:list"))
        self.assertNotContains(r, "Closed Cove")

    def test_fr_pl_05_empty_state(self):
        Place.objects.update(is_active=False)
        r = self.client.get(reverse("places:list"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "No places are listed yet")

    def test_br_03_inactive_category_hides_its_places(self):
        self.temple.is_active = False
        self.temple.save()
        r = self.client.get(reverse("places:list"))
        self.assertNotContains(r, "Old Temple")
        self.assertNotContains(r, ">Temples<")

    def test_ir_com_02_utf8(self):
        r = self.client.get(reverse("places:list"))
        self.assertIn("charset=utf-8", r["Content-Type"])


class FilterTests(TestCase):
    def setUp(self):
        self.beach = make_category(name="Beaches", slug="beaches")
        self.temple = make_category(name="Temples", slug="temples")
        self.museums = make_category(name="Museums", slug="museums")  # no places yet
        make_place(category=self.beach, name="Sunny Beach")
        make_place(category=self.temple, name="Old Temple")

    def test_fr_fi_01_all_option_and_every_active_category(self):
        r = self.client.get(reverse("places:list"))
        self.assertContains(r, "All places")
        for name in ("Beaches", "Temples", "Museums"):
            self.assertContains(r, name)

    def test_fr_fi_02_filters_by_category(self):
        r = self.client.get(reverse("places:list"), {"category": "beaches"})
        self.assertContains(r, "Sunny Beach")
        self.assertNotContains(r, "Old Temple")

    def test_fr_fi_03_selected_filter_shown(self):
        r = self.client.get(reverse("places:list"), {"category": "beaches"})
        self.assertContains(r, 'class="filter-chip is-selected"', count=1)
        self.assertEqual(r.context["selected_category"], self.beach)

    def test_fr_fi_04_clear_filter(self):
        r = self.client.get(reverse("places:list"), {"category": "beaches"})
        self.assertContains(r, "Clear filter")
        r = self.client.get(reverse("places:list"))
        self.assertContains(r, "Old Temple")
        self.assertContains(r, "Sunny Beach")

    def test_fr_fi_05_no_results_message(self):
        r = self.client.get(reverse("places:list"), {"category": "museums"})
        self.assertContains(r, "No places in Museums yet")

    def test_fr_fi_05_unknown_category(self):
        r = self.client.get(reverse("places:list"), {"category": "does-not-exist"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "That category isn't available")


class DetailTests(TestCase):
    def setUp(self):
        self.place = make_place(
            name="Richmond Castle",
            description="A mansion built in 1910.",
            opening_hours="9.00 am to 4.00 pm",
            entrance_fee="",
            toilets="yes",
            parking="no",
            transport="Take a tuk-tuk.",
            travel_tips="Go early.",
            family_suitability="Fine for children.",
            student_discount="Half price with student ID",
        )

    def test_fr_pd_01_name_category_description(self):
        r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "Richmond Castle")
        self.assertContains(r, self.place.category.name)
        self.assertContains(r, "A mansion built in 1910.")

    def test_fr_pd_02_distance_without_reference_coordinates(self):
        config = dict(settings.NEARBYGO, REFERENCE_LAT=6.7012345, REFERENCE_LNG=79.9054321)
        with override_settings(NEARBYGO=config):
            r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "5.0 km")
        self.assertNotContains(r, "6.7012345")
        self.assertNotContains(r, "79.9054321")

    def test_fr_pd_03_hours_fee_duration(self):
        r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "9.00 am to 4.00 pm")
        self.assertContains(r, "Recommended visit")
        self.assertContains(r, "1 h")

    def test_fr_pd_04_facilities(self):
        r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "Toilets")
        self.assertContains(r, "Parking")
        self.assertContains(r, "Accessibility")

    def test_fr_pd_05_travel_guidance(self):
        r = self.client.get(self.place.get_absolute_url())
        for text in ("Take a tuk-tuk.", "Go early.", "Fine for children.", "Half price with student ID"):
            self.assertContains(r, text)

    def test_fr_pd_06_unavailable_and_unverified_marked(self):
        r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "Not available")  # empty entrance fee
        self.assertContains(r, "Not yet verified")
        self.assertContains(r, "Not verified")  # facility left unknown

    def test_fr_pd_06_verified_date_shown(self):
        self.place.info_verified_on = "2026-09-01"
        self.place.save()
        r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "Checked with the venue on 1 September 2026")

    def test_fr_pd_07_unknown_and_inactive_return_404(self):
        self.assertEqual(self.client.get("/places/no-such-place/").status_code, 404)
        self.place.is_active = False
        self.place.save()
        r = self.client.get(self.place.get_absolute_url())
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "We couldn't find that page", status_code=404)

    def test_nfr_sa_01_04_guidance_notice(self):
        r = self.client.get(self.place.get_absolute_url())
        self.assertContains(r, "Information on this site is a guide only.")
        self.assertContains(r, "Check with the venue before you travel")

    def test_xss_safe_output(self):
        self.place.summary = "<script>alert(1)</script>"
        self.place.save()
        r = self.client.get(self.place.get_absolute_url())
        self.assertNotContains(r, "<script>alert(1)</script>")


class MapTests(TestCase):
    def setUp(self):
        self.place = make_place(name="Mount Lavinia Beach", latitude=Decimal("6.838500"), longitude=Decimal("79.863000"))
        self.hidden = make_place(name="Hidden Place", is_active=False)

    def markers(self, response):
        html = response.content.decode()
        start = html.index('<script id="map-markers" type="application/json">') + len('<script id="map-markers" type="application/json">')
        return json.loads(html[start:html.index("</script>", start)])

    def test_fr_mp_01_map_centred_on_panadura(self):
        r = self.client.get(reverse("places:map"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="places-map"')
        config = r.context["NEARBYGO_MAP"]
        self.assertEqual(config["center"], [6.7133, 79.9042])

    def test_fr_mp_02_one_marker_per_active_place(self):
        markers = self.markers(self.client.get(reverse("places:map")))
        self.assertEqual([m["name"] for m in markers], ["Mount Lavinia Beach"])
        self.assertAlmostEqual(markers[0]["lat"], 6.8385)

    def test_fr_mp_03_marker_has_name_and_link(self):
        marker = self.markers(self.client.get(reverse("places:map")))[0]
        self.assertEqual(marker["url"], self.place.get_absolute_url())
        self.assertEqual(marker["category"], self.place.category.name)

    def test_fr_mp_05_attribution(self):
        r = self.client.get(reverse("places:map"))
        self.assertContains(r, "OpenStreetMap")

    def test_fr_mp_06_text_list_available_without_map(self):
        r = self.client.get(reverse("places:map"))
        self.assertContains(r, "Places on this map")
        self.assertContains(r, self.place.get_absolute_url())

    def test_nfr_se_07_reference_not_in_map_page(self):
        config = dict(settings.NEARBYGO, REFERENCE_LAT=6.7012345, REFERENCE_LNG=79.9054321)
        with override_settings(NEARBYGO=config):
            r = self.client.get(reverse("places:map"))
        self.assertNotContains(r, "6.7012345")
        self.assertNotContains(r, "79.9054321")


class OtherPageTests(TestCase):
    def test_about_page(self):
        r = self.client.get(reverse("places:about"))
        self.assertContains(r, "How to use NearbyGo")

    def test_places_alias_redirects(self):
        r = self.client.get("/places/?category=x")
        self.assertRedirects(r, "/?category=x", fetch_redirect_response=False)

    def test_security_headers(self):
        r = self.client.get(reverse("places:list"))
        self.assertEqual(r["X-Frame-Options"], "DENY")
        self.assertEqual(r["X-Content-Type-Options"], "nosniff")


class PerformanceTests(TestCase):
    """NFR-PE-01 / NFR-PE-02 under test conditions with 100 places."""

    @classmethod
    def setUpTestData(cls):
        categories = [make_category() for _ in range(5)]
        for i in range(100):
            make_place(category=categories[i % 5], distance_km=Decimal(str(round(i * 0.24, 1))))

    def test_nfr_pe_01_place_list_fast_and_query_count_bounded(self):
        with self.assertNumQueries(3):
            self.client.get(reverse("places:list"))
        durations = []
        for _ in range(20):
            start = time.perf_counter()
            r = self.client.get(reverse("places:list"))
            durations.append(time.perf_counter() - start)
            self.assertEqual(r.status_code, 200)
        durations.sort()
        self.assertLess(durations[int(len(durations) * 0.95) - 1], 3.0)

    def test_nfr_pe_02_filter_fast(self):
        slug = Place.objects.first().category.slug
        start = time.perf_counter()
        r = self.client.get(reverse("places:list"), {"category": slug})
        self.assertEqual(r.status_code, 200)
        self.assertLess(time.perf_counter() - start, 2.0)
