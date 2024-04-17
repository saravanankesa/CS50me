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
    
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES, widget=forms.RadioSelect(attrs={'onchange': 'updateFormFields();'}))

    account_name = forms.ModelChoiceField(
        queryset=Account.objects.none(),  # Initially empty, will be set in the view
        empty_label="Select Account",
        label='Account Name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    class Meta:
        model = Transaction
        fields = ['transaction_type', 'account_name', 'transaction_name', 'category', 'amount', 'date', 'is_pre_auth', 'is_recurring']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'transaction_type': forms.RadioSelect,
            'is_pre_auth': forms.CheckboxInput(attrs={'class': 'expense-only'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'income-only'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            initial['account_name'] = instance.account_name
            kwargs['initial'] = initial
        self.user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Populate account_name with names from the Account model
        self.fields['account_name'] = forms.ChoiceField(
            choices=[(account.account_name, account.account_name) for account in Account.objects.all()]
        )
        if 'transaction_type' in self.data:
            # If the form is being submitted, update the queryset based on the selected transaction type.
            transaction_type = self.data.get('transaction_type')
            self.fields['category'].queryset = Category.objects.filter(transaction_type=transaction_type)
        elif self.instance.pk:
            # This ensures that during form editing, the current value is valid.
            self.fields['category'].queryset = Category.objects.filter(transaction_type=self.instance.transaction_type)
        elif self.user:
            self.fields['account_name'].queryset = Account.objects.filter(user=self.user)

        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            initial['account_name'] = instance.account_name
            kwargs['initial'] = initial
        self.fields['is_pre_auth'].widget = forms.CheckboxInput(attrs={'class': 'expense-only', 'style': 'display:none;'})
        self.fields['is_recurring'].widget = forms.CheckboxInput(attrs={'class': 'income-only', 'style': 'display:none;'})

    def save(self, commit=True):
        instance = super(TransactionForm, self).save(commit=False)
        if not instance.user_id:  # Only set user if it's not already set
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Needed for saving many-to-many relations
        return instance

    def clean_category(self):
        # Explicitly fetch the category ID to handle cases where the model instance might be passed
        category_id = self.cleaned_data.get('category')
        if isinstance(category_id, Category):
            return category_id
        try:
            # Attempt to get the Category instance by ID
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise forms.ValidationError("This category does not exist.")
        return category

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')

        # Add a check to ensure category is not None before accessing its ID
        if category is None:
            print("Transaction Type:", transaction_type)
            print("Category:", category)
            raise forms.ValidationError("Category is required.")
        
        if not Category.objects.filter(transaction_type=transaction_type, id=category.id).exists():
            raise forms.ValidationError("Select a valid choice. That choice is not one of the available choices.")

        return cleaned_data

