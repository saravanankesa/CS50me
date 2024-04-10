from django.contrib.auth.models import User
from django.db import models

TRANSACTION_TYPES = [
    ('Expense', 'Expense'),
    ('Income', 'Income')
]

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.account_name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Expense', 'Expense'),
        ('Income', 'Income')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100, blank=True)  # Allow blank for dynamic input
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, default='Expense')
    transaction_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)  # Allow blank for dynamic input
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(null="0000-00-00")
    is_pre_auth = models.BooleanField(default=False, verbose_name="Pre-Auth Payment")

    def __str__(self):
        return f"{self.transaction_type}: {self.category} - ${self.amount}"
