from django import forms
from django.contrib.auth.models import User
from .models import Transaction

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account_name', 'transaction_type', 'category', 'amount', 'date', 'pre_auth_date']
        widgets = {
            'transaction_type': forms.Select(choices=Transaction.TRANSACTION_TYPES),
            'category': forms.Select(),  # We will populate this dynamically based on the transaction type
            'date': forms.DateInput(attrs={'type': 'date'}),
            'pre_auth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        if user:
            # Populate account_name with user's previous account names
            self.fields['account_name'].queryset = Transaction.objects.filter(user=user).values_list('account_name', flat=True).distinct()

            # Hide pre_auth_date initially
            self.fields['pre_auth_date'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("transaction_type")
        category = cleaned_data.get("category")
        pre_auth_date = cleaned_data.get("pre_auth_date")

        # Validate categories based on transaction type
        if transaction_type and category:
            valid_categories = [c[0] for c in Transaction.CATEGORIES[transaction_type]]
            if category not in valid_categories:
                self.add_error('category', "Invalid category for the selected transaction type.")
        
        # Validate pre_auth_date for Pre-Auth Payments category only
        if category != 'Pre-Auth Payments' and pre_auth_date:
            self.add_error('pre_auth_date', "Pre-auth date is only allowed for Pre-Auth Payments category.")
