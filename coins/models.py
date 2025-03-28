from django.db import models


class Ticker(models.Model):
    symbol = models.CharField(max_length=20)

    price_change = models.CharField(max_length=20)
    price_change_percent = models.CharField(max_length=20)
    weighted_avg_price = models.CharField(max_length=20)
    prev_close_price = models.CharField(max_length=20)
    last_price = models.CharField(max_length=20)
    last_qty = models.CharField(max_length=20)
    bid_price = models.CharField(max_length=20)
    bid_qty = models.CharField(max_length=20)
    ask_price = models.CharField(max_length=20)
    ask_qty = models.CharField(max_length=20)
    open_price = models.CharField(max_length=20)
    high_price = models.CharField(max_length=20)
    low_price = models.CharField(max_length=20)
    volume = models.CharField(max_length=30)
    quote_volume = models.CharField(max_length=30)

    open_time = models.BigIntegerField()
    close_time = models.BigIntegerField()
    first_id = models.BigIntegerField()
    last_id = models.BigIntegerField()
    count = models.IntegerField()

    fetched_at = models.DateField()

    class Meta:
        unique_together = ('symbol', 'fetched_at')
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['fetched_at']),
        ]
        ordering = ['-fetched_at', 'symbol']

    def __str__(self):
        return f"{self.symbol} on {self.fetched_at}"

