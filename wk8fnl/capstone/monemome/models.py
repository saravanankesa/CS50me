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
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    EXPENSE_CATEGORIES = [
        ('Bills', 'Bills'),
        ('Groceries', 'Groceries'),
        ('Rent', 'Rent'),
        # Add more categories...
    ]
    INCOME_CATEGORIES = [
        ('CPP', 'CPP'),
        ('OAS', 'OAS'),
        # Add more categories...
    ]

    CATEGORIES = {
        'Expense': EXPENSE_CATEGORIES,
        'Income': INCOME_CATEGORIES,
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, default='Expense')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    pre_auth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.type}: {self.name} - ${self.amount}"
