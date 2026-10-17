from django.contrib import admin

from .models import PlanItem, VisitPlan


class PlanItemInline(admin.TabularInline):
    model = PlanItem
    extra = 0
    fields = ("visit_order", "place", "planned_time", "added_at")
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(VisitPlan)
class VisitPlanAdmin(admin.ModelAdmin):
    """Read-only view of anonymous plans, useful for checking DR-06. Plans hold no personal data."""

    list_display = ("id", "item_count", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fields = ("created_at", "updated_at")
    inlines = (PlanItemInline,)

    def get_queryset(self, request):
        from django.db.models import Count

        return super().get_queryset(request).annotate(_item_count=Count("items"))

    @admin.display(description="places", ordering="_item_count")
    def item_count(self, obj):
        return obj._item_count

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
