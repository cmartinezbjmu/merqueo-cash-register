"""Available cash test cases."""

# Django
from django.test import TestCase
from django.urls import reverse

# Models
from cash_register.models import AvailableCash, CurrencyDenomination

# Utils
import json


class CashRegisterTestCase(TestCase):
    """Cash register test cases."""
    @classmethod
    def setUpTestData(cls):
        CurrencyDenomination.objects.create(currency_type=100000)
        CurrencyDenomination.objects.create(currency_type=20000)
        CurrencyDenomination.objects.create(currency_type=10000)
        CurrencyDenomination.objects.create(currency_type=500)
        CurrencyDenomination.objects.create(currency_type=200)

        AvailableCash.objects.create(currency_type_id=20000, quantity=5)
        AvailableCash.objects.create(currency_type_id=10000, quantity=10)
        AvailableCash.objects.create(currency_type_id=500, quantity=15)
        AvailableCash.objects.create(currency_type_id=200, quantity=20)

    def test_available_cash_create(self):
        """Valid test to add available cash."""

        new_cash = CurrencyDenomination.objects.filter(currency_type=100000)
        response = self.client.post(reverse("available-cash-list"), {
            "quantity": 3,
            "currency_type": new_cash
        }, formal="json")
        response_data = json.loads(response.content)
        self.assertEqual(response_data["quantity"], 3)
        self.assertEqual(response.status_code, 201)

    def test_available_cash_empty_cash_register(self):
        """Valid test to empty cash register."""

        response = self.client.get(reverse("empty-register"), formal="json")
        response_data = json.loads(response.content)
        self.assertEqual(response_data, "Register has been empty.")
        self.assertEqual(response.status_code, 200)

    def test_available_cash_current_state(self):
        """Valid test to retrieve cash register current state."""

        response = self.client.get(reverse("current-state"), formal="json")
        response_data = json.loads(response.content)
        self.assertEqual(response_data['total_amount'], 211500)
        self.assertEqual(response.status_code, 200)
