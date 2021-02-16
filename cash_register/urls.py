from django.urls import path, include

# Django Rest Framework
from rest_framework import routers

from .views import AvailableCashViewSet

router = routers.DefaultRouter()
router.register(r"available-cash",
                AvailableCashViewSet,
                basename="available-cash")

urlpatterns = [
    path("available-cash/empty/",
         AvailableCashViewSet.as_view({"get": "empty_register"}),
         name="empty-register"),
    path("", include(router.urls)),
]