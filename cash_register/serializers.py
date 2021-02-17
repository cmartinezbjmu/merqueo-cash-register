""""""

from rest_framework import serializers

from .models import *


class CurrencyDenominationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyDenomination
        fields = ["currency_type"]

class AvailableCashSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableCash
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["amount", "total_payment"]

class PaymentFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentForm
        fields = ["currency_type", "quantity"]        

class PaymentFormCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentForm
        fields = "__all__"         

class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        fields = "__all__"                 