import datetime

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from places.models import Place

from . import services


def _redirect_back(request, fallback):
    """Return to the page the visitor came from, if it is on this site."""
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(target)
    return redirect(fallback)


def plan_view(request):
    """Show the one-day plan in visit order (FR-VP-03, FR-VP-06, FR-VP-09)."""
    plan = services.get_plan(request)
    removed = services.prune_unavailable(plan)
    if removed == 1:
        messages.info(request, "One place in your plan is no longer listed, so it was removed.")
    elif removed:
        messages.info(request, f"{removed} places in your plan are no longer listed, so they were removed.")
    items = list(services.plan_items(plan))
    total_minutes = sum(i.place.visit_duration_minutes or 0 for i in items)
    missing_duration = sum(1 for i in items if not i.place.visit_duration_minutes)
    markers = [
        {
            "name": i.place.name,
            "category": i.place.category.name,
            "colour": i.place.category.colour_hex,
            "lat": float(i.place.latitude),
            "lng": float(i.place.longitude),
            "url": i.place.get_absolute_url(),
            "order": index,
        }
        for index, i in enumerate(items, start=1)
    ]
    context = {
        "items": items,
        "total_minutes": total_minutes,
        "missing_duration": missing_duration,
        "markers": markers,
    }
    return render(request, "planner/plan.html", context)


@require_POST
def plan_add(request):
    """Add a public place to the plan (FR-VP-01, FR-VP-02)."""
    try:
        place_id = int(request.POST.get("place_id", ""))
    except ValueError:
        raise Http404("Unknown place")
    place = get_object_or_404(Place.objects.public(), pk=place_id)
    plan = services.get_plan(request, create=True)
    try:
        _, created = services.add_place(plan, place)
    except services.PlanFullError:
        messages.error(request, f"Your plan already has {services.MAX_PLAN_ITEMS} places. Remove one before adding another.")
        return _redirect_back(request, place.get_absolute_url())
    if created:
        messages.success(request, f"Added {place.name} to your plan.")
    else:
        messages.info(request, f"{place.name} is already in your plan.")
    return _redirect_back(request, place.get_absolute_url())


@require_POST
def plan_remove(request, item_id):
    """Remove one place (FR-VP-04)."""
    plan = services.get_plan(request)
    place = services.remove_item(plan, item_id) if plan else None
    if place:
        messages.success(request, f"Removed {place.name} from your plan.")
    else:
        messages.error(request, "That place is not in your plan.")
    return redirect("planner:plan")


@require_POST
def plan_move(request, item_id):
    """Move one place earlier or later in the visit order (FR-VP-05)."""
    direction = request.POST.get("direction")
    plan = services.get_plan(request)
    if direction not in {"up", "down"} or plan is None:
        messages.error(request, "That change could not be made. Use the Move earlier or Move later buttons.")
        return redirect("planner:plan")
    services.move_item(plan, item_id, direction)
    return redirect(f"{reverse('planner:plan')}#item-{item_id}")


@require_POST
def plan_set_time(request, item_id):
    """Save or clear an optional planned arrival time for one place."""
    plan = services.get_plan(request)
    raw = (request.POST.get("planned_time") or "").strip()
    planned_time = None
    if raw:
        try:
            planned_time = datetime.time.fromisoformat(raw)
        except ValueError:
            messages.error(request, "Enter the time as hours and minutes, for example 09:30.")
            return redirect("planner:plan")
    if plan and services.set_planned_time(plan, item_id, planned_time):
        messages.success(request, "Time saved." if planned_time else "Time cleared.")
    else:
        messages.error(request, "That place is not in your plan.")
    return redirect(f"{reverse('planner:plan')}#item-{item_id}")


@require_http_methods(["GET", "POST"])
def plan_clear(request):
    """Ask for confirmation, then remove every place (FR-VP-08)."""
    plan = services.get_plan(request)
    count = plan.items.count() if plan else 0
    if request.method == "POST":
        if plan:
            services.clear_plan(plan)
        messages.success(request, "Your plan is now empty.")
        return redirect("planner:plan")
    if count == 0:
        messages.info(request, "Your plan is already empty.")
        return redirect("planner:plan")
    return render(request, "planner/clear_confirm.html", {"count": count})
