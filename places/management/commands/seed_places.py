from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from places.models import Category, Place
from places.seed_data import CATEGORIES, PLACES

SEED_IMAGE_DIR = Path(__file__).resolve().parents[2] / "seed_images"
IMAGE_FIELDS = ("image", "image_alt", "image_credit")


def attach_seed_image(place, filename, alt, credit):
    """Copy a bundled picture into MEDIA_ROOT and attach it to the place. Returns True if attached."""
    source = SEED_IMAGE_DIR / filename
    if not source.exists():
        return False
    place.image_alt = alt
    place.image_credit = credit
    with source.open("rb") as fh:
        place.image.save(filename, File(fh), save=False)
    return True


class Command(BaseCommand):
    help = (
        "Load the five categories and ten approved places from the SRS (DR-07), with their pictures. "
        "Safe to run more than once."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite existing places with the seed text. Without this, existing places keep their text. "
            "Pictures are only added to places that have none.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for data in CATEGORIES:
            category, created = Category.objects.get_or_create(slug=data["slug"], defaults=data)
            categories[data["slug"]] = category
            self.stdout.write(f"{'Created' if created else 'Kept'} category: {category.name}")

        created_count = updated_count = kept_count = images_added = 0
        for raw in PLACES:
            data = dict(raw)
            image_data = {key: data.pop(key, "") for key in IMAGE_FIELDS}
            data["category"] = categories[data["category"]]
            for key in ("latitude", "longitude", "distance_km"):
                data[key] = Decimal(data[key])

            existing = Place.objects.filter(slug=data["slug"]).first()
            if existing and not options["update"]:
                kept_count += 1
                # Existing places keep their text, but get the picture if they have none yet.
                if not existing.image and image_data["image"]:
                    if attach_seed_image(existing, image_data["image"], image_data["image_alt"], image_data["image_credit"]):
                        existing.save(update_fields=["image", "image_alt", "image_credit", "updated_at"])
                        images_added += 1
                continue

            place = existing or Place()
            for key, value in data.items():
                setattr(place, key, value)
            if image_data["image"] and not place.image:
                if attach_seed_image(place, image_data["image"], image_data["image_alt"], image_data["image_credit"]):
                    images_added += 1
            place.full_clean()
            place.save()
            if existing:
                updated_count += 1
            else:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Places: {created_count} created, {updated_count} updated, {kept_count} left unchanged. "
            f"Pictures added: {images_added}."
        ))
