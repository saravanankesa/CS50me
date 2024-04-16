from django import forms
from django.contrib.auth.models import User
from .models import Account, Category  # Ensure you import your Account and Category models

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