from django.core.management.base import BaseCommand
from datetime import date
from django.db import connection
from coins.models import Ticker
from coins.fetch_tickers import fetch_and_store_ticker_data

# only import beat models if the tables exist
def beat_tables_ready():
    tables = connection.introspection.table_names()
    return (
        'django_celery_beat_crontabschedule' in tables and
        'django_celery_beat_periodictask' in tables
    )


class Command(BaseCommand):
    help = "Runs the fetch once and sets up daily schedule"

    def handle(self, *args, **kwargs):
        if not Ticker.objects.filter(fetched_at=date.today()).exists():
            fetch_and_store_ticker_data.delay()
            self.stdout.write("✅ Task triggered for today.")

        if beat_tables_ready():
            from django_celery_beat.models import PeriodicTask, CrontabSchedule

            schedule, _ = CrontabSchedule.objects.get_or_create(minute='0', hour='2')
            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                name='Daily Binance Ticker Fetch',
                task='coins.fetch_tickers.fetch_and_store_ticker_data',
            )
            self.stdout.write("✅ Daily schedule ensured.")
        else:
            self.stdout.write("⚠️ Celery Beat tables not ready. Skipping schedule creation.")
