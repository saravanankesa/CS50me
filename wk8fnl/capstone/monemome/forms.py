from django import forms
from django.contrib.auth.models import User
from .models import Transaction, Account, Category

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account_name', 'transaction_type', 'name', 'category', 'amount', 'date', 'pre_auth_date']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        self.fields['transaction_type'].widget = forms.RadioSelect(choices=Transaction.TRANSACTION_TYPES)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['pre_auth_date'].widget = forms.DateInput(attrs={'type': 'date'})

        if self.user:
            # Populate account_name with user's previous account names or allow adding a new one
            account_names = list(Transaction.objects.filter(user=self.user)
                                 .values_list('account_name', flat=True).distinct())
            account_names_choices = [(name, name) for name in account_names]
            account_names_choices.insert(0, ('', '--- Add New ---'))
            self.fields['account_name'].widget = forms.Select(choices=account_names_choices)

            # Populate category based on the transaction type and user's previous categories
            # This will be further handled in JavaScript to dynamically update based on transaction type
            expense_categories = list(Category.objects.filter(user=self.user, transaction_type='Expense')
                                     .values_list('name', flat=True).distinct())
            income_categories = list(Category.objects.filter(user=self.user, transaction_type='Income')
                                    .values_list('name', flat=True).distinct())
            category_choices = [('', '--- Select Category ---')] + \
                               [(cat, cat) for cat in expense_categories + income_categories]
            self.fields['category'].widget = forms.Select(choices=category_choices)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        try:
            amount = float(amount)
        except ValueError:
            raise forms.ValidationError("Amount must be a number.")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return round(amount, 2)

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category.isalnum():
            raise forms.ValidationError("Category name should only contain letters and numbers.")
        # Check for duplicate categories
        if Category.objects.filter(user=self.user, name=category).exists():
            raise forms.ValidationError("This category already exists.")
        return category


    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        pre_auth_date = cleaned_data.get("pre_auth_date")

        # Validate pre_auth_date for Pre-Auth Payments category only
        if category != 'Pre-Auth Payments' and pre_auth_date:
            self.add_error('pre_auth_date', "Pre-auth date is only allowed for Pre-Auth Payments category.")

        if self.user:
            # Populate account_name with user's previous account names or allow adding a new one
            account_names = list(Transaction.objects.filter(user=self.user)
                                 .values_list('account_name', flat=True).distinct())
            account_names_choices = [(name, name) for name in account_names]
            account_names_choices.insert(0, ('', '--- Add New ---'))
            self.fields['account_name'].widget = forms.Select(choices=account_names_choices)

            # Populate category based on the transaction type and user's previous categories
            # This will be further handled in JavaScript to dynamically update based on transaction type
            expense_categories = list(Category.objects.filter(user=self.user, transaction_type='Expense')
                                     .values_list('name', flat=True).distinct())
            income_categories = list(Category.objects.filter(user=self.user, transaction_type='Income')
                                    .values_list('name', flat=True).distinct())
            category_choices = [('', '--- Select Category ---')] + \
                               [(cat, cat) for cat in expense_categories + income_categories]
            self.fields['category'].widget = forms.Select(choices=category_choices)

