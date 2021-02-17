"""Cash register views."""

# Django Rest Framework
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
import rest_framework.status as status_codes
from rest_framework.decorators import api_view

# Serializers
from .serializers import AvailableCashSerializer, PaymentFormSerializer, PaymentSerializer, PaymentFormCreateSerializer, TransactionLogSerializer

# Models
from cash_register.models import AvailableCash, Payment, TransactionLog

# Utils
from functools import reduce

@api_view(["GET"])
def check_status(request):
  """
  Simple view function to check the API status
  Args:
      request (object): The request object
  """
  return Response({"API working"},
                        status=status_codes.HTTP_200_OK)

class AvailableCashViewSet(ModelViewSet):
    """
    Class based view to handle CRUD operations over Available cash objects

    ...
    Methods:
        perform_update(): Override update method to save transaction log
        destroy(): Prevent use of delete method 
        empty_register(): Empty the cash register
        current_state(): Retrieve cash register current state
        _calc_total_cash(): Private method to calc total amount of transaction
    """
    queryset = AvailableCash.objects.all()
    serializer_class = AvailableCashSerializer

    def perform_update(self, serializer):
        """
        This method override update method to save transaction log

        ...
        Params
        - serializer: Serializer data to update
        """
        serializer.save()
        amount = serializer.data.get("currency_type") * serializer.data.get(
            "quantity")
        TransactionLog.objects.create(transaction_type="income", amount=amount)

    def destroy(self, request, pk=None):
        """
        This method prevent use of delete method 
        """
        raise MethodNotAllowed(method="DELETE")

    def empty_register(self, request):
        """
        This method empty the cash register
        """
        query = AvailableCash.objects.all()
        total_amount = self._calc_total_cash(query)
        self.queryset.update(quantity=0)
        TransactionLog.objects.create(transaction_type="outcome",
                                      amount=total_amount)
        return Response("Register has been empty.",
                        status=status_codes.HTTP_200_OK)

    def current_state(self, request):
        """
        This method retrieve cash register current state
        """
        query = AvailableCash.objects.all()
        total_amount = self._calc_total_cash(query)
        denominations = AvailableCashSerializer(query, many=True)
        data = {
            "denominations": denominations.data,
            "total_amount": total_amount
        }
        return Response(data, status=status_codes.HTTP_200_OK)

    def _calc_total_cash(self, query):
        """
        This private method to calc total amount of transaction

        ...
        Params
        - query: Query of all Available cash registers
        """        
        partial_amount = list(
            map((
                lambda bill: bill.quantity * bill.currency_type.currency_type),
                query))
        total_amount = reduce((lambda total1, total2: total1 + total2),
                              partial_amount)
        return total_amount


class PaymentFormViewSet(ModelViewSet):
    """
    Class based view to handle CRUD operations over payment form objects

    ...
    Methods:
        create(): Create payment register
        _validate_payment(): Check if the payment format is correct  
        _calc_change(): Calculate change for the customer
        _update_cash_register(): Update cash registers
        _insert_log(): Create a new log register
        destroy(): Prevent use of delete method 
        update(): Prevent use of put method 
        partial_update(): Prevent use of patch method 
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request):
        """
        This method create payment register

        ...
        Params
        - reques: Costumer payment detail
        """          
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
        """
        This method check if the payment format is correct  

        ...
        Params
        - payment_method: Costumer payment detail
        - amount: Cost of the product purchased by the customer 
        """          
        partial_amount = list(
            map((
                lambda bill: bill.get("quantity") * bill.get("currency_type")),
                payment_method))
        total_amount = reduce((lambda total1, total2: total1 + total2),
                              partial_amount)
        return total_amount if total_amount >= amount else 0

    def _calc_change(self, amount):
        """
        This method calculate change for the customer

        ...
        Params
        - amount: Cost of the product purchased by the customer 
        """           
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
        """
        This method update cash registers

        ...
        Params
        - payment_method: Costumer payment detail
        - change: Amount of money to be returned to the customer 
        """          
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
        """
        This method create a new log register

        ...
        Params
        - total_payment: Amount of money delivered by the customer 
        - amount: Cost of the product purchased by the customer
        """          
        TransactionLog.objects.create(transaction_type="income",
                                      amount=total_payment)
        TransactionLog.objects.create(transaction_type="outcome",
                                      amount=total_payment - amount)

    def destroy(self, request, pk=None):
        """
        This method prevent use of delete method 
        """
        raise MethodNotAllowed(method="DELETE")

    def update(self, request, pk=None):
        """
        This method prevent use of put method 
        """
        raise MethodNotAllowed(method="PUT")

    def partial_update(self, request, pk=None):
        """
        This method prevent use of pacth method 
        """
        raise MethodNotAllowed(method="PATCH")


class TransactionLogViewSet(ModelViewSet):
    """
    Class based view to handle CRUD operations over payment form objects

    ...
    Methods:
        create(): Prevent use of post method 
        update(): Prevent use of put method 
        partial_update(): Prevent use of patch method 
        destroy(): Prevent use of delete method 
        cash_history(): Retrieve cash history transactions
    """
    queryset = TransactionLog.objects.all()
    serializer_class = TransactionLogSerializer

    def create(self, request):
        """
        This method prevent use of post method 
        """        
        raise MethodNotAllowed(method="POST")

    def update(self, request, pk=None):
        """
        This method prevent use of put method 
        """        
        raise MethodNotAllowed(method="PUT")

    def partial_update(self, request, pk=None):
        """
        This method prevent use of patch method 
        """        
        raise MethodNotAllowed(method="PATCH")

    def destroy(self, request, pk=None):
        """
        This method prevent use of delete method 
        """        
        raise MethodNotAllowed(method="DELETE")

    def cash_history(self, request):
        """
        This method retrieve cash history transactions

        ...
        Params
        - request: Date to filter data
        """          
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
        }, status=status_codes.HTTP_200_OK)
