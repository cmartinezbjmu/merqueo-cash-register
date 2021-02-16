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