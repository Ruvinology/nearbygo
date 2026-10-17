from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from . import geo


def unique_slug(instance, value, max_length=140):
    """Build a slug from `value` that is unique for the instance's model."""
    base = slugify(value)[:max_length] or "item"
    slug = base
    counter = 2
    model = type(instance)
    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        slug = f"{base[: max_length - len(suffix)]}{suffix}"
        counter += 1
    return slug


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("created", auto_now_add=True)
    updated_at = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """A classification used to group places (Appendix A)."""

    class Colour(models.TextChoices):
        LAGOON = "lagoon", "Lagoon blue"
        SAFFRON = "saffron", "Saffron"
        LEAF = "leaf", "Leaf green"
        INDIGO = "indigo", "Indigo"
        BRICK = "brick", "Brick red"
        SLATE = "slate", "Slate"

    COLOUR_HEX = {
        "lagoon": "#0b7f8a",
        "saffron": "#c27a0e",
        "leaf": "#2f8a4c",
        "indigo": "#6a4cc2",
        "brick": "#c0502e",
        "slate": "#4f5d68",
    }

    class Icon(models.TextChoices):
        PIN = "geo-alt", "Map pin"
        WATER = "water", "Water / beach"
        TREE = "tree", "Nature"
        BINOCULARS = "binoculars", "Wildlife"
        FLOWER = "flower1", "Religious site"
        BANK = "bank", "Heritage building"
        EASEL = "easel", "Museum / learning"
        CAMERA = "camera", "Sightseeing"

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True, help_text="Used in web addresses. Leave blank to generate from the name.")
    description = models.TextField(blank=True)
    colour = models.CharField(max_length=10, choices=Colour.choices, default=Colour.LAGOON, help_text="Colour used for cards and map markers.")
    icon = models.CharField(max_length=20, choices=Icon.choices, default=Icon.PIN, help_text="Symbol shown when a place has no photo.")
    display_order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first in the filter bar.")
    is_active = models.BooleanField("active", default=True, help_text="Inactive categories and their places are hidden from visitors.")

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    @property
    def colour_hex(self):
        return self.COLOUR_HEX.get(self.colour, self.COLOUR_HEX["slate"])

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
        # DR-04: names are unique regardless of letter case.
        if self.name and Category.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({"name": "A category with this name already exists (names are not case-sensitive)."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, max_length=90)
        super().save(*args, **kwargs)


class PlaceQuerySet(models.QuerySet):
    def public(self):
        """Places visitors may see: active, in an active category and inside the radius (FR-PL-04, BR-01, BR-03)."""
        return self.filter(
            is_active=True,
            category__is_active=True,
            distance_km__lte=Decimal(str(geo.radius_km())),
        ).select_related("category")


class Place(TimeStampedModel):
    """A local place that visitors can discover and add to a one-day plan."""

    class Availability(models.TextChoices):
        UNKNOWN = "unknown", "Not verified"
        YES = "yes", "Available"
        NO = "no", "Not available"

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True, help_text="Used in web addresses. Leave blank to generate from the name.")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="places")
    summary = models.CharField(max_length=200, help_text="One or two sentences shown on place cards.")
    description = models.TextField()

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
        help_text="Decimal degrees, from -90 to 90.",
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))],
        help_text="Decimal degrees, from -180 to 180.",
    )
    distance_km = models.DecimalField(
        "approximate distance (km)", max_digits=5, decimal_places=1,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Verified distance from the reference location. Must be 25 km or less for the place to be active.",
    )
    is_active = models.BooleanField("active", default=True, help_text="Only active places are shown to visitors.")

    # Practical information (DR-03). Blank means "not available".
    opening_hours = models.CharField(max_length=200, blank=True)
    entrance_fee = models.CharField(max_length=200, blank=True)
    visit_duration_minutes = models.PositiveSmallIntegerField(
        "recommended visit (minutes)", null=True, blank=True,
        validators=[MinValueValidator(10), MaxValueValidator(720)],
    )
    best_time_to_visit = models.CharField(max_length=200, blank=True)

    toilets = models.CharField(max_length=10, choices=Availability.choices, default=Availability.UNKNOWN)
    parking = models.CharField(max_length=10, choices=Availability.choices, default=Availability.UNKNOWN)
    seating = models.CharField(max_length=10, choices=Availability.choices, default=Availability.UNKNOWN)
    food = models.CharField("food and refreshments", max_length=10, choices=Availability.choices, default=Availability.UNKNOWN)
    facilities_notes = models.TextField(blank=True)
    accessibility = models.TextField("accessibility information", blank=True)

    transport = models.TextField("getting there", blank=True, help_text="Transport options and directions.")
    family_suitability = models.TextField(blank=True)
    student_discount = models.CharField(max_length=200, blank=True)
    travel_tips = models.TextField(blank=True)

    image = models.ImageField(upload_to="places/", blank=True)
    image_alt = models.CharField("image description (alt text)", max_length=200, blank=True)
    image_credit = models.CharField(max_length=200, blank=True, help_text="Photographer or licence, if required (OR-04).")

    info_verified_on = models.DateField(
        "practical info verified on", null=True, blank=True,
        help_text="Leave blank until hours, fees and facilities have been checked with the venue.",
    )

    objects = PlaceQuerySet.as_manager()

    class Meta:
        ordering = ["distance_km", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("places:detail", kwargs={"slug": self.slug})

    @property
    def is_verified(self):
        return self.info_verified_on is not None

    @property
    def facility_items(self):
        return [
            ("Toilets", self.toilets),
            ("Parking", self.parking),
            ("Seating", self.seating),
            ("Food and refreshments", self.food),
        ]

    def straight_line_km(self):
        """Haversine distance from the private reference point, if configured."""
        return geo.distance_from_reference_km(self.latitude, self.longitude)

    def clean(self):
        super().clean()
        errors = {}
        self.name = (self.name or "").strip()

        # DR-04: unique names regardless of letter case.
        if self.name and Place.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            errors["name"] = "A place with this name already exists (names are not case-sensitive)."

        # FR-AD-07 / BR-01: a place outside the radius cannot be published.
        limit = geo.radius_km()
        if self.is_active and self.distance_km is not None and self.distance_km > Decimal(str(limit)):
            errors["distance_km"] = (
                f"This place is {self.distance_km} km away. Only places within {limit:g} km can be active; "
                "untick 'active' or correct the distance."
            )

        if self.is_active and self.latitude is not None and self.longitude is not None:
            computed = self.straight_line_km()
            if computed is not None and computed > limit:
                errors["latitude"] = (
                    f"These coordinates are {computed:.1f} km in a straight line from the reference location, "
                    f"which is outside the {limit:g} km radius. Check the coordinates or untick 'active'."
                )

        # NFR-QA-02: informative images need alternative text.
        if self.image and not self.image_alt.strip():
            errors["image_alt"] = "Describe the image for visitors who use screen readers."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)
