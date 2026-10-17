from decimal import Decimal
from itertools import count

from places.models import Category, Place

_seq = count(1)


def make_category(**kwargs):
    n = next(_seq)
    data = {"name": f"Category {n}", "slug": f"category-{n}", "colour": "lagoon", "is_active": True}
    data.update(kwargs)
    return Category.objects.create(**data)


def make_place(category=None, **kwargs):
    n = next(_seq)
    data = {
        "name": f"Place {n}",
        "slug": f"place-{n}",
        "category": category or make_category(),
        "summary": f"Summary for place {n}.",
        "description": f"Description for place {n}.",
        "latitude": Decimal("6.713300"),
        "longitude": Decimal("79.904200"),
        "distance_km": Decimal("5.0"),
        "is_active": True,
        "visit_duration_minutes": 60,
    }
    data.update(kwargs)
    return Place.objects.create(**data)
