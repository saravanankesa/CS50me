from django import forms
from django.contrib.auth.models import User
from .models import Account, Category, Transaction

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter new email',
        'class': 'form-control',
        'autocomplete': 'off'
    }), required=False)

    class Meta:
        model = User
        fields = ['email']
    
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'New Email'
        self.fields['email'].required = False
        self.fields['email'].initial = None  # Clear the initial email field

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_name', 'purpose']
        widgets = {
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'account_name', 'style': 'width: 40%;'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 1})
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'transaction_type']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'account_name'}),
            'transaction_type': forms.Select(choices=Category.TRANSACTION_TYPES, attrs={'class': 'form-control', 'placeholder': 'Select one'})
        }
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].required = True
        self.fields['transaction_type'].widget.attrs['placeholder'] = 'Select one'
        self.fields['transaction_type'].empty_label = "Select one"

class TransactionForm(forms.ModelForm):
    TRANSACTION_TYPES = [
        ('Expense', 'Expense'),
        ('Income', 'Income'),
    ]
    
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES, widget=forms.RadioSelect)

    account_name = forms.ModelChoiceField(
        queryset=Account.objects.none(),  # Initially empty, will be set in the view
        empty_label="Select Account",
        label='Account Name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    class Meta:
        model = Transaction
        fields = ['account_name', 'transaction_name', 'category', 'amount', 'date', 'transaction_type', 'is_pre_auth', 'is_recurring']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'transaction_type': forms.Select(choices=Transaction.TRANSACTION_TYPES),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            initial['account_name'] = instance.account_name
            kwargs['initial'] = initial
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['account_name'].queryset = Account.objects.filter(user=user)
        

