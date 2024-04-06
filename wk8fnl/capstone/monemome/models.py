from django.contrib.auth.models import User
from django.db import models

TRANSACTION_TYPES = [
    ('Expense', 'Expense'),
    ('Income', 'Income')
]

class Category(models.Model):
    name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)

    def __str__(self):
        return self.name

class Account(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100, blank=True)  # Allow blank for dynamic input
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, default='Expense')
    category = models.CharField(max_length=100, blank=True)  # Allow blank for dynamic input
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    pre_auth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.category} - ${self.amount}"
