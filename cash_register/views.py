
from cash_register.models import AvailableCash

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed


from .serializers import AvailableCashSerializer


from django.db.models.base import Model


class AvailableCashViewSet(ModelViewSet):

  queryset = AvailableCash.objects.all()
  serializer_class = AvailableCashSerializer

  def destroy(self, request, pk=None):
    raise MethodNotAllowed(method='DELETE')