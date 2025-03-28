from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import date

from .fetch_tickers import fetch_and_store_ticker_data
from .models import Ticker
from .serializers import TickerSerializer


class TodayTickerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Today's Binance Tickers (Paginated)",
        description="Returns paginated Binance ticker data for the current day. Supports optional `symbol` filter.",
        parameters=[
            OpenApiParameter(name='symbol', description='Filter by symbol (e.g. BTCUSDT)', required=False, type=str),
            OpenApiParameter(name='page', description='Page number (for pagination)', required=False, type=int),
        ],
        responses={200: TickerSerializer(many=True)},
    )
    def get(self, request):
        """
        It will fetch the Today's Ticker Data and Store it To DB if no data present in DB initially
        :param request:
        :return: returns the todays all coins data
        """
        today = date.today()
        symbol = request.GET.get('symbol')

        queryset = Ticker.objects.filter(fetched_at=today)

        if len(queryset) == 0:
            _ = fetch_and_store_ticker_data()
            queryset = Ticker.objects.filter(fetched_at=today)

        if symbol:
            queryset = queryset.filter(symbol=symbol)

        paginator = PageNumberPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = TickerSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)


class CoinStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Current Coin Status",
        description="Returns current status (last price, % change, and trend) for a given coin symbol.",
        parameters=[
            OpenApiParameter(name='symbol', description='Symbol like BTCUSDT, ETHBTC, etc.', required=True, type=str),
        ],
        responses={
            200: dict,
            404: dict,
        }
    )
    def get(self, request):
        symbol = request.GET.get('symbol')
        if not symbol:
            return Response({"error": "Missing symbol param"}, status=status.HTTP_400_BAD_REQUEST)

        today = date.today()
        try:
            ticker = Ticker.objects.filter(symbol=symbol.upper(), fetched_at=today).latest('fetched_at')
        except Ticker.DoesNotExist:
            return Response({"error": "Data not found for symbol today."}, status=status.HTTP_404_NOT_FOUND)

        try:
            change_percent = float(ticker.price_change_percent)
        except (TypeError, ValueError):
            change_percent = 0.0

        # TODO: we can have config based Define trend logic

        if change_percent > 0.2:
            trend = "uptrend"
        elif change_percent < -0.2:
            trend = "downtrend"
        else:
            trend = "flat"

        return Response({
            "symbol": ticker.symbol,
            "last_price": ticker.last_price,
            "price_change_percent": ticker.price_change_percent,
            "trend": trend
        })


# TODO: In oder to have the api exposed and to render it via other front end library
class CoinChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Historical Chart Data for a Coin",
        description="Returns historical last price and price change % for chart plotting.",
        parameters=[
            OpenApiParameter(name='symbol', description='Symbol (e.g., BTCUSDT)', required=True, type=str)
        ],
        responses={200: dict, 404: dict}
    )
    def get(self, request):
        symbol = request.GET.get('symbol')
        if not symbol:
            return Response({"error": "Missing symbol param"}, status=status.HTTP_400_BAD_REQUEST)

        tickers = Ticker.objects.filter(symbol=symbol.upper()).order_by('fetched_at')

        if not tickers.exists():
            return Response({"error": "No data found for this symbol."}, status=status.HTTP_404_NOT_FOUND)

        data = [
            {
                "date": t.fetched_at.isoformat(),
                "last_price": t.last_price,
                "price_change_percent": t.price_change_percent,
            }
            for t in tickers
        ]
        return Response(data)


def coin_chart_view(request, symbol="BTCUSDT"):
    """
    get chart view will render the chart view and its unauthenticated
    :param request:
    :param symbol: you have to send the SYMBOL of the coin for which you are looking the data
    :return: return the HTML response
    """
    tickers = Ticker.objects.filter(symbol=symbol.upper()).order_by('fetched_at')

    labels = [t.fetched_at.strftime("%Y-%m-%d") for t in tickers]
    prices = [float(t.last_price) for t in tickers]
    changes = [float(t.price_change_percent) for t in tickers]

    context = {
        "symbol": symbol.upper(),
        "labels": labels,
        "prices": prices,
        "changes": changes,
    }
    return render(request, "coins/coin_chart.html", context)
