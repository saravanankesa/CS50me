from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    purpose = models.TextField(default='')

    def __str__(self):
        return self.name

class Category(models.Model):
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    category_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, blank=False)

    def __str__(self):
        return self.name
