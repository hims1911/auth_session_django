from django.urls import path
from .views import TodayTickerAPIView, CoinStatusAPIView, CoinChartDataAPIView

urlpatterns = [
    path('tickers/today/', TodayTickerAPIView.as_view(), name='today-tickers'),
    path('tickers/status/', CoinStatusAPIView.as_view(), name='coin-status'),
    path('tickers/chart-data/', CoinChartDataAPIView.as_view(), name='chart-data'),
]
