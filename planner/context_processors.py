from .services import SESSION_PLAN_KEY
from .models import PlanItem


def plan_summary(request):
    """Number of places in the visitor's plan, for the navigation badge."""
    session = getattr(request, "session", None)
    plan_id = session.get(SESSION_PLAN_KEY) if session is not None else None
    if not plan_id:
        return {"plan_count": 0}
    return {"plan_count": PlanItem.objects.filter(plan_id=plan_id).count()}
