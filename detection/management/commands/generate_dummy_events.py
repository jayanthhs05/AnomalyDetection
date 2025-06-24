from django.core.management.base import BaseCommand
from django.utils import timezone
from random import gauss, randrange
from datetime import timedelta

from detection.models import GenericEvent


class Command(BaseCommand):
    help = "Populate GenericEvent with synthetic data (+ a few obvious outliers)."

    def add_arguments(self, parser):
        parser.add_argument(
            "-n",
            "--num",
            type=int,
            default=1_000,
            help="Total number of rows to create (default 1000)",
        )

    def handle(self, *args, **opts):
        n = opts["num"]
        now = timezone.now()

        rows = []
        for i in range(n):

            val = gauss(50, 5)

            if randrange(20) == 0:
                val *= 3

            rows.append(
                GenericEvent(
                    timestamp=now - timedelta(seconds=i),
                    value=val,
                )
            )

        GenericEvent.objects.bulk_create(rows, batch_size=10_000)
        self.stdout.write(self.style.SUCCESS(f"Inserted {n} GenericEvent rows"))
