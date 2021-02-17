"""Cash register urls."""

from django.urls import path, include

# Django Rest Framework
from rest_framework import routers

from .views import AvailableCashViewSet, PaymentFormViewSet, TransactionLogViewSet

router = routers.DefaultRouter()
router.register(r"available-cash",
                AvailableCashViewSet,
                basename="available-cash")
router.register(r"payments", PaymentFormViewSet, basename="payments")
router.register(r"logs", TransactionLogViewSet, basename="logs")

urlpatterns = [
    path("available-cash/empty/",
         AvailableCashViewSet.as_view({"get": "empty_register"}),
         name="empty-register"),
    path("available-cash/current-state/",
         AvailableCashViewSet.as_view({"get": "current_state"}),
         name="current-state"),
    path("logs/search-date/",
         TransactionLogViewSet.as_view({"post": "cash_history"}),
         name="search-date"),
    path("", include(router.urls)),
]
