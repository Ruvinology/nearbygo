from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.html import format_html

from . import geo
from .models import Category, Place


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "colour", "display_order", "is_active", "place_count", "updated_at")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    actions = ("make_active", "make_inactive")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_place_count=Count("places"))

    @admin.display(description="places", ordering="_place_count")
    def place_count(self, obj):
        return obj._place_count

    @admin.action(description="Activate selected categories")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} categor{'y' if updated == 1 else 'ies'}.", messages.SUCCESS)

    @admin.action(description="Deactivate selected categories (their places are hidden)")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} categor{'y' if updated == 1 else 'ies'}.", messages.SUCCESS)


class VerifiedFilter(admin.SimpleListFilter):
    title = "practical info"
    parameter_name = "verified"

    def lookups(self, request, model_admin):
        return (("yes", "Verified"), ("no", "Not verified"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(info_verified_on__isnull=False)
        if self.value() == "no":
            return queryset.filter(info_verified_on__isnull=True)
        return queryset


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "distance_km", "is_active", "verified", "updated_at")
    list_filter = ("is_active", "category", VerifiedFilter)
    list_select_related = ("category",)
    search_fields = ("name", "summary", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("radius_check", "image_preview", "created_at", "updated_at")
    save_on_top = True
    actions = ("make_active", "make_inactive")

    fieldsets = (
        (None, {
            "fields": ("name", "slug", "category", "is_active", "summary", "description"),
        }),
        ("Location", {
            "description": "Coordinates are shown on the public map. The reference location itself is never shown to visitors.",
            "fields": (("latitude", "longitude"), "distance_km", "radius_check"),
        }),
        ("Visiting information", {
            "description": "Leave a field blank if the information cannot be verified. Visitors will see 'Not available'.",
            "fields": ("opening_hours", "entrance_fee", "visit_duration_minutes", "best_time_to_visit", "info_verified_on"),
        }),
        ("Facilities", {
            "fields": (("toilets", "parking"), ("seating", "food"), "facilities_notes", "accessibility"),
        }),
        ("Travel guidance", {
            "fields": ("transport", "family_suitability", "student_discount", "travel_tips"),
        }),
        ("Image", {
            "fields": ("image", "image_preview", "image_alt", "image_credit"),
        }),
        ("Record", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(boolean=True, description="info verified", ordering="info_verified_on")
    def verified(self, obj):
        return obj.is_verified

    @admin.display(description="radius check")
    def radius_check(self, obj):
        limit = geo.radius_km()
        if not geo.reference_configured():
            return (
                f"Reference location not configured. Only the recorded distance is checked against {limit:g} km. "
                "Set NEARBYGO_REFERENCE_LAT and NEARBYGO_REFERENCE_LNG to enable the coordinate check."
            )
        if obj is None or obj.pk is None:
            return "Save the place to see the straight-line distance from the reference location."
        computed = obj.straight_line_km()
        status = "inside" if computed <= limit else "OUTSIDE"
        return f"{computed:.1f} km in a straight line from the reference location ({status} the {limit:g} km radius)."

    @admin.display(description="preview")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" alt="{}" style="max-width:240px;height:auto;border-radius:6px">', obj.image.url, obj.image_alt)
        return "No image uploaded."

    @admin.action(description="Activate selected places (radius rules apply)")
    def make_active(self, request, queryset):
        activated, refused = 0, []
        for place in queryset.select_related("category"):
            if place.is_active:
                continue
            place.is_active = True
            try:
                place.full_clean()
            except ValidationError:
                refused.append(place.name)
                continue
            place.save(update_fields=["is_active", "updated_at"])
            activated += 1
        if activated:
            self.message_user(request, f"Activated {activated} place{'s' if activated != 1 else ''}.", messages.SUCCESS)
        if refused:
            self.message_user(
                request,
                "Not activated because the details are incomplete or outside the radius: " + ", ".join(refused) + ". Open each place to see why.",
                messages.ERROR,
            )
        if not activated and not refused:
            self.message_user(request, "The selected places were already active.", messages.INFO)

    @admin.action(description="Deactivate selected places (hide from visitors)")
    def make_inactive(self, request, queryset):
        updated = 0
        for place in queryset.filter(is_active=True):
            place.is_active = False
            place.save(update_fields=["is_active", "updated_at"])
            updated += 1
        self.message_user(request, f"Deactivated {updated} place{'s' if updated != 1 else ''}.", messages.SUCCESS)
