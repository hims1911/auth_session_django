# binance/tasks.py

from celery import shared_task
import requests
from datetime import date
from .models import Ticker


@shared_task
def fetch_and_store_ticker_data():
    today = date.today()
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        count = 0
        for item in data:
            symbol = item.get("symbol")
            if Ticker.objects.filter(symbol=symbol, fetched_at=today).exists():
                continue

            Ticker.objects.create(
                symbol=symbol,
                price_change=item.get("priceChange"),
                price_change_percent=item.get("priceChangePercent"),
                weighted_avg_price=item.get("weightedAvgPrice"),
                prev_close_price=item.get("prevClosePrice"),
                last_price=item.get("lastPrice"),
                last_qty=item.get("lastQty"),
                bid_price=item.get("bidPrice"),
                bid_qty=item.get("bidQty"),
                ask_price=item.get("askPrice"),
                ask_qty=item.get("askQty"),
                open_price=item.get("openPrice"),
                high_price=item.get("highPrice"),
                low_price=item.get("lowPrice"),
                volume=item.get("volume"),
                quote_volume=item.get("quoteVolume"),
                open_time=item.get("openTime"),
                close_time=item.get("closeTime"),
                first_id=item.get("firstId"),
                last_id=item.get("lastId"),
                count=item.get("count"),
                fetched_at=today
            )
            count += 1
        return f"{count} tickers saved for {today}"
    return "Failed to fetch data"
