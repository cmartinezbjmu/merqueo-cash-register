"""Cash register models."""

# Django
from django.db import models


class CurrencyDenomination(models.Model):
    """
    CurrencyDenomination Model stores all denomination cash.
    """
    currency_type = models.IntegerField(unique=True)

    def __str__(self):
        return self.currency_type.__str__()


class AvailableCash(models.Model):
    """
    AvailableCash Model stores available cash on cash register.
    """
    currency_type = models.OneToOneField(CurrencyDenomination,
                                         to_field="currency_type",
                                         on_delete=models.CASCADE,
                                         related_name="available_currency")
    quantity = models.IntegerField(blank=False, null=False, default=0)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    """
    Payment Model stores the total payment and the amount
    of money delivered by the customer.
    """
    amount = models.IntegerField(blank=False, null=False, default=0)
    total_payment = models.IntegerField(blank=False, null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class PaymentForm(models.Model):
    """
    PaymentForm Model stores the detail payment delivered by the customer.
    """
    payment = models.ForeignKey(Payment,
                                on_delete=models.CASCADE,
                                related_name="payment_form")
    currency_type = models.ForeignKey(CurrencyDenomination,
                                      to_field="currency_type",
                                      on_delete=models.CASCADE,
                                      related_name="payment_currency")
    quantity = models.IntegerField(blank=False, null=False)


class TransactionLog(models.Model):
    """
    TransactionLog Model stores all transactions of the cash register.
    """
    TRANSACTION_TYPES_CHOICES = [("INCOME", "income"), ("OUTCOME", "outcome")]
    transaction_type = models.CharField(choices=TRANSACTION_TYPES_CHOICES,
                                        blank=False,
                                        null=False,
                                        max_length=8)
    amount = models.IntegerField(blank=False, null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
