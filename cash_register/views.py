"""Cash register views."""

# Django Rest Framework
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
import rest_framework.status as status_codes

# Serializers
from .serializers import AvailableCashSerializer, PaymentFormSerializer, PaymentSerializer, PaymentFormCreateSerializer, TransactionLogSerializer

# Models
from cash_register.models import AvailableCash, Payment, TransactionLog

# Utils
from functools import reduce


class AvailableCashViewSet(ModelViewSet):

    queryset = AvailableCash.objects.all()
    serializer_class = AvailableCashSerializer

    def perform_update(self, serializer):
        serializer.save()
        amount = serializer.data.get("currency_type") * serializer.data.get(
            "quantity")
        TransactionLog.objects.create(transaction_type="income", amount=amount)

    def destroy(self, request, pk=None):
        raise MethodNotAllowed(method="DELETE")

    def empty_register(self, request):
        query = AvailableCash.objects.all()
        total_amount = self._calc_total_cash(query)
        self.queryset.update(quantity=0)
        TransactionLog.objects.create(transaction_type="outcome",
                                      amount=total_amount)
        return Response("Register has been empty.",
                        status=status_codes.HTTP_200_OK)

    def current_state(self, request):
        query = AvailableCash.objects.all()
        total_amount = self._calc_total_cash(query)
        denominations = AvailableCashSerializer(query, many=True)
        data = {
            "denominations": denominations.data,
            "total_amount": total_amount
        }
        return Response(data, status=status_codes.HTTP_200_OK)

    def _calc_total_cash(self, query):
        partial_amount = list(
            map((
                lambda bill: bill.quantity * bill.currency_type.currency_type),
                query))
        total_amount = reduce((lambda total1, total2: total1 + total2),
                              partial_amount)
        return total_amount


class PaymentFormViewSet(ModelViewSet):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request):
        total_payment = self._validate_payment(request.data["payment_form"],
                                               request.data["amount"])
        if total_payment:
            change, error = self._calc_change(total_payment -
                                              request.data["amount"])
            if error:
                return Response(
                    f"Sorry, Missing change for ${change.__str__()}",
                    status=status_codes.HTTP_400_BAD_REQUEST)

            request.data["total_payment"] = total_payment
            serializer_payment_form = PaymentFormSerializer(
                data=request.data["payment_form"], many=True)
            serializer_payment = self.serializer_class(data=request.data)
            if serializer_payment.is_valid(
            ) and serializer_payment_form.is_valid():
                self.perform_create(serializer_payment)
                for payment_method in request.data["payment_form"]:
                    payment_method["payment"] = serializer_payment.instance.id
                    payment_form_create = PaymentFormCreateSerializer(
                        data=payment_method)
                    if payment_form_create.is_valid():
                        payment_form_create.save()
                    else:
                        return Response(
                            payment_form_create.errors,
                            status=status_codes.HTTP_400_BAD_REQUEST)
                self._update_cash_register(request.data["payment_form"],
                                           change)
                self._insert_log(total_payment, request.data["amount"])
                change.append(
                    {"total_change": total_payment - request.data["amount"]})
                return Response(change, status=status_codes.HTTP_201_CREATED)
            else:
                return Response(serializer_payment_form.errors,
                                status=status_codes.HTTP_400_BAD_REQUEST)

        return Response("Payment value is lower than purchase amount.",
                        status=status_codes.HTTP_400_BAD_REQUEST)

    def _validate_payment(self, payment_method, amount):
        partial_amount = list(
            map((
                lambda bill: bill.get("quantity") * bill.get("currency_type")),
                payment_method))
        total_amount = reduce((lambda total1, total2: total1 + total2),
                              partial_amount)
        return total_amount if total_amount >= amount else 0

    def _calc_change(self, amount):
        current_cash = AvailableCash.objects.filter(
            quantity__gt=0).values_list("currency_type",
                                        "quantity").order_by("-currency_type")
        change = []
        for available_cash in list(current_cash):
            if amount >= available_cash[0]:
                partial_change = dict()
                partial_change["currency_type"] = available_cash[0]
                partial_change["quantity"] = amount // available_cash[
                    0] if amount // available_cash[0] <= available_cash[
                        1] else available_cash[1]
                change.append(partial_change)
                amount = amount - partial_change["quantity"] * partial_change[
                    "currency_type"]
        if amount == 0:
            return change, False
        return amount, True

    def _update_cash_register(self, payment_method, change):
        denominations_payment = dict((cash["currency_type"], cash["quantity"])
                                     for cash in payment_method)
        denominations_change = dict(
            (cash["currency_type"], cash["quantity"]) for cash in change)
        denominations = list(
            map(lambda cash: cash.get("currency_type"), payment_method))
        current_cash = AvailableCash.objects.select_for_update().filter(
            currency_type__in=denominations)
        for partial_cash in current_cash:
            partial_cash.quantity += denominations_payment[
                partial_cash.currency_type.currency_type]
            partial_cash.save()
        denominations_cash = list(
            map(lambda cash: cash.get("currency_type"), change))
        current_cash = AvailableCash.objects.select_for_update().filter(
            currency_type__in=denominations_cash)
        for partial_cash in current_cash:
            partial_cash.quantity -= denominations_change[
                partial_cash.currency_type.currency_type]
            partial_cash.save()

    def _insert_log(self, total_payment, amount):
        TransactionLog.objects.create(transaction_type="income",
                                      amount=total_payment)
        TransactionLog.objects.create(transaction_type="outcome",
                                      amount=total_payment - amount)

    def destroy(self, request, pk=None):
        raise MethodNotAllowed(method="DELETE")

    def update(self, request, pk=None):
        raise MethodNotAllowed(method="PUT")

    def partial_update(self, request, pk=None):
        raise MethodNotAllowed(method="PATCH")


class TransactionLogViewSet(ModelViewSet):

    queryset = TransactionLog.objects.all()
    serializer_class = TransactionLogSerializer

    def create(self, request):
        raise MethodNotAllowed(method="POST")

    def update(self, request, pk=None):
        raise MethodNotAllowed(method="PUT")

    def partial_update(self, request, pk=None):
        raise MethodNotAllowed(method="PATCH")

    def destroy(self, request, pk=None):
        raise MethodNotAllowed(method="DELETE")

    def cash_history(self, request):
        registers = self.queryset.filter(
            created_at__lte=request.data.get("date"))
        serializer = self.serializer_class(registers, many=True)
        total_amount = 0
        for register in registers:
            if register.transaction_type == "income":
                total_amount += register.amount
            else:
                total_amount -= register.amount
        return Response({
            "total_amount": total_amount,
            "logs": serializer.data
        },
                        status=status_codes.HTTP_200_OK)
