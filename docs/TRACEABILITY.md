# NearbyGo requirement traceability

This table links every requirement in the NearbyGo SRS v1.0 to where it is
implemented and how it is verified (NFR-QA-06). Automated tests run with
`python manage.py test`. "Manual" means a browser check listed in the
acceptance checklist at the end of this file.

## Functional requirements

| ID | Implementation | Verification |
|---|---|---|
| FR-PL-01 | `places/views.py` `place_list`, `Place.objects.public()` | `test_fr_pl_01_lists_active_places` |
| FR-PL-02 | `templates/places/_place_card.html` | `test_fr_pl_02_summary_fields` |
| FR-PL-03 | Card title and "View details" link | `test_fr_pl_03_link_to_details` |
| FR-PL-04 | `PlaceQuerySet.public()` | `test_fr_pl_04_inactive_hidden`, `test_public_queryset_rules` |
| FR-PL-05 | Empty state in `place_list.html` | `test_fr_pl_05_empty_state` |
| FR-FI-01 | `_categories_with_counts()`, `includes/category_filter.html` | `test_fr_fi_01_all_option_and_every_active_category` |
| FR-FI-02 | `?category=<slug>` filter | `test_fr_fi_02_filters_by_category` |
| FR-FI-03 | Selected chip (`is-selected`, `aria-current`) | `test_fr_fi_03_selected_filter_shown` |
| FR-FI-04 | "All places" and "Clear filter" links | `test_fr_fi_04_clear_filter` |
| FR-FI-05 | No-results empty state | `test_fr_fi_05_no_results_message`, `test_fr_fi_05_unknown_category` |
| FR-PD-01 | `place_detail.html` | `test_fr_pd_01_name_category_description` |
| FR-PD-02 | `distance_km` shown; reference only in server settings | `test_fr_pd_02_distance_without_reference_coordinates` |
| FR-PD-03 | Visiting information list | `test_fr_pd_03_hours_fee_duration` |
| FR-PD-04 | Facilities (toilets, parking, seating, food) and accessibility | `test_fr_pd_04_facilities` |
| FR-PD-05 | Transport, families, student discount, travel tips | `test_fr_pd_05_travel_guidance` |
| FR-PD-06 | "Not available", "Not verified", "Not yet verified" notice, `info_verified_on` | `test_fr_pd_06_unavailable_and_unverified_marked`, `test_fr_pd_06_verified_date_shown` |
| FR-PD-07 | `get_object_or_404(Place.objects.public())`, `templates/404.html` | `test_fr_pd_07_unknown_and_inactive_return_404` |
| FR-MP-01 | `NEARBYGO["MAP_CENTER"]`, `static/js/maps.js` | `test_fr_mp_01_map_centred_on_panadura` |
| FR-MP-02 | Marker data from `_marker_data()` | `test_fr_mp_02_one_marker_per_active_place` |
| FR-MP-03 | Popup with name, category and "View details" link | `test_fr_mp_03_marker_has_name_and_link` |
| FR-MP-04 | Leaflet pan and zoom controls | Manual check M1 |
| FR-MP-05 | Tile layer attribution, footer link | `test_fr_mp_05_attribution` |
| FR-MP-06 | Text list under the map; tile/Leaflet failure message | `test_fr_mp_06_text_list_available_without_map`, manual check M2 |
| FR-VP-01 | `planner.views.plan_add`, `services.add_place` | `test_fr_vp_01_add_place`, `test_fr_vp_01_confirmation_message`, `test_fr_vp_01_inactive_place_cannot_be_added` |
| FR-VP-02 | `unique_place_per_plan` constraint, `add_place` | `test_fr_vp_02_br_04_no_duplicates` |
| FR-VP-03 | Numbered ordered list, `services.renumber` | `test_fr_vp_03_numbered_order` |
| FR-VP-04 | `plan_remove` | `test_fr_vp_04_remove` |
| FR-VP-05 | "Move earlier" / "Move later" buttons, `services.move_item` | `test_fr_vp_05_move_earlier`, `test_fr_vp_05_move_later`, `test_fr_vp_05_first_cannot_move_up` |
| FR-VP-06 | Distance, visit time and total visiting time on plan page | `test_fr_vp_06_distance_and_duration_shown` |
| FR-VP-07 | Plan id stored in the server-side session; `VisitPlan` row | `test_fr_vp_07_plan_kept_for_session` |
| FR-VP-08 | Confirmation page `planner/clear_confirm.html` | `test_fr_vp_08_clear_asks_for_confirmation` |
| FR-VP-09 | "This plan is a guide" notice | `test_fr_vp_09_guidance_notice` |
| FR-AD-01 | Django admin `staff_member_required` | `test_fr_ad_01_nfr_se_01_login_required`, `test_non_staff_user_cannot_use_admin` |
| FR-AD-02 | Django admin login form (generic error) | `test_fr_ad_02_invalid_credentials_generic_message` |
| FR-AD-03 | `CategoryAdmin` | `test_fr_ad_03_category_create_edit_delete` |
| FR-AD-04 | `PlaceAdmin`, activate and deactivate actions | `test_fr_ad_04_place_create_and_edit`, `test_fr_ad_04_activate_and_deactivate_actions` |
| FR-AD-05 | Model fields and `Place.clean()` | `test_fr_ad_05_required_fields`, `test_fr_ad_05_dr_04_unique_name_ignores_case`, `test_fr_ad_05_non_negative_distance` |
| FR-AD-06 | Latitude and longitude validators | `test_fr_ad_06_latitude_range`, `test_fr_ad_06_longitude_range`, `test_fr_ad_06_boundary_values_accepted` |
| FR-AD-07 | `Place.clean()` radius check, `places/geo.py`, `check_radius` command | `test_fr_ad_07_*` (6 tests), `test_check_radius_command` |
| FR-AD-08 | Django admin delete confirmation; `PROTECT` on category | `test_fr_ad_08_delete_requires_confirmation`, `test_category_in_use_cannot_be_deleted_from_admin` |
| FR-AD-09 | `TimeStampedModel` | `test_fr_ad_09_timestamps` |
| FR-AD-10 | Admin "Log out" (POST) | `test_fr_ad_10_sign_out_invalidates_session` |

## Interface requirements

| ID | Implementation | Verification |
|---|---|---|
| IR-UI-01 | `templates/base.html`, `static/css/nearbygo.css` | Inspection |
| IR-UI-02 | Responsive CSS grid, tested at 360, 768 and 1280 px | Manual check M3 |
| IR-UI-03 | Visible labels and `visually-hidden` names on icon buttons | Inspection |
| IR-UI-04 | Django form errors beside fields | `test_ir_ui_04_field_error_messages` |
| IR-UI-05 | Empty states on list, map and plan | `test_fr_pl_05_empty_state`, `test_ir_ui_05_empty_plan_message` |
| IR-COM-01 | `USE_HTTPS` / `SECURE_SSL_REDIRECT` | `manage.py check --deploy` |
| IR-COM-02 | `DEFAULT_CHARSET = "utf-8"`, `<meta charset>` | `test_ir_com_02_utf8` |
| IR-COM-03 | Standard HTML form posts | Inspection |
| IR-COM-04 | `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` follow `USE_HTTPS` | `manage.py check --deploy` |
| IR-COM-05 | Configurable `MAP_TILE_URL`, attribution always shown | `test_fr_mp_05_attribution` |

## Nonfunctional requirements

| ID | Implementation | Verification |
|---|---|---|
| NFR-PE-01 | `select_related`, two queries per list page | `test_nfr_pe_01_place_list_fast_and_query_count_bounded` (100 places) |
| NFR-PE-02 | Same queries with a filter | `test_nfr_pe_02_filter_fast` |
| NFR-PE-03 | Stateless views, database sessions | Manual check M5 (load test) |
| NFR-PE-04 | Server-rendered HTML, local static files, scripts at end of page | Manual check M4 |
| NFR-PE-05 | Tiles load asynchronously; 8-second fallback message | Manual check M2 |
| NFR-SA-01 | Footer and detail notices | `test_nfr_sa_01_04_guidance_notice` |
| NFR-SA-02 | Content rules in About page and seed text | Inspection |
| NFR-SA-03 | "Deactivate" action and `is_active` checkbox | `test_nfr_sa_03_deactivation_hides_immediately` |
| NFR-SA-04 | "Confirm with the venue" notices | `test_nfr_sa_01_04_guidance_notice` |
| NFR-SE-01 | Django admin permissions | `test_fr_ad_01_nfr_se_01_login_required` |
| NFR-SE-02 | Django password hashers | `test_nfr_se_02_password_hashed` |
| NFR-SE-03 | `CsrfViewMiddleware`, `{% csrf_token %}` on every form | `test_nfr_se_03_csrf_enforced`, `test_nfr_se_03_admin_forms_use_csrf` |
| NFR-SE-04 | Model validation, `int()` parsing of ids, safe `next` redirects | `test_invalid_place_id_returns_404`, `test_open_redirect_blocked`, `test_xss_safe_output` |
| NFR-SE-05 | Django ORM only, no raw SQL | Inspection |
| NFR-SE-06 | `USE_HTTPS=True` turns on HTTPS redirect, secure cookies and HSTS | `manage.py check --deploy` |
| NFR-SE-07 | Reference point only in environment and `places/geo.py` | `test_fr_pd_02_*`, `test_nfr_se_07_reference_not_in_map_page`, `test_fr_ad_07_coordinates_checked_against_private_reference` |
| NFR-SE-08 | `AdminIdleTimeoutMiddleware`, `ADMIN_IDLE_TIMEOUT` | `test_nfr_se_08_idle_timeout`, `test_fr_ad_10_sign_out_invalidates_session` |
| NFR-QA-01 | Single flow: card → details → Add to plan | Manual check M6 |
| NFR-QA-02 | Alt text required with images, labelled controls, keyboard markers | `test_nfr_qa_02_image_requires_alt_text`, manual check M7 |
| NFR-QA-03 | Responsive layout | Manual check M3 |
| NFR-QA-04 | 404 page for bad ids, empty states | `test_fr_pd_07_*`, `test_invalid_place_id_returns_404` |
| NFR-QA-05 | Two Django apps (`places`, `planner`) with models, views, urls, templates, static | Inspection |
| NFR-QA-06 | This document | Inspection |
| NFR-QA-07 | `.env` / environment variables in `config/settings.py` | Inspection |
| NFR-QA-08 | Same validation in model and admin form | `test_fr_ad_05_*`, `test_fr_ad_06_*` |

## Business, database and other requirements

| ID | Implementation | Verification |
|---|---|---|
| BR-01 | `public()` filter and `Place.clean()` | `test_public_queryset_rules`, `test_fr_ad_07_*` |
| BR-02 | Admin only | `test_fr_ad_01_*` |
| BR-03 | `category__is_active=True` in `public()` | `test_br_03_inactive_category_hides_its_places` |
| BR-04 | Unique constraint on plan items | `test_fr_vp_02_br_04_no_duplicates` |
| BR-05 | No booking or payment features | `test_br_05_no_booking_or_payment_controls` |
| BR-06 | No routing; plan map shows numbered stops only | `test_fr_vp_09_guidance_notice` |
| BR-07 | Optional fields, verified date | `test_fr_pd_06_*` |
| DR-01 to DR-03 | `places/models.py` | Migrations, `test_fr_ad_05_required_fields` |
| DR-04 | `unique=True` plus case-insensitive check in `clean()` | `test_fr_ad_05_dr_04_unique_name_ignores_case`, `test_dr_04_category_name_unique_ignoring_case` |
| DR-05 | Foreign key with `on_delete=PROTECT` | `test_dr_05_category_with_places_cannot_be_deleted` |
| DR-06 | `VisitPlan` and `PlanItem` with `visit_order` | `test_fr_vp_*` |
| DR-07 | `seed_places` command | `test_dr_07_seed_loads_ten_places_within_radius` |
| OR-01 | English interface | Inspection |
| OR-02 | `utf8mb4` database charset | `test_unicode_names_supported` |
| OR-03 | Attribution on every map | `test_fr_mp_05_attribution` |
| OR-04 | Original seed text; image credit field | Inspection |
| OR-05 | Plans store only a session key and places | `test_or_05_no_personal_data_collected` |

## Manual acceptance checklist

Run these in Chrome, Edge and Firefox with internet access.

- **M1** Map page: drag the map and use + and − and the mouse wheel (after clicking the map). Tab to a marker and press Enter to open its popup.
- **M2** Disconnect from the internet (or block `tile.openstreetmap.org`) and reload the map page. A yellow message appears within about 8 seconds and the list of places still works.
- **M3** In developer tools, check the home, details, map and plan pages at 360, 768 and 1280 px wide. There is no sideways scrolling.
- **M4** In developer tools (Network, "Fast 4G"), the first text appears in under 3 seconds.
- **M5** Run 20 concurrent sessions, for example `ab -n 400 -c 20 http://127.0.0.1:8000/` with the production server, and check there are no errors.
- **M6** Ask a first-time user to find a place, see it on the map and add it to a plan without help.
- **M7** Complete browse → details → add to plan → reorder → clear using only the keyboard.
