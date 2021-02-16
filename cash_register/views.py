from django.db.models import query
from cash_register.models import AvailableCash

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
import rest_framework.status as status_codes

from .serializers import AvailableCashSerializer

from django.db.models.base import Model

# Utils
from functools import reduce


class AvailableCashViewSet(ModelViewSet):

    queryset = AvailableCash.objects.all()
    serializer_class = AvailableCashSerializer

    def destroy(self, request, pk=None):
        raise MethodNotAllowed(method='DELETE')

    def empty_register(self, request):
        self.queryset.update(quantity=0)
        return Response("Register has been empty.",
                        status=status_codes.HTTP_200_OK)

    def current_state(self, request):
        partial_ammount = list(
            map((lambda bill: bill.quantity * bill.currency_type.currency_type), self.queryset))
        total_ammount = reduce((lambda total1, total2: total1 + total2), partial_ammount)
        denominations = AvailableCashSerializer(self.queryset, many=True)
        data = {
            "denominations": denominations.data,
            "total": total_ammount
        }
        return Response(data,
                    status=status_codes.HTTP_200_OK)
