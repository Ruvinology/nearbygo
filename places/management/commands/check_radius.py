from django.core.management.base import BaseCommand

from places import geo
from places.models import Place


class Command(BaseCommand):
    help = (
        "Report every place's recorded distance and, when the private reference location is configured, "
        "its straight-line distance from it. Flags anything outside the project radius (BR-01, FR-AD-07). "
        "The reference coordinates themselves are never printed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--tolerance", type=float, default=5.0,
            help="Warn when recorded and straight-line distances differ by more than this many km (default 5).",
        )

    def handle(self, *args, **options):
        limit = geo.radius_km()
        configured = geo.reference_configured()
        if not configured:
            self.stdout.write(self.style.WARNING(
                "Reference location not set (NEARBYGO_REFERENCE_LAT / NEARBYGO_REFERENCE_LNG). "
                "Only recorded distances are checked."
            ))

        problems = 0
        header = f"{'Place':42} {'Active':6} {'Recorded':>9} {'Straight':>9}  Result"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for place in Place.objects.select_related("category").order_by("distance_km", "name"):
            computed = place.straight_line_km()
            notes = []
            if place.distance_km > limit:
                notes.append(f"recorded distance over {limit:g} km")
            if computed is not None:
                if computed > limit:
                    notes.append(f"coordinates over {limit:g} km")
                if computed > float(place.distance_km) + 0.05:
                    notes.append("straight line longer than recorded distance")
                elif float(place.distance_km) - computed > options["tolerance"]:
                    notes.append("recorded distance much longer than straight line")
            if notes and place.is_active:
                problems += 1
            result = "; ".join(notes) if notes else "OK"
            straight = f"{computed:6.1f} km" if computed is not None else f"{'-':>9}"
            self.stdout.write(
                f"{place.name[:42]:42} {'yes' if place.is_active else 'no':6} {float(place.distance_km):6.1f} km {straight}  {result}"
            )

        if problems:
            self.stdout.write(self.style.ERROR(f"{problems} active place(s) need attention."))
        else:
            self.stdout.write(self.style.SUCCESS("All active places pass the radius check."))
