"""Cash register serializers"""

# Django Rest Framework
from rest_framework import serializers

# Models
from .models import CurrencyDenomination, AvailableCash, Payment, PaymentForm, TransactionLog


class CurrencyDenominationSerializer(serializers.ModelSerializer):
    """Currency Denomination serializer."""
    class Meta:
        model = CurrencyDenomination
        fields = ["currency_type"]

class AvailableCashSerializer(serializers.ModelSerializer):
    """Available Cash serializer."""
    class Meta:
        model = AvailableCash
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer."""
    class Meta:
        model = Payment
        fields = ["amount", "total_payment"]

class PaymentFormSerializer(serializers.ModelSerializer):
    """Payment Form serializer."""
    class Meta:
        model = PaymentForm
        fields = ["currency_type", "quantity"]

class PaymentFormCreateSerializer(serializers.ModelSerializer):
    """Payment Form Create serializer."""
    class Meta:
        model = PaymentForm
        fields = "__all__"

class TransactionLogSerializer(serializers.ModelSerializer):
    """Transaction Log serializer."""
    class Meta:
        model = TransactionLog
        fields = "__all__"
