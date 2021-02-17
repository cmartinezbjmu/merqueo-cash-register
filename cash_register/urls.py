from django.urls import path, include

# Django Rest Framework
from rest_framework import routers

from .views import AvailableCashViewSet, PaymentFormViewSet

router = routers.DefaultRouter()
router.register(r"available-cash",
                AvailableCashViewSet,
                basename="available-cash")
router.register(r"payments", PaymentFormViewSet, basename="payments")

urlpatterns = [
    path("available-cash/empty/",
         AvailableCashViewSet.as_view({"get": "empty_register"}),
         name="empty-register"),
    path("available-cash/current-state/",
         AvailableCashViewSet.as_view({"get": "current_state"}),
         name="current_state"),
    path("", include(router.urls)),
]