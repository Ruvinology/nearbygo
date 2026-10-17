from django import template

register = template.Library()


@register.filter
def duration(minutes):
    """Format minutes as '45 min', '1 h' or '2 h 30 min'."""
    if minutes in (None, ""):
        return ""
    minutes = int(minutes)
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours} h {mins} min"
    if hours:
        return f"{hours} h"
    return f"{mins} min"


@register.filter
def km(value):
    """Format a distance like '4.0 km'."""
    if value in (None, ""):
        return ""
    return f"{float(value):.1f} km"


@register.filter
def contains(collection, item):
    return item in collection
