"""Cash register models."""

# Django
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import Choices

class CurrencyDenomination(models.Model):
  currency_type = models.IntegerField(unique=True)


class AvailableCash(models.Model):
  currency_type = models.ForeignKey(CurrencyDenomination, on_delete=CASCADE, related_name="available_currency")
  quantity = models.IntegerField(blank=False, null=False, default=0)
  updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
  amount = models.IntegerField(blank=False, null=False, default=0)
  total_payment = models.IntegerField(blank=False, null=False, default=0)
  created_at = models.DateTimeField(auto_now_add=True)
    

class PaymentForm(models.Model):
  payment = models.ForeignKey(Payment, on_delete=CASCADE, related_name="payment_form")
  currency_type = models.ForeignKey(CurrencyDenomination, on_delete=CASCADE, related_name="payment_currency")
  quantity = models.IntegerField(blank=False, null=False, default=0)


class TransactionLog(models.Model):
  
  TRANSACTION_TYPES_CHOICES = [
    ("INCOME", "income"),
    ("OUTCOME", "outcome")
  ]
  transaction_type = models.CharField(choices=TRANSACTION_TYPES_CHOICES, blank=False, null=False, max_length=8)
  amount = models.IntegerField(blank=False, null=False, default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)