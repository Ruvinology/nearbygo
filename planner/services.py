"""
Operations on a visitor's one-day plan (SRS 4.5).

Plans are anonymous: the plan's id is kept in the visitor's server-side
session, and the plan row records the current session key so stale plans can
be cleaned up later (DR-06, TBD-05).
"""

from django.db import IntegrityError, transaction
from django.db.models import Max

from places.models import Place

from .models import PlanItem, VisitPlan

SESSION_PLAN_KEY = "nearbygo_plan_id"
MAX_PLAN_ITEMS = 20


class PlanFullError(Exception):
    pass


def get_plan(request, create=False):
    """Return the visitor's plan, creating it (and the session) if `create` is true."""
    session = request.session
    plan = None
    plan_id = session.get(SESSION_PLAN_KEY)
    if plan_id:
        plan = VisitPlan.objects.filter(pk=plan_id).first()
        if plan is None:
            session.pop(SESSION_PLAN_KEY, None)

    if plan is None and create:
        session[SESSION_PLAN_KEY] = None  # marks the session as modified so the cookie is sent
        if not session.session_key:
            session.save()
        plan = VisitPlan.objects.create(session_key=session.session_key)
        session[SESSION_PLAN_KEY] = plan.pk

    # Django rotates the session key when someone signs in; keep the plan attached.
    if plan is not None and session.session_key and plan.session_key != session.session_key:
        VisitPlan.objects.filter(session_key=session.session_key).exclude(pk=plan.pk).delete()
        plan.session_key = session.session_key
        plan.save(update_fields=["session_key", "updated_at"])
    return plan


def plan_items(plan):
    if plan is None:
        return PlanItem.objects.none()
    return plan.items.select_related("place", "place__category").order_by("visit_order", "added_at")


def renumber(plan):
    """Keep visit_order as 1, 2, 3 … with no gaps (FR-VP-03)."""
    for index, item in enumerate(plan.items.order_by("visit_order", "added_at"), start=1):
        if item.visit_order != index:
            item.visit_order = index
            item.save(update_fields=["visit_order"])


def add_place(plan, place):
    """Add `place` to the end of the plan. Returns (item, created) (FR-VP-01, FR-VP-02)."""
    existing = plan.items.filter(place=place).first()
    if existing:
        return existing, False
    if plan.items.count() >= MAX_PLAN_ITEMS:
        raise PlanFullError
    next_order = (plan.items.aggregate(m=Max("visit_order"))["m"] or 0) + 1
    try:
        with transaction.atomic():
            item = PlanItem.objects.create(plan=plan, place=place, visit_order=next_order)
    except IntegrityError:
        # A second request added the same place at the same moment.
        return plan.items.get(place=place), False
    plan.save(update_fields=["updated_at"])
    return item, True


def remove_item(plan, item_id):
    """Remove one place from the plan (FR-VP-04). Returns the removed place or None."""
    item = plan.items.select_related("place").filter(pk=item_id).first()
    if item is None:
        return None
    place = item.place
    item.delete()
    renumber(plan)
    return place


@transaction.atomic
def move_item(plan, item_id, direction):
    """Move an item one step up or down (FR-VP-05). Returns True if the order changed."""
    renumber(plan)
    items = list(plan.items.order_by("visit_order"))
    index = next((i for i, item in enumerate(items) if item.pk == item_id), None)
    if index is None:
        return False
    target = index - 1 if direction == "up" else index + 1
    if target < 0 or target >= len(items):
        return False
    a, b = items[index], items[target]
    a.visit_order, b.visit_order = b.visit_order, a.visit_order
    a.save(update_fields=["visit_order"])
    b.save(update_fields=["visit_order"])
    plan.save(update_fields=["updated_at"])
    return True


def set_planned_time(plan, item_id, planned_time):
    updated = plan.items.filter(pk=item_id).update(planned_time=planned_time)
    return bool(updated)


def clear_plan(plan):
    """Remove every place from the plan (FR-VP-08)."""
    count, _ = plan.items.all().delete()
    return count


def prune_unavailable(plan):
    """Drop places that were deactivated after the visitor added them (FR-PL-04)."""
    if plan is None:
        return 0
    public_ids = Place.objects.public().values("pk")
    count, _ = plan.items.exclude(place__in=public_ids).delete()
    if count:
        renumber(plan)
    return count
