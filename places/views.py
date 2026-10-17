from django.conf import settings
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from planner.services import get_plan

from .models import Category, Place


def _categories_with_counts():
    """Active categories with the number of places a visitor can see (FR-FI-01)."""
    public_ids = Place.objects.public().values("pk")
    return Category.objects.filter(is_active=True).annotate(
        place_count=Count("places", filter=Q(places__in=public_ids))
    )


def _selected_category(request, categories):
    """Return (slug, Category or None). An unknown slug yields no category but keeps the slug."""
    slug = (request.GET.get("category") or "").strip()
    if not slug:
        return "", None
    return slug, next((c for c in categories if c.slug == slug), None)


def _planned_place_ids(request):
    plan = get_plan(request)
    if plan is None:
        return set()
    return set(plan.items.values_list("place_id", flat=True))


def place_list(request):
    """Home page: browse and filter places (SRS 4.1, 4.2)."""
    categories = list(_categories_with_counts())
    selected_slug, selected_category = _selected_category(request, categories)

    places = Place.objects.public()
    if selected_slug:
        # An unknown or inactive category returns no places and an explanation (FR-FI-05).
        places = places.filter(category=selected_category) if selected_category else places.none()

    context = {
        "categories": categories,
        "selected_slug": selected_slug,
        "selected_category": selected_category,
        "places": places,
        "planned_ids": _planned_place_ids(request),
        "radius_km": settings.NEARBYGO["RADIUS_KM"],
    }
    return render(request, "places/place_list.html", context)


def place_detail(request, slug):
    """Full information for one place (SRS 4.3). Inactive or unknown places return 404 (FR-PD-07)."""
    place = get_object_or_404(Place.objects.public(), slug=slug)
    nearby = (
        Place.objects.public()
        .filter(category=place.category)
        .exclude(pk=place.pk)[:3]
    )
    planned_ids = _planned_place_ids(request)
    context = {
        "place": place,
        "in_plan": place.pk in planned_ids,
        "planned_ids": planned_ids,
        "nearby": nearby,
        "marker": _marker_data([place])[0],
    }
    return render(request, "places/place_detail.html", context)


def _marker_data(places, planned_ids=frozenset()):
    return [
        {
            "name": p.name,
            "category": p.category.name,
            "colour": p.category.colour_hex,
            "lat": float(p.latitude),
            "lng": float(p.longitude),
            "distance": float(p.distance_km),
            "url": p.get_absolute_url(),
            "inPlan": p.pk in planned_ids,
        }
        for p in places
    ]


def map_view(request):
    """Interactive map of every public place (SRS 4.4)."""
    categories = list(_categories_with_counts())
    selected_slug, selected_category = _selected_category(request, categories)

    places = Place.objects.public().filter(latitude__isnull=False, longitude__isnull=False)
    if selected_slug:
        places = places.filter(category=selected_category) if selected_category else places.none()
    places = list(places)
    planned_ids = _planned_place_ids(request)

    context = {
        "categories": categories,
        "selected_slug": selected_slug,
        "selected_category": selected_category,
        "places": places,
        "markers": _marker_data(places, planned_ids),
        "planned_ids": planned_ids,
    }
    return render(request, "places/map.html", context)


def about(request):
    """About and help page (SRS 2.6)."""
    return render(request, "places/about.html", {"radius_km": settings.NEARBYGO["RADIUS_KM"]})
