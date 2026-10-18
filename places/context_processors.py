from django.conf import settings

from .models import Category


def site_settings(request):
    """Public, non-sensitive settings used by templates. The reference location is never included (NFR-SE-07)."""
    config = settings.NEARBYGO
    return {
        "NEARBYGO_MAP": {
            "center": list(config["MAP_CENTER"]),
            "zoom": config["MAP_ZOOM"],
            "tileUrl": config["MAP_TILE_URL"],
            "attribution": config["MAP_ATTRIBUTION"],
        },
        "NEARBYGO_RADIUS_KM": config["RADIUS_KM"],
        "footer_categories": Category.objects.filter(is_active=True).only("name", "slug"),
    }
