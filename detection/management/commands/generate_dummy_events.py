# detection/management/commands/generate_dummy_events.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from random import gauss, randrange
from datetime import timedelta

from detection.models import RawEvent   # timestamp, value[1]

class Command(BaseCommand):
    help = "Populate RawEvent with synthetic data (+ a few obvious outliers)."

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--num", type=int, default=1_000,
            help="Total number of rows to create (default 1000)"
        )

    def handle(self, *args, **opts):
        n = opts["num"]
        now = timezone.now()

        rows = []
        for i in range(n):
            # 95 % of points ~ N(50, 5²)
            val = gauss(50, 5)

            # 5 % obvious outliers
            if randrange(20) == 0:          # 1 out of 20
                val *= 3                    # push it far away

            rows.append(
                RawEvent(
                    timestamp=now - timedelta(seconds=i),
                    value=val,
                )
            )

        RawEvent.objects.bulk_create(rows, batch_size=10_000)  # one SQL INSERT
        self.stdout.write(self.style.SUCCESS(f"Inserted {n} RawEvent rows"))
