"""Payment form test cases."""

# Django
from django.test import TestCase
from django.urls import reverse

# Models
from cash_register.models import AvailableCash, CurrencyDenomination

# Utils
import json


class PaymentFormTestCase(TestCase):
    """Payment form test cases."""
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

    def test_payment_create(self):
        """Valid test to add Payments."""

        response = self.client.post(reverse("payments-list"), {
            "amount": 130000,
            "payment_form": [{
                "quantity": 8,
                "currency_type": 10000
            }, {
                "quantity": 10,
                "currency_type": 20000
            }, {
                "quantity": 1,
                "currency_type": 500
            }]
        }, content_type="application/json")
        response_data = json.loads(response.content)
        self.assertEqual(response_data[0], {
            "currency_type": 20000,
            "quantity": 5
        })
        self.assertEqual(response.status_code, 201)
