from django.db import models

from places.models import Place


class VisitPlan(models.Model):
    """
    A visitor's one-day plan, tied to their anonymous browser session (DR-06, TBD-05).

    No personal information is stored (OR-05): only the session key Django
    already issues, the selected places and their order.
    """

    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Plan {self.pk} ({self.items.count()} places)"


class PlanItem(models.Model):
    plan = models.ForeignKey(VisitPlan, on_delete=models.CASCADE, related_name="items")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="plan_items")
    visit_order = models.PositiveSmallIntegerField()
    planned_time = models.TimeField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["visit_order", "added_at"]
        constraints = [
            # FR-VP-02 / BR-04: a place appears at most once in a plan.
            models.UniqueConstraint(fields=["plan", "place"], name="unique_place_per_plan"),
        ]

    def __str__(self):
        return f"{self.visit_order}. {self.place}"
