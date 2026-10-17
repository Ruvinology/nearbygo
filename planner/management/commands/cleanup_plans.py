from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.utils import timezone

from planner.models import VisitPlan


class Command(BaseCommand):
    help = "Delete visit plans whose browser session has expired. Run after Django's clearsessions command."

    def handle(self, *args, **options):
        live_keys = Session.objects.filter(expire_date__gt=timezone.now()).values("session_key")
        cutoff = timezone.now() - timedelta(seconds=settings.SESSION_COOKIE_AGE)
        stale = VisitPlan.objects.exclude(session_key__in=live_keys) | VisitPlan.objects.filter(updated_at__lt=cutoff)
        stale_ids = list(stale.values_list("pk", flat=True).distinct())
        VisitPlan.objects.filter(pk__in=stale_ids).delete()
        count = len(stale_ids)
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} expired plan(s)."))
