""""""

from rest_framework import serializers

from .models import *

class CurrencyDenominationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyDenomination
        fields = "__all__"

class AvailableCashSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableCash
        fields = "__all__"