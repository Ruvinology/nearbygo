import os

from django.conf import settings
from django.contrib.staticfiles import finders

from .models import Category


def _asset_version(path):
    """Last-modified time of a static file, used as ?v= so browsers fetch a changed file instead of a cached one."""
    found = finders.find(path)
    try:
        return str(int(os.path.getmtime(found))) if found else "1"
    except OSError:
        return "1"


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
        "CSS_VERSION": _asset_version("css/nearbygo.css"),
        "JS_VERSION": _asset_version("js/maps.js"),
    }
