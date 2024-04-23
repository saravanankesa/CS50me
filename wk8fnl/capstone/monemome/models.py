from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    purpose = models.TextField(default='')

    def calculate_balance(self):
        # Ensure you prefetch related transactions if calling this method multiple times
        transactions = self.transactions.all()  # Assuming related_name='transactions'
        income = sum(t.amount for t in transactions if t.transaction_type == 'Income')
        expense = sum(t.amount for t in transactions if t.transaction_type == 'Expense')
        return income - expense


    def __str__(self):
        return self.account_name

class Category(models.Model):
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    VALUE_SCORE_CHOICES = [
        (1, '1 - Low'),
        (2, '2'),
        (3, '3 - Medium'),
        (4, '4'),
        (5, '5 - High')
    ]

    category_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, blank=False)
    value_score = models.IntegerField(choices=VALUE_SCORE_CHOICES, default=3, verbose_name="Value Score")

    def __str__(self):
        return self.category_name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_name = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    transaction_type = models.CharField(max_length=10)  # Example: 'Income', 'Expense'
    is_pre_auth = models.BooleanField(default=False, verbose_name="Pre-Authorized Payment")
    is_recurring = models.BooleanField(default=False, verbose_name="Recurring Income")

    def __str__(self):
        return f"{self.date} - {self.category} - {self.amount}"
