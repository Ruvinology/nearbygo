"""
Distance-checking method for the 25 km project radius (SRS 2.5, BR-01).

NearbyGo stores an administrator-verified approximate distance for every
place. When the private reference location is configured through the
environment, the system also computes the straight-line (great-circle)
distance from that point with the haversine formula and refuses to publish a
place that lies outside the radius. Straight-line distance is always shorter
than or equal to road distance, so it is a conservative lower bound: a place
that fails this check is certainly outside the radius.

The reference coordinates never leave this module's callers on the server.
"""

from math import asin, cos, radians, sin, sqrt

from django.conf import settings

EARTH_RADIUS_KM = 6371.0088  # mean Earth radius (IUGG)


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance in kilometres between two WGS84 points."""
    lat1, lng1, lat2, lng2 = (radians(float(v)) for v in (lat1, lng1, lat2, lng2))
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def radius_km():
    return float(settings.NEARBYGO["RADIUS_KM"])


def reference_configured():
    config = settings.NEARBYGO
    return config.get("REFERENCE_LAT") is not None and config.get("REFERENCE_LNG") is not None


def distance_from_reference_km(lat, lng):
    """Straight-line distance from the private reference point, or None if it is not configured."""
    if not reference_configured() or lat is None or lng is None:
        return None
    config = settings.NEARBYGO
    return haversine_km(config["REFERENCE_LAT"], config["REFERENCE_LNG"], lat, lng)
